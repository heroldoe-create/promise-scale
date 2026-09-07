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

print("\n  [scale-self-test] missed=%d\n" % fallas)
sys.exit(1 if fallas else 0)
