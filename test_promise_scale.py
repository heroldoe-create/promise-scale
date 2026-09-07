#!/usr/bin/env python3
"""The scale's own planted failures — it is measured by its own rule.

    python3 test_promise_scale.py

No test framework: one file, no dependencies, same as the library. If the scale
cannot be shown its own failures, it has no business asking you to plant yours.
"""

import sys
from datetime import datetime, timedelta

from promise_scale import (
    AVISO, CUMPLE, NO_CUMPLE, UNMEASURABLE, UNMEASURED,
    History, Scale, promise, run_planted, since_when,
)

fallas = 0


def caso(nombre, esperado, obtenido):
    global fallas
    ok = obtenido == esperado
    if not ok:
        fallas += 1
    print("  %-5s %-62s expected %-14r got %r"
          % ("ok" if ok else "MISS", nombre, esperado, obtenido))


print("\n  THE SCALE, WEIGHED BY ITS OWN RULE\n")

# ── the rule itself: unmeasurable is never green ────────────────────────────
v = Scale.verdict([{"key": "a", "state": UNMEASURABLE}, {"key": "b", "state": CUMPLE}])
caso("one unmeasurable -> exit 3, not 0", 3, v["exit_code"])

v = Scale.verdict([{"key": "a", "state": UNMEASURABLE}, {"key": "b", "state": AVISO}])
caso("unmeasurable OUTRANKS a warning (3, not 2)", 3, v["exit_code"])

v = Scale.verdict([{"key": "a", "state": UNMEASURABLE}, {"key": "b", "state": NO_CUMPLE}])
caso("broken still outranks unmeasurable (1)", 1, v["exit_code"])

v = Scale.verdict([{"key": "a", "state": UNMEASURED}, {"key": "b", "state": CUMPLE}])
caso("unmeasured (a choice) is NOT a failure -> 0", 0, v["exit_code"])

v = Scale.verdict([{"key": "a", "state": UNMEASURED}, {"key": "b", "state": CUMPLE}])
caso("unmeasured does not count as measured", 1, v["measured"])

v = Scale.verdict([{"key": "a", "state": AVISO}, {"key": "b", "state": CUMPLE}])
caso("only a warning -> exit 2", 2, v["exit_code"])

v = Scale.verdict([{"key": "a", "state": CUMPLE}])
caso("all kept -> exit 0", 0, v["exit_code"])

# ── a probe that crashes must be unmeasurable, not fine and not broken ──────
reg = []


@promise("X", "a promise whose probe explodes", registry=reg)
def _():
    raise RuntimeError("boom")


r = Scale(registry=reg, planted_cases=[]).weigh()[0]
caso("a crashing probe -> unmeasurable, not broken and not fine",
     UNMEASURABLE, r["state"])
caso("and it says why", True, "boom" in r["detail"])

# ── a probe may return the state alone ──────────────────────────────────────
reg2 = []


@promise("Y", "returns the bare state", registry=reg2)
def _():
    return CUMPLE


caso("a bare state is accepted", CUMPLE, Scale(registry=reg2, planted_cases=[]).weigh()[0]["state"])

# ── since when ──────────────────────────────────────────────────────────────
ahora = datetime(2026, 9, 2, 12, 0)
hist = [{"at": "2026-09-01 10:00", "states": {"P4": CUMPLE}},
        {"at": "2026-09-01 12:00", "states": {"P4": AVISO}},
        {"at": "2026-09-02 09:00", "states": {"P4": AVISO}},
        {"at": "2026-09-02 11:00", "states": {"P7": CUMPLE}}]      # did not measure P4
d = since_when("P4", AVISO, hist, ahora)
caso("since when: skips runs that did not measure that key",
     "2026-09-01 12:00", d.strftime("%Y-%m-%d %H:%M") if d else None)
caso("since when: a different state -> None", None, since_when("P4", CUMPLE, hist, ahora))
caso("since when: no history at all -> None", None, since_when("P4", AVISO, [], ahora))

# ── history never breaks a run ──────────────────────────────────────────────
h = History("/proc/this/cannot/be/written/ever.jsonl")
h.append([{"key": "a", "state": CUMPLE}], "fast")
caso("an unwritable history does NOT crash the run", [], h.read())

