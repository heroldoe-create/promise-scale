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

print("\n  [scale-self-test] missed=%d\n" % fallas)
sys.exit(1 if fallas else 0)
