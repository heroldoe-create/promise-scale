"""promise-scale — make your agent system state what it promises, and weigh it.

    A dashboard that is all green because nobody is looking is worse than a red one.

This is a single file with no dependencies. You declare what your system promises,
and how each promise is measured. Then you weigh it.

    from promise_scale import promise, Scale, CUMPLE, NO_CUMPLE, UNMEASURABLE

    @promise("P1", "The backup actually contains new photos")
    def _():
        n = photos_added_last_24h()          # your measurement, whatever it is
        if n is None:
            return UNMEASURABLE, "the log is unreadable", "check the mount"
        if n == 0:
            return NO_CUMPLE, "0 photos in 24h", "run the backup by hand"
        return CUMPLE, "%d photos arrived" % n, ""

    Scale().run()

THE ONE RULE THAT MAKES THIS DIFFERENT
--------------------------------------
UNMEASURABLE never counts as green.

Every health check answers "is it OK?" — this one also answers "could I even
tell?", and refuses to round that up. A probe that fails silently reads as
"not applicable" on a dashboard, which reads as fine. It isn't.

That distinction is not theoretical. It came from a home server where four
containers were healthy, the page returned 200, the logs were clean — and the
phone backup had not uploaded a single photo in twenty hours. Everything being
watched was fine. Nobody was watching whether photos arrived.

And its sibling: a logo sat on a dark toolbar painting dark ink, invisible. The
test was green because it asked "did the image load?" — an image loads fine when
it paints dark-on-dark. Ask for contrast, not for existence.

WHAT IT GIVES YOU
-----------------
  * five states, and the difference between the last two is the point:
      CUMPLE      kept
      AVISO       warning
      NO_CUMPLE   broken
      UNMEASURABLE  we tried to measure and could not  -> never green
      UNMEASURED    we chose not to measure it in this mode (too slow/costly)
  * "since when": each run appends one line to a history file, so a promise can
    say it has been broken for 3 days instead of just "broken".
  * planted failures: `--test` breaks each promise on purpose and demands the
    scale SEE it. A scale nobody has seen fail is not a scale.
  * the scale weighs itself: Scale(expect_every="24h") adds one promise that is
    always measured — that the scale has actually been running. Delete the cron
    entry and it says so, UNMEASURABLE, instead of saying nothing at all.
  * where a reading came from: @promise(..., source="the sentinel's report")
    marks a reading this scale did not take, and `--own` drops them, so no
    layer certifies its own earlier word with the face of a fresh measurement.
  * carried readings: Scale(carry="last-full.json") lets the expensive run
    leave its readings for the fast one, which shows them WITH their age and
    drops them to UNMEASURABLE once they go stale.
  * exit codes for cron and CI: 0 kept · 1 broken · 2 warnings · 3 unmeasurable.

Written by Heroldo Escobedo. MIT.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

__version__ = "0.2.0"
__all__ = [
    "promise", "Scale", "planted", "check", "judge_last_run",
    "CUMPLE", "AVISO", "NO_CUMPLE", "UNMEASURABLE", "UNMEASURED",
    "KEPT", "WARN", "BROKEN",
]

# ── the five states ─────────────────────────────────────────────────────────
# Spanish names kept as the canonical values because that is what the running
# system that produced this speaks, and renaming them later would silently
# break anyone's stored history. English aliases below for readability.
CUMPLE = "kept"
AVISO = "warning"
NO_CUMPLE = "broken"
UNMEASURABLE = "unmeasurable"   # we tried and could not — NEVER green
UNMEASURED = "unmeasured"       # we chose not to, in this mode — not a failure

KEPT, WARN, BROKEN = CUMPLE, AVISO, NO_CUMPLE

# The five, and nothing else. A probe that returns anything outside this set —
# a typo like "KEPT", a bare True, an object— has answered something the scale
# cannot read, which is the same thing as not having answered. It is folded into
# UNMEASURABLE rather than passed through, because passed through it counted as
# "measured, and not one of the failures" and the run exited 0. That is the exact
# shape this whole file exists to refuse: a probe that could not tell, wearing
# the colour of a probe that said fine.
_STATES = (CUMPLE, AVISO, NO_CUMPLE, UNMEASURABLE, UNMEASURED)

_COLOR = {
    CUMPLE: "\033[38;5;77m",
    AVISO: "\033[38;5;220m",
    NO_CUMPLE: "\033[38;5;203m",
    UNMEASURABLE: "\033[38;5;140m",
    UNMEASURED: "\033[2m",
}
_OFF, _DIM, _BOLD = "\033[0m", "\033[2m", "\033[1m"


def _tty() -> bool:
    """Colour only on a real terminal, and never when NO_COLOR is set.

    Redirected output —cron, a log file, a CI job— must be plain text. The
    first version leaked escape codes into files because the reset was written
    directly instead of going through here.
    """
    return sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def _paint(text: str, code: str) -> str:
    return (code + text + _OFF) if (_tty() and text) else text


def _dot(state: str) -> str:
    return _paint("●", _COLOR.get(state, ""))


# ── declaring a promise ─────────────────────────────────────────────────────
_REGISTRY: list[dict] = []


def promise(key: str, title: str, *, mode: str = "fast", how: str = "",
            source: str = "", registry: list | None = None):
    """Declare one promise and how it is measured.

    key    short stable id (P1, backup, tls...). It is what history is keyed on,
           so changing it starts a new history for that promise.
    title  what the system promises, in the words of whoever depends on it —
           not the name of the probe. "photos still arrive", not "check_rsync".
    mode   which run includes it: "fast" (always), or any label you pass to
           run(modes=...) for the slow or expensive ones.
    how    one sentence naming the actual command or file that decides it. This
           is not decoration: a promise whose measurement cannot be named in one
           sentence is usually two promises.
    source name the OTHER layer this reading comes from, when it is not measured
           here — "the sentinel's report", "the nightly job's json". Leave it
           empty for anything this scale measures itself.

           This is the mechanism behind "don't let one layer certify another
           layer's reading". A borrowed reading is carried everywhere the scale
           reports it (`--json` and the printed report both name the source),
           and `--own` drops every borrowed reading, so the layer that produced
           the report can run the scale without certifying itself with a
           reading of its own, wearing the face of a fresh measurement.

    The decorated function returns (state, detail, remedy):
        state   one of the five above
        detail  what was measured, with the number in it
        remedy  what to do about it — only read when not kept
    """
    reg = _REGISTRY if registry is None else registry

    def wrap(fn):
        reg.append({"key": key, "title": title, "mode": mode, "how": how,
                    "source": source, "fn": fn})
        return fn
    return wrap


def check(state, detail: str = "", remedy: str = ""):
    """Small helper so a probe can `return check(CUMPLE, "...")`."""
    return state, detail, remedy


# ── history: "since when has it been like this" ─────────────────────────────
class History:
    """One JSON line per run. Small on purpose: date, mode, state per key.

    Without this, a scale can say "broken" but not "broken since Tuesday", and
    every rule you write about age ("warn if it has been failing for 48h") is a
    rule nobody can actually apply.
    """

    def __init__(self, path: Path | str | None):
        # expanduser, so a "~/..." path lands in the home directory instead of
        # quietly creating a directory literally called "~" next to the script.
        self.path = Path(path).expanduser() if path else None

    def append(self, readings: list[dict], mode: str) -> None:
        if not self.path:
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            line = json.dumps({
                "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "mode": mode,
                "states": {r["key"]: r["state"] for r in readings
                           if r["state"] != UNMEASURED},
            }, ensure_ascii=False)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass          # history is a comfort, never a reason to fail a run

    def read(self, tail: int = 2000) -> list[dict]:
        if not self.path or not self.path.is_file():
            return []
        out = []
        try:
            for raw in self.path.read_text(encoding="utf-8",
                                           errors="replace").splitlines()[-tail:]:
                try:
                    out.append(json.loads(raw))
                except ValueError:
                    continue
        except OSError:
            return []
        return out


def since_when(key: str, state: str, history: list[dict],
               now: datetime | None = None) -> datetime | None:
    """When did this promise first enter the state it is in now?

    Runs that did not measure this key are skipped, not treated as a change —
    otherwise a promise measured only on Sundays would look like it changes
    every day.
    """
    now = now or datetime.now()
    start = None
    for run in reversed(history):
        was = (run.get("states") or {}).get(key)
        if was is None:
            continue
        if was != state:
            break
        try:
            start = datetime.strptime(run["at"], "%Y-%m-%d %H:%M")
        except (KeyError, ValueError):
            break
    return start


def _age(hours: float | None) -> str:
    if hours is None:
        return "?"
    if hours < 1:
        return "%d min" % int(hours * 60)
    if hours < 48:
        return "%.0f h" % hours
    return "%.0f days" % (hours / 24)


def _hours(value) -> float | None:
    """"24h" -> 24.0. Also 30m, 90s, 7d, or a timedelta. None if unreadable.

    Unreadable on purpose returns None instead of raising: a scale that dies
    over its own configuration is a scale that says nothing at 4 a.m., and
    saying nothing is the failure this whole file is about. The None travels
    to a judgement that reports UNMEASURABLE and names the value it could not
    read, so the misconfiguration is loud in the report itself.
    """
    if value is None:
        return None
    if isinstance(value, timedelta):
        n = value.total_seconds() / 3600.0
        return n if n > 0 else None
    try:
        text = str(value).strip().lower()
        n = float(text[:-1]) * {"s": 1 / 3600.0, "m": 1 / 60.0,
                                "h": 1.0, "d": 24.0}[text[-1]]
    except (IndexError, KeyError, ValueError):
        return None
    return n if n > 0 else None


# ── has the scale itself been running? ──────────────────────────────────────
# The gap this file spent a version denouncing one floor down: a scale that
# never ran and a scale with nothing to report look identical from the outside.
# Delete the cron entry, fill the disk, move python3 — nothing here noticed.
# The history file already carried the timestamps; nobody read them for this.

# The mode of the implicit promise below. It is not a mode you can ask for: it
# runs in every run, because a watchdog you can leave out of the fast run is a
# watchdog that is off exactly when the fast run is all that is left.
_ALWAYS = "always"


def last_run_at(history: list[dict]) -> datetime | None:
    """When did this scale last finish a run? None if nothing is on record."""
    for run in reversed(history):
        try:
            return datetime.strptime(run["at"], "%Y-%m-%d %H:%M")
        except (KeyError, TypeError, ValueError):
            continue
    return None


def _late_after(every_hours: float) -> float:
    """When a run counts as missing: the cadence plus a tenth of it (at least a
    minute), so ordinary cron jitter does not make the scale cry wolf about
    itself. A daily scale is late at 26.4 h — near enough the 26 h the running
    system this came from settled on for its 04:10 cron.
    """
    return every_hours + max(every_hours * 0.1, 1 / 60.0)


def judge_last_run(hours_since: float | None, every_hours: float | None,
                   note: str = ""):
    """Pure judgement: numbers in, verdict out — so it can be planted.

    hours_since  hours since the last run on record, or None if there is none
    every_hours  how often it is meant to run, or None if that could not be read
    note         why the reading is missing, when something upstream knows

    A late scale is UNMEASURABLE, never BROKEN, and that is the whole point:
    you have not learned that the system is bad, you have learned that you
    stopped looking. That is exactly the state this project already has.
    """
    fix = "check whatever is supposed to run this (cron, timer, CI) and the history file"
    if every_hours is None:
        return (UNMEASURABLE,
                note or "cannot read how often this scale is supposed to run",
                "pass expect_every='24h' to Scale() — s, m, h or d")
    every = _age(every_hours)
    if hours_since is None:
        return (UNMEASURABLE,
                note or ("nothing on record says this scale has ever run "
                         "(it is set to run every %s)" % every), fix)
    if hours_since > _late_after(every_hours):
        return (UNMEASURABLE,
                "last run %s ago, and it is set to run every %s"
                % (_age(hours_since), every), fix)
    return CUMPLE, "last run %s ago (every %s)" % (_age(hours_since), every), ""


# ── carried readings: the expensive ones, kept with their age ───────────────
class Carry:
    """Readings from the expensive run, stored with the hour they were taken.

    The fast run cannot afford the three-minute promise, and calling it
    `unmeasured` every day leaves the daily report incomplete by design. So the
    full run leaves its readings here and the fast run carries them forward —
    but only while they are fresh, and never without saying how old they are.

    A stored reading shown without its age is a stale reading wearing the face
    of a fresh one, which is the same failure as a silent probe. Past the limit
    it becomes UNMEASURABLE, not UNMEASURED: once you have asked for carried
    readings, not having one is not a choice you made in this run.
    """

    def __init__(self, path: Path | str | None, max_age="26h"):
        self.path = Path(path).expanduser() if path else None
        self.max_hours = _hours(max_age)
        self.max_age = max_age

    def read(self) -> dict:
        if not self.path or not self.path.is_file():
            return {}
        try:
            stored = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}
        return stored if isinstance(stored, dict) else {}

    def write(self, readings: list[dict], modes) -> None:
        """Store only what a run that INCLUDED that mode actually measured.

        `modes` is what this run asked for, and it is the whole guard. Found on
        2026-09-07 by running the example twice on a clean machine: the first
        run stored its own "there is no stored reading yet" line — an
        UNMEASURABLE about the absence of a reading — and the second run
        carried it forward as though it were one. A note saying "I could not
        measure this" is not a measurement, and the moment it is filed as one
        the whole mechanism turns into the stale green it exists to prevent.

        A carried reading is never written back either. Writing it back would
        stamp it with today's hour, and a reading whose clock restarts every
        fifteen minutes never grows old and never expires — a permanent green
        built out of one measurement taken once. Same rule as history: a file
        that cannot be written is a comfort lost, never a reason to fail a run.
        """
        if not self.path:
            return
        wanted = set(modes)
        fresh = {r["key"]: {"at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "mode": r.get("mode", ""), "state": r["state"],
                            "detail": r.get("detail", ""),
                            "remedy": r.get("remedy", "")}
                 for r in readings
                 if r.get("mode") in wanted and r["state"] != UNMEASURED
                 and not r.get("carried")}
        if not fresh:
            return
        try:
            stored = self.read()
            stored.update(fresh)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(stored, ensure_ascii=False, indent=1),
                                 encoding="utf-8")
        except OSError:
            pass

    def carried(self, key: str, now: datetime | None = None):
        """(reading, hours_old) for a stored reading, or (None, hours_old)."""
        entry = self.read().get(key)
        if not isinstance(entry, dict):
            return None, None
        try:
            taken = datetime.strptime(entry["at"], "%Y-%m-%d %H:%M")
        except (KeyError, TypeError, ValueError):
            return None, None
        old = ((now or datetime.now()) - taken).total_seconds() / 3600.0
        if self.max_hours is None or old > self.max_hours:
            return None, old
        return entry, old


# ── planted failures ────────────────────────────────────────────────────────
_PLANTED: list[dict] = []


def planted(name: str, expect, *, key: str = "", registry: list | None = None):
    """Break a promise on purpose and demand the scale sees it.

    A scale that has never been seen failing is not a scale — it is a green
    light with no wiring behind it. `--test` runs these.

    The decorated function returns whatever your judgement function returns
    (usually a (state, detail, remedy) tuple, or the state alone); `expect` is
    the state it MUST report.

        @planted("backup 30h old -> broken", NO_CUMPLE, key="P2")
        def _():
            return judge_backup(hours_old=30)

    key   optional: the promise this case belongs to. Give it, and `--test`
          also names the promises that have NO planted case — which is the rule
          this project asks of you ("a new promise arrives with its planted case,
          or it does not arrive") finally applied to itself instead of only
          written down. It is a report, never a failure: it does not change the
          missed count or the exit code, so adding keys cannot redden anyone's
          CI. The coverage line only appears once at least one case declares a
          key, so a suite that never opts in sees no change at all.

    Keep the judgement separate from the reading — a function that both reads
    the disk and decides cannot be planted, only mocked.
    """
    reg = _PLANTED if registry is None else registry

    def wrap(fn):
        reg.append({"name": name, "expect": expect, "key": key, "fn": fn})
        return fn
    return wrap


def _coverage(cases: list[dict], registry: list | None, out) -> list[str]:
    """Which promises have no planted case? Reported, never enforced.

    Silent until at least one case declares a `key`: a suite that has not opted
    in gets no new line, and one that has gets the list it asked for.
    """
    covered = {c.get("key") for c in cases if c.get("key")}
    if not covered or registry is None:
        return []
    naked = [p["key"] for p in registry if p["key"] not in covered]
    if naked:
        print("  " + _paint(
            "%d promise(s) with no planted case: %s — nobody has ever seen "
            "these fail" % (len(naked), ", ".join(naked)), _COLOR[AVISO]), file=out)
    else:
        print("  " + _paint("every promise has a planted case", _DIM), file=out)
    return naked


def run_planted(cases: list[dict] | None = None, out=None,
                registry: list | None = None) -> int:
    """Run the planted failures. Returns the number that the scale did NOT see.

    `registry`, if given, is the promise list: any promise with no planted case
    naming its key is reported at the end. That report never changes the return
    value — an uncovered promise is a gap in your suite, not a scale that failed
    to see something, and the two deserve different words.
    """
    cases = _PLANTED if cases is None else cases
    out = out or sys.stdout
    missed = 0
    print("\n  %s  %s" % (_paint("PLANTED FAILURES", _BOLD),
                          _paint("(does the scale actually see them?)", _DIM)), file=out)
    if not cases:
        print("  " + _paint("none declared — an unproven scale is a green light "
                            "with no wiring behind it", _COLOR[AVISO]), file=out)
        return 0
    for c in cases:
        try:
            got = c["fn"]()
        except Exception as e:                       # a crash is also a miss
            got = ("crashed: %s" % e, "", "")
        state = got[0] if isinstance(got, (tuple, list)) else got
        detail = got[1] if isinstance(got, (tuple, list)) and len(got) > 1 else ""
        ok = state == c["expect"]
        if not ok:
            missed += 1
        print("  %s %-58s expected %-13s got %s"
              % (_paint("ok  " if ok else "MISS", _COLOR[CUMPLE if ok else NO_CUMPLE]),
                 c["name"][:58], c["expect"], state), file=out)
        if not ok and detail:
            print("       " + _paint(str(detail)[:120], _DIM), file=out)
    print("\n  [planted] cases=%d missed=%d" % (len(cases), missed), file=out)
    _coverage(cases, registry, out)
    if missed:
        print("  " + _paint("The scale did not see %d failure(s) it was shown. "
                            "Fix the scale, not the case." % missed,
                            _COLOR[NO_CUMPLE]), file=out)
    return missed


# ── the scale ───────────────────────────────────────────────────────────────
class Scale:
    """Weighs the promises and reports.

    name         what is being weighed, for the header
    version      your system's version, if it has one
    history      path to the JSONL history file (None disables "since when")
    registry     the promises (defaults to everything declared with @promise)
    expect_every how often this scale is supposed to run — "24h", "15m", a
                 timedelta. Set it and the scale weighs one more promise, always:
                 that it has actually been running. Left unset, nothing changes
                 and the scale still cannot tell whether it ran.
    self_key     the key that implicit promise is stored under (default "scale").
                 It shares the history file with yours, so change it only if you
                 already have a promise by that name.
    carry        path to a json file where the expensive readings are left, so a
                 fast run can carry them forward with their age shown
    carry_max_age how old a carried reading may be before it stops counting as a
                 reading at all (default "26h": a daily job plus slack)
    """

    def __init__(self, name: str = "this system", version: str = "",
                 history: str | Path | None = None,
                 registry: list | None = None,
                 planted_cases: list | None = None,
                 expect_every=None, self_key: str = "scale",
                 carry: str | Path | None = None, carry_max_age="26h"):
        self.name = name
        self.version = version
        self.registry = _REGISTRY if registry is None else registry
        self.planted_cases = _PLANTED if planted_cases is None else planted_cases
        self.history = History(history)
        self.expect_every = expect_every
        self.self_key = self_key
        self.carry = Carry(carry, carry_max_age)

    # -- the promises, including the one about the scale itself -------------
    def promises(self) -> list[dict]:
        """Your promises, plus the implicit one when expect_every is set.

        It goes through the same list as the rest on purpose: that way it shows
        up in `--promises`, and `--test` counts it when it names the promises
        nobody has ever seen fail. A watchdog exempt from the project's own
        rules would be the joke this project is about.
        """
        if self.expect_every is None:
            return list(self.registry)
        return [{
            "key": self.self_key, "mode": _ALWAYS, "source": "", "fn": None,
            "title": "This scale has actually been running",
            "how": "the time of the last run in the history file, against "
                   "expect_every=%r" % (self.expect_every,)}] + list(self.registry)

    def _weigh_self(self, past: list[dict], now: datetime):
        """The reading of the implicit promise. Wiring problems are loud here."""
        if self.history.path is None:
            return (UNMEASURABLE,
                    "there is no history file, so nothing anywhere records "
                    "whether this scale ran", "give Scale(history=...) a path")
        if any(p["key"] == self.self_key for p in self.registry):
            return (UNMEASURABLE,
                    "one of your promises already uses the key %r, so this one "
                    "cannot be told apart from it in the history"
                    % self.self_key, "pass self_key= to Scale()")
        every = _hours(self.expect_every)
        last = last_run_at(past)
        since = (now - last).total_seconds() / 3600.0 if last else None
        return judge_last_run(since, every,
                              "" if every is not None else
                              "expect_every=%r cannot be read as a duration"
                              % (self.expect_every,))

    # -- measuring ----------------------------------------------------------
    def weigh(self, modes=("fast",), own: bool = False) -> list[dict]:
        """Measure every promise whose mode is included. Never raises.

        own   drop every promise that declares a `source`: the readings this
              scale did not take itself. For the layer that WROTE that source —
              running the full scale there would have it certify its own earlier
              reading with the face of a fresh measurement.
        """
        wanted = set(modes)
        past = self.history.read()
        now = datetime.now()
        readings = []
        for p in self.promises():
            t0 = time.time()
            carried_at, carried_hours = "", None
            if p["fn"] is None:                       # the scale weighing itself
                state, detail, remedy = self._weigh_self(past, now)
            elif own and p.get("source"):
                state, detail, remedy = (
                    UNMEASURED,
                    "read from %s, and --own does not take another layer's "
                    "word for it" % p["source"], "")
            elif p["mode"] not in wanted:
                stored, old = self.carry.carried(p["key"], now)
                if stored:
                    # The age is welded to the text, not offered next to it:
                    # there is no way to print this reading without saying when
                    # it was taken.
                    state = stored.get("state", UNMEASURABLE)
                    detail = "%s — carried from the %s run %s ago" % (
                        stored.get("detail", "").strip() or "measured",
                        stored.get("mode", "full"), _age(old))
                    remedy = stored.get("remedy", "")
                    carried_at, carried_hours = stored.get("at", ""), old
                elif self.carry.path:
                    state, detail, remedy = (
                        UNMEASURABLE,
                        "not measured in this run (mode: %s), and the stored "
                        "reading is %s" % (p["mode"], "%s old (limit %s)"
                                           % (_age(old), self.carry.max_age)
                                           if old is not None else "missing"),
                        "run it in full once: --all")
                else:
                    state, detail, remedy = (
                        UNMEASURED,
                        "not measured in this run (mode: %s)" % p["mode"], "")
            else:
                try:
                    got = p["fn"]()
                    if isinstance(got, (tuple, list)):
                        state = got[0]
                        detail = got[1] if len(got) > 1 else ""
                        remedy = got[2] if len(got) > 2 else ""
                    else:
                        state, detail, remedy = got, "", ""
                except Exception as e:
                    # A probe that crashes is UNMEASURABLE, not broken and not
                    # fine: we learned nothing about the promise itself.
                    state, detail, remedy = (
                        UNMEASURABLE, "the probe crashed: %s" % e, "")
            if state not in _STATES:
                # Same reasoning as a crash: an answer we cannot read is not
                # an answer. Say what came back, so the typo is findable. This
                # sits outside the branch above because a carried reading comes
                # out of a file anyone can edit or truncate, and a rule that
                # only holds on the path you were thinking about is not a rule.
                state, detail, remedy = (
                    UNMEASURABLE,
                    "the reading came back as %r, which is not one of the five "
                    "states — so the promise was not measured" % (state,), "")
            r = {"key": p["key"], "title": p["title"], "how": p["how"],
                 "mode": p["mode"], "state": state, "detail": detail,
                 "remedy": remedy, "source": p.get("source", ""),
                 "ms": int((time.time() - t0) * 1000)}
            if carried_hours is not None:
                r["carried"] = True
                r["carried_at"] = carried_at
                r["carried_hours"] = round(carried_hours, 1)
            if state != UNMEASURED:
                start = since_when(p["key"], state, past, now)
                r["since"] = start.strftime("%Y-%m-%d %H:%M") if start else ""
                r["hours_like_this"] = (
                    round((now - start).total_seconds() / 3600, 1) if start else 0.0)
            readings.append(r)
        return readings

    # -- judging ------------------------------------------------------------
    @staticmethod
    def verdict(readings: list[dict]) -> dict:
        measured = [r for r in readings if r["state"] != UNMEASURED]
        broken = [r["key"] for r in measured if r["state"] == NO_CUMPLE]
        warned = [r["key"] for r in measured if r["state"] == AVISO]
        # An unreadable state lands here too, and for the same reason: `weigh`
        # already folds it in, but `verdict` is a staticmethod anyone can call
        # with readings the scale did not produce, and the rule has to hold
        # there as well or it holds only where it is convenient.
        blind = [r["key"] for r in measured
                 if r["state"] == UNMEASURABLE or r["state"] not in _STATES]
        skipped = [r["key"] for r in readings if r["state"] == UNMEASURED]
        kept = len([r for r in measured if r["state"] == CUMPLE])
        # THE ORDER IS THE POINT: unmeasurable outranks warnings. Not knowing is
        # worse than a known small problem, because nobody investigates a shrug.
        code = 1 if broken else (3 if blind else (2 if warned else 0))
        return {"kept": kept, "measured": len(measured), "broken": broken,
                "warnings": warned, "unmeasurable": blind, "unmeasured": skipped,
                "exit_code": code}

    # -- reporting ----------------------------------------------------------
    def report(self, readings: list[dict], v: dict, modes, out=None,
               own: bool = False) -> None:
        out = out or sys.stdout
        head = _paint(self.name, _BOLD)
        if self.version:
            head += "  " + _paint(self.version, _DIM)
        modes_said = ", ".join(modes) + (", own readings only" if own else "")
        print("\n  %s  %s\n" % (head, _paint("(%s)" % modes_said, _DIM)), file=out)
        for r in readings:
            # .get, not [ ]: a reading handed in from outside can carry a state
            # the palette does not know, and the report going down with a
            # KeyError is the loudest possible way to tell you nothing.
            print("  %-5s %s %s %s" % (r["key"], _dot(r["state"]),
                                       _paint("%-13s" % str(r["state"]).upper(),
                                              _COLOR.get(r["state"], "")),
                                       r["title"]), file=out)
            if r["detail"]:
                print("        %s" % _paint(r["detail"], _DIM), file=out)
            # Where a reading came from travels with it. A borrowed reading that
            # prints like a measured one is how a layer ends up certifying its
            # own earlier word without anybody deciding to let it.
            if r.get("source") and r["state"] != UNMEASURED:
                print("        %s" % _paint(
                    "read from %s — this scale did not measure it" % r["source"],
                    _DIM), file=out)
            if r.get("hours_like_this", 0) >= 1 and r["state"] != CUMPLE:
                print("        %s" % _paint(
                    "like this for %s (since %s)"
                    % (_age(r["hours_like_this"]), r.get("since", "")), _DIM), file=out)
            if r["remedy"] and r["state"] in (NO_CUMPLE, AVISO, UNMEASURABLE):
                print("        %s %s" % (_paint("to fix:", _DIM), r["remedy"]), file=out)
        print(file=out)
        if v["broken"]:
            linea = "%d of %d promises BROKEN: %s" % (
                len(v["broken"]), v["measured"], ", ".join(v["broken"]))
            print("  " + _paint(linea, _COLOR[NO_CUMPLE]), file=out)
        elif v["unmeasurable"]:
            linea = ("%d kept, and %d could not be measured — that is NOT green: %s"
                     % (v["kept"], len(v["unmeasurable"]),
                        ", ".join(v["unmeasurable"])))
            print("  " + _paint(linea, _COLOR[UNMEASURABLE]), file=out)
        elif v["warnings"]:
            linea = "%d of %d kept, %d with a warning: %s" % (
                v["kept"], v["measured"], len(v["warnings"]), ", ".join(v["warnings"]))
            print("  " + _paint(linea, _COLOR[AVISO]), file=out)
        else:
            print("  " + _paint("All %d measured promises are kept." % v["measured"],
                                _COLOR[CUMPLE]), file=out)
        if v["unmeasured"]:
            print("  " + _paint("%d not measured in this run (%s)."
                                % (len(v["unmeasured"]), " ".join(v["unmeasured"])),
                                _DIM), file=out)
        print(file=out)

    @staticmethod
    def one_line(v: dict) -> str:
        bits = ["kept %d/%d" % (v["kept"], v["measured"])]
        if v["broken"]:
            bits.insert(0, "BROKEN " + " ".join(v["broken"]))
        if v["warnings"]:
            bits.append("warning " + " ".join(v["warnings"]))
        if v["unmeasurable"]:
            bits.append("could not measure " + " ".join(v["unmeasurable"]))
        return " · ".join(bits)

    def table(self) -> str:
        """The promises as markdown — so the doc and the code cannot drift."""
        rows = ["# What %s promises" % self.name, "",
                "> Generated by promise-scale. Do not edit by hand: edit the "
                "`@promise` declarations and regenerate.", "",
                "| # | Promise | How it is measured | Run |",
                "|---|---|---|---|"]
        for p in self.promises():
            how = p["how"] or "—"
            if p.get("source"):
                how += " — **read from %s**, not measured here" % p["source"]
            rows.append("| %s | **%s** | %s | %s |"
                        % (p["key"], p["title"], how, p["mode"]))
        rows += ["", "States: kept · warning · broken · **unmeasurable** (tried "
                 "and could not — never counts as green) · unmeasured (skipped "
                 "in that run).",
                 "Exit codes: 0 kept · 1 broken · 2 warnings · 3 unmeasurable.", ""]
        return "\n".join(rows)

    # -- entry point --------------------------------------------------------
    def run(self, argv=None) -> int:
        ap = argparse.ArgumentParser(
            prog="scale", description="Weigh what this system promises.")
        ap.add_argument("--mode", action="append", default=None,
                        help="which promises to run (default: fast). Repeatable.")
        ap.add_argument("--all", action="store_true", help="every mode declared")
        ap.add_argument("--json", action="store_true", help="machine readable")
        ap.add_argument("--brief", action="store_true", help="one line, for cron")
        ap.add_argument("--promises", action="store_true",
                        help="print the promise table as markdown")
        ap.add_argument("--test", action="store_true",
                        help="run the planted failures and exit")
        ap.add_argument("--own", action="store_true",
                        help="only what this scale measures itself — skip every "
                             "promise read from another layer's report")
        ap.add_argument("--no-history", action="store_true",
                        help="do not record this run (history or carried readings)")
        a = ap.parse_args(argv)

        if a.test:
            return 1 if run_planted(self.planted_cases,
                                    registry=self.promises()) else 0
        if a.promises:
            print(self.table())
            return 0

        modes = (tuple(sorted({p["mode"] for p in self.registry})) if a.all
                 else tuple(a.mode or ["fast"]))
        readings = self.weigh(modes, own=a.own)
        v = self.verdict(readings)
        if not a.no_history:
            self.history.append(readings, "+".join(modes))
            self.carry.write(readings, modes)

        if a.json:
            print(json.dumps({"name": self.name, "version": self.version,
                              "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "modes": list(modes), "own": a.own,
                              "promises": readings, "verdict": v},
                             ensure_ascii=False, indent=1))
        elif a.brief:
            print(self.one_line(v))
        else:
            self.report(readings, v, modes, own=a.own)
        return v["exit_code"]


def main(argv=None) -> int:      # `python -m promise_scale` on its own says how
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