# ── the mode filter ─────────────────────────────────────────────────────────
reg3 = []


@promise("F", "fast one", registry=reg3)
def _():
    return CUMPLE


@promise("S", "slow one", mode="slow", registry=reg3)
def _():
    return CUMPLE


s3 = Scale(registry=reg3, planted_cases=[])
estados = {r["key"]: r["state"] for r in s3.weigh(("fast",))}
caso("mode filter: the slow one comes back unmeasured", UNMEASURED, estados["S"])
estados = {r["key"]: r["state"] for r in s3.weigh(("fast", "slow"))}
caso("mode filter: asked for, it is measured", CUMPLE, estados["S"])

# ── the planted runner catches a scale that does NOT see ────────────────────
malos = [{"name": "a scale that reports fine on a broken thing",
          "expect": NO_CUMPLE, "fn": lambda: (CUMPLE, "", "")}]
import io
perdidos = run_planted(malos, out=io.StringIO())
caso("the planted runner catches a scale that does not see", 1, perdidos)

buenos = [{"name": "sees it", "expect": NO_CUMPLE, "fn": lambda: (NO_CUMPLE, "", "")}]
caso("and passes one that does", 0, run_planted(buenos, out=io.StringIO()))

crash = [{"name": "the case itself explodes", "expect": CUMPLE,
          "fn": lambda: 1 / 0}]
caso("a planted case that crashes counts as missed, not as passed",
     1, run_planted(crash, out=io.StringIO()))

# ── colour never leaks into a redirected run ────────────────────────────────
salida = io.StringIO()          # not a tty
Scale(name="x", registry=reg3, planted_cases=[]).report(
    s3.weigh(("fast",)), v, ("fast",), out=salida)
caso("no escape codes when the output is not a terminal",
     False, "\033" in salida.getvalue())

# ── a state outside the five is "could not tell", never green ───────────────
# Found on 2026-09-07 by planting it: a probe returning "KEPT" (a typo for the
# real value "kept") was counted as measured, matched none of the failures, and
# the run exited 0. The scale said "kept 1/2" and went green over a promise it
# had never read. That is the exact failure this file exists to refuse, living
# inside the file itself.
reg4 = []


@promise("A", "answers properly", registry=reg4)
def _():
    return CUMPLE


@promise("B", "answers with a typo", registry=reg4)
def _():
    return "KEPT", "looks fine to a human", ""


s4 = Scale(registry=reg4, planted_cases=[])
lect4 = s4.weigh()
estados4 = {r["key"]: r["state"] for r in lect4}
caso("an unreadable state -> unmeasurable, not green", UNMEASURABLE, estados4["B"])
caso("and it shows what came back", True, "'KEPT'" in dict(
    (r["key"], r["detail"]) for r in lect4)["B"])
caso("so the run exits 3, not 0", 3, s4.verdict(lect4)["exit_code"])
caso("and the typo is not counted as kept", 1, s4.verdict(lect4)["kept"])
# verdict is a staticmethod anyone can call with readings the scale did not make
caso("verdict holds the rule on readings it did not produce", 3, Scale.verdict(
    [{"key": "a", "state": "Broken"}, {"key": "b", "state": CUMPLE}])["exit_code"])

# ── and the report must survive it instead of dying with a KeyError ─────────
salida4 = io.StringIO()
try:
    s4.report(lect4, s4.verdict(lect4), ("fast",), out=salida4)
    caso("the report survives a state the palette does not know", True,
         "UNMEASURABLE" in salida4.getvalue())
except Exception as e:
    caso("the report survives a state the palette does not know", True,
         "crashed: %s" % e)
# even one handed in raw, bypassing weigh
salida5 = io.StringIO()
try:
    Scale(name="raw", registry=[], planted_cases=[]).report(
        [{"key": "Z", "title": "t", "how": "", "mode": "fast",
          "state": "Purple", "detail": "", "remedy": ""}],
        Scale.verdict([{"key": "Z", "state": "Purple"}]), ("fast",), out=salida5)
    caso("and a raw unknown state does not crash the report", True,
         "PURPLE" in salida5.getvalue())
