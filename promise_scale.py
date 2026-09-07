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

__version__ = "0.1.0"
__all__ = [
    "promise", "Scale", "planted", "check",
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
            registry: list | None = None):
    """Declare one promise and how it is measured.

    key   short stable id (P1, backup, tls...). It is what history is keyed on,
          so changing it starts a new history for that promise.
    title what the system promises, in the words of whoever depends on it —
          not the name of the probe. "photos still arrive", not "check_rsync".
    mode  which run includes it: "fast" (always), or any label you pass to
          run(modes=...) for the slow or expensive ones.
    how   one sentence naming the actual command or file that decides it. This
          is not decoration: a promise whose measurement cannot be named in one
          sentence is usually two promises.

    The decorated function returns (state, detail, remedy):
        state   one of the five above
        detail  what was measured, with the number in it
        remedy  what to do about it — only read when not kept
    """
    reg = _REGISTRY if registry is None else registry

    def wrap(fn):
        reg.append({"key": key, "title": title, "mode": mode, "how": how, "fn": fn})
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
        self.path = Path(path) if path else None

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

    name      what is being weighed, for the header
    version   your system's version, if it has one
    history   path to the JSONL history file (None disables "since when")
    registry  the promises (defaults to everything declared with @promise)
    """

    def __init__(self, name: str = "this system", version: str = "",
                 history: str | Path | None = None,
                 registry: list | None = None,
                 planted_cases: list | None = None):
        self.name = name
        self.version = version
        self.registry = _REGISTRY if registry is None else registry
        self.planted_cases = _PLANTED if planted_cases is None else planted_cases
        self.history = History(history)

    # -- measuring ----------------------------------------------------------
    def weigh(self, modes=("fast",)) -> list[dict]:
        """Measure every promise whose mode is included. Never raises."""
        wanted = set(modes)
        past = self.history.read()
        now = datetime.now()
        readings = []
        for p in self.registry:
            t0 = time.time()
            if p["mode"] not in wanted:
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
                    # an answer. Say what came back, so the typo is findable.
                    state, detail, remedy = (
                        UNMEASURABLE,
                        "the probe returned %r, which is not one of the five "
                        "states — so the promise was not measured" % (state,), "")
            r = {"key": p["key"], "title": p["title"], "how": p["how"],
                 "mode": p["mode"], "state": state, "detail": detail,
                 "remedy": remedy, "ms": int((time.time() - t0) * 1000)}
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
    def report(self, readings: list[dict], v: dict, modes, out=None) -> None:
        out = out or sys.stdout
        head = _paint(self.name, _BOLD)
        if self.version:
            head += "  " + _paint(self.version, _DIM)
        print("\n  %s  %s\n" % (head, _paint("(%s)" % ", ".join(modes), _DIM)), file=out)
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
        for p in self.registry:
            rows.append("| %s | **%s** | %s | %s |"
                        % (p["key"], p["title"], p["how"] or "—", p["mode"]))
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
        ap.add_argument("--no-history", action="store_true",
                        help="do not append this run to the history file")
        a = ap.parse_args(argv)

        if a.test:
            return 1 if run_planted(self.planted_cases,
                                    registry=self.registry) else 0
        if a.promises:
            print(self.table())
            return 0

        modes = (tuple(sorted({p["mode"] for p in self.registry})) if a.all
                 else tuple(a.mode or ["fast"]))
        readings = self.weigh(modes)
        v = self.verdict(readings)
        if not a.no_history:
            self.history.append(readings, "+".join(modes))

        if a.json:
            print(json.dumps({"name": self.name, "version": self.version,
                              "at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "modes": list(modes), "promises": readings,
                              "verdict": v}, ensure_ascii=False, indent=1))
        elif a.brief:
            print(self.one_line(v))
        else:
            self.report(readings, v, modes)
        return v["exit_code"]


def main(argv=None) -> int:      # `python -m promise_scale` on its own says how
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