except Exception as e:
    caso("and a raw unknown state does not crash the report", True,
         "crashed: %s" % e)

# ── planted-case coverage: the project's own rule, applied to itself ────────
cubre = [{"name": "covers A", "expect": CUMPLE, "key": "A",
          "fn": lambda: (CUMPLE, "", "")}]
salida6 = io.StringIO()
perdidos6 = run_planted(cubre, out=salida6, registry=reg4)
caso("coverage names the promise with no planted case", True,
     "no planted case: B" in salida6.getvalue())
caso("and reporting a gap is NOT a miss (exit code untouched)", 0, perdidos6)

sin_clave = [{"name": "no key", "expect": CUMPLE, "fn": lambda: (CUMPLE, "", "")}]
salida7 = io.StringIO()
run_planted(sin_clave, out=salida7, registry=reg4)
caso("a suite that never opts in sees no coverage line", False,
     "planted case" in salida7.getvalue())

todo_cubierto = [{"name": "A", "expect": CUMPLE, "key": "A",
                  "fn": lambda: (CUMPLE, "", "")},
                 {"name": "B", "expect": CUMPLE, "key": "B",
                  "fn": lambda: (CUMPLE, "", "")}]
salida8 = io.StringIO()
run_planted(todo_cubierto, out=salida8, registry=reg4)
caso("and says so when every promise is covered", True,
     "every promise has a planted case" in salida8.getvalue())

# ── the scale weighing itself: did it actually run? ─────────────────────────
# The gap this project spent a version denouncing one floor down. The proof it
# was a gap is three cases below: without expect_every, a scale whose cron was
# deleted months ago reports every promise kept and exits 0.
import json as _json
import os
import shutil
import tempfile

from promise_scale import Carry, _hours, judge_last_run

caso("ran: 3 h ago on a daily scale -> kept", CUMPLE, judge_last_run(3, 24)[0])
caso("ran: 25 h on a daily scale -> still kept (cron jitter)",
     CUMPLE, judge_last_run(25, 24)[0])
caso("ran: 27 h on a daily scale -> unmeasurable, past the slack",
     UNMEASURABLE, judge_last_run(27, 24)[0])
caso("ran: 3 days ago -> unmeasurable, NEVER broken (you stopped looking)",
     UNMEASURABLE, judge_last_run(74, 24)[0])
caso("and it says how late it is and how often it should run", True,
     "3 days" in judge_last_run(74, 24)[1] and "24 h" in judge_last_run(74, 24)[1])
caso("ran: nothing on record at all -> unmeasurable, not kept",
     UNMEASURABLE, judge_last_run(None, 24)[0])
caso("ran: a cadence nobody can read -> unmeasurable, not kept",
     UNMEASURABLE, judge_last_run(3, None)[0])

caso("duration: 24h", 24.0, _hours("24h"))
caso("duration: 30m", 0.5, _hours("30m"))
caso("duration: 7d", 168.0, _hours("7d"))
caso("duration: a timedelta", 2.0, _hours(timedelta(hours=2)))
caso("duration: nonsense is unreadable and does NOT raise", None, _hours("soon"))
caso("duration: a bare number has no unit -> unreadable", None, _hours("24"))
caso("duration: zero or less is unreadable", None, _hours("0h"))

tmp = tempfile.mkdtemp(prefix="promise-scale-selftest-")
vacio = os.path.join(tmp, "never-written.jsonl")
hist = os.path.join(tmp, "history.jsonl")
with open(hist, "w", encoding="utf-8") as f:
    f.write(_json.dumps({"at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                         "mode": "fast", "states": {"F": CUMPLE}}) + "\n")

regS = []


@promise("F", "a promise that is kept", registry=regS)
def _():
    return CUMPLE


s_nunca = Scale(registry=regS, planted_cases=[], history=vacio, expect_every="24h")
lect_n = s_nunca.weigh()
caso("the scale's own promise is weighed first", "scale", lect_n[0]["key"])
caso("no run on record -> unmeasurable, not green", UNMEASURABLE, lect_n[0]["state"])
caso("so the run exits 3 even though every promise you wrote is kept",
     3, s_nunca.verdict(lect_n)["exit_code"])

s_corrio = Scale(registry=regS, planted_cases=[], history=hist, expect_every="24h")
caso("a run recorded minutes ago -> kept", CUMPLE, s_corrio.weigh()[0]["state"])
caso("and the run is green again", 0,
     s_corrio.verdict(s_corrio.weigh())["exit_code"])

# The same scale WITHOUT expect_every — this is what the gap looked like.
s_ciega = Scale(registry=regS, planted_cases=[], history=vacio)
caso("without expect_every there is no extra promise (nothing changes)",
     1, len(s_ciega.weigh()))
caso("and a scale that has never run once reads as all green — the hole",
     0, s_ciega.verdict(s_ciega.weigh())["exit_code"])

s_sin_hist = Scale(registry=regS, planted_cases=[], history=None,
                   expect_every="24h")
r_sh = s_sin_hist.weigh()[0]
caso("expect_every with no history file -> unmeasurable, and says why", True,
     r_sh["state"] == UNMEASURABLE and "no history file" in r_sh["detail"])

s_malo = Scale(registry=regS, planted_cases=[], history=hist,
               expect_every="soon")
r_m = s_malo.weigh()[0]
caso("an expect_every nobody can parse -> unmeasurable, quoting the value", True,
     r_m["state"] == UNMEASURABLE and "'soon'" in r_m["detail"])

regK = []


@promise("scale", "a promise that took that key first", registry=regK)
def _():
    return CUMPLE


r_k = Scale(registry=regK, planted_cases=[], history=hist,
            expect_every="24h").weigh()[0]
caso("a key collision is reported, never silently skipped", True,
     r_k["state"] == UNMEASURABLE and "already uses the key" in r_k["detail"])

salida9 = io.StringIO()
run_planted([{"name": "F is covered", "expect": CUMPLE, "key": "F",
              "fn": lambda: (CUMPLE, "", "")}],
            out=salida9, registry=s_corrio.promises())
caso("--test asks for a planted case for the scale's own promise too", True,
     "no planted case: scale" in salida9.getvalue())
caso("and --promises lists it, so the table cannot hide it", True,
     "This scale has actually been running" in s_corrio.table())

# ── where a reading came from, and --own ────────────────────────────────────
# "Don't let one layer certify another layer's reading" was the one hard piece
# of advice in the README with no mechanism behind it. This is the mechanism.
regP = []


@promise("A", "something this scale measures itself", registry=regP)
def _():
    return CUMPLE


@promise("B", "something another layer already measured",
         source="the sentinel's report", registry=regP)
def _():
    return CUMPLE


sP = Scale(registry=regP, planted_cases=[])
todas = {r["key"]: r for r in sP.weigh()}
caso("a borrowed reading is measured like any other by default",
     CUMPLE, todas["B"]["state"])
caso("and every reading carries where it came from",
     "the sentinel's report", todas["B"]["source"])
caso("a reading measured here carries no source", "", todas["A"]["source"])

propias = {r["key"]: r for r in sP.weigh(own=True)}
caso("--own drops the borrowed reading", UNMEASURED, propias["B"]["state"])
caso("and names the layer whose word it refused to take", True,
     "the sentinel's report" in propias["B"]["detail"])
caso("--own still measures what this scale measures itself",
     CUMPLE, propias["A"]["state"])
caso("refusing a borrowed reading is a choice, not a failure", 0,
     sP.verdict(sP.weigh(own=True))["exit_code"])

salidaP = io.StringIO()
lectP = sP.weigh()
sP.report(lectP, sP.verdict(lectP), ("fast",), out=salidaP)
caso("the printed report names the source, so nobody reads it as measured here",
     True, "read from the sentinel's report" in salidaP.getvalue())
caso("and the generated promise table marks it too", True,
     "read from the sentinel's report" in sP.table())
salidaO = io.StringIO()
sP.report(lectP, sP.verdict(lectP), ("fast",), out=salidaO, own=True)
caso("an --own report says so in its own header", True,
     "own readings only" in salidaO.getvalue())

# ── carried readings: the expensive ones, with their age welded on ──────────
llevado = os.path.join(tmp, "last-full.json")
regC = []


@promise("Q", "a cheap one", registry=regC)
def _():
    return CUMPLE


@promise("R", "an expensive one", mode="slow",
         how="the full suite with a browser", registry=regC)
def _():
    return NO_CUMPLE, "34 of 35 checks pass", "run the suite"


sC = Scale(registry=regC, planted_cases=[], carry=llevado)
caso("carry asked for and nothing stored yet -> unmeasurable, not unmeasured",
     UNMEASURABLE, {r["key"]: r for r in sC.weigh(("fast",))}["R"]["state"])

sin_carry = Scale(registry=regC, planted_cases=[])
caso("with no carry at all, a skipped mode is still a choice (unmeasured)",
     UNMEASURED, {r["key"]: r for r in sin_carry.weigh(("fast",))}["R"]["state"])

lleno = sC.weigh(("fast", "slow"))
sC.carry.write(lleno, ("fast", "slow"))
r_c = {r["key"]: r for r in sC.weigh(("fast",))}["R"]
caso("the fast run carries the stored reading forward", NO_CUMPLE, r_c["state"])
caso("and cannot print it without saying when it was taken", True,
     "carried from the slow run" in r_c["detail"])
caso("and it is marked as carried, not as measured just now",
     True, r_c.get("carried") is True)


def _guarda(entrada):
    with open(llevado, "w", encoding="utf-8") as f:
        _json.dump({"R": entrada}, f)


hace_40 = (datetime.now() - timedelta(hours=40)).strftime("%Y-%m-%d %H:%M")
_guarda({"at": hace_40, "mode": "slow", "state": NO_CUMPLE,
         "detail": "34 of 35 checks pass", "remedy": ""})
r_v = {r["key"]: r for r in sC.weigh(("fast",))}["R"]
caso("a stored reading past its limit -> unmeasurable, NOT unmeasured",
     UNMEASURABLE, r_v["state"])
caso("and it says how old it was and what the limit is", True,
     "40 h" in r_v["detail"] and "26h" in r_v["detail"])

hace_2 = (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
_guarda({"at": hace_2, "mode": "slow", "state": NO_CUMPLE,
         "detail": "34 of 35 checks pass", "remedy": ""})
sC.carry.write(sC.weigh(("fast",)), ("fast",))
with open(llevado, encoding="utf-8") as f:
    quedo = _json.load(f)["R"]["at"]
caso("a carried reading is never written back — or it would never grow old",
     hace_2, quedo)

_guarda({"at": datetime.now().strftime("%Y-%m-%d %H:%M"), "mode": "slow",
         "state": "fine", "detail": "", "remedy": ""})
caso("a stored state outside the five -> unmeasurable, not green", UNMEASURABLE,
     {r["key"]: r for r in sC.weigh(("fast",))}["R"]["state"])

# Caught on 2026-09-07 by running the example twice on a clean machine, after
# twenty green cases here: the first fast run stored its own "there is no
# stored reading yet" line, and the second run carried that forward as if it
# were a reading. A note about the absence of a measurement is not one.
limpio = os.path.join(tmp, "clean-carry.json")
sV = Scale(registry=regC, planted_cases=[], carry=limpio)
sV.carry.write(sV.weigh(("fast",)), ("fast",))
caso("an 'I could not measure this' note is never filed as a measurement",
     False, "R" in sV.carry.read())
r_v2 = {r["key"]: r for r in sV.weigh(("fast",))}["R"]
caso("so the next fast run still says it is missing", UNMEASURABLE, r_v2["state"])
caso("and never claims it was carried", None, r_v2.get("carried"))

roto = Carry("/proc/this/cannot/be/written/ever.json")
roto.write(lleno, ("fast", "slow"))
caso("an unwritable carry file does NOT crash the run", {}, roto.read())

shutil.rmtree(tmp, ignore_errors=True)

print("\n  [scale-self-test] missed=%d\n" % fallas)
sys.exit(1 if fallas else 0)
