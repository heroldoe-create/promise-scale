# promise-scale

**How I measure whether my agent system actually keeps what it promises.**

A dashboard that is all green because nobody is looking is worse than a red one. Every health check answers *"is it OK?"*. This one also answers ***"could I even tell?"*** — and refuses to round that up.

```python
from promise_scale import promise, Scale, CUMPLE, NO_CUMPLE, UNMEASURABLE

@promise("P1", "Photos from the phone still arrive",
         how="count of files added in the last 24 h, from the backup log")
def _():
    n = photos_added_last_24h()
    if n is None:
        return UNMEASURABLE, "cannot read the photo log", "check the mount"
    if n == 0:
        return NO_CUMPLE, "0 photos in 24 h", "open the app, check it is logged in"
    return CUMPLE, "%d photos arrived" % n, ""

Scale(name="home server").run()
```

```
  home server  v0.2.0  (fast)

  P1    ● KEPT          Photos from the phone still arrive
        41 photos arrived in 24 h
  P2    ● BROKEN        There is a backup, it is recent, and it is not empty
        the backup ran but wrote 0 MB
        like this for 31 h (since 2026-09-01 12:10)
        to fix: check the source path
  P3    ● UNMEASURABLE  The brand mark can actually be seen
        could not compute the contrast
  P4    ● KEPT          There is room on the disk
        314 GB free (67%)

  1 of 4 promises BROKEN: P2
```

Single file. No dependencies. Python 3.9+. MIT.

## Try it in 30 seconds

```bash
git clone https://github.com/heroldoe-create/promise-scale && cd promise-scale
python3 minimal.py          # two promises, both kept
python3 example.py          # seven promises, the full shape
python3 example.py --test   # 19 planted failures, all caught
```

`minimal.py` is 35 lines (24 of code). Copy it, replace the fake numbers with real ones, and you have a scale.

## The one rule

**`UNMEASURABLE` never counts as green.**

A probe that cannot answer looks exactly like a probe that answered "fine". This scale gives "could not tell" its own state, its own colour, and its own exit code — and orders it *above* warnings, because nobody investigates a shrug.

## The five states

| State | Meaning | Exit code |
|---|---|---:|
| `kept` | measured, and the promise holds | 0 |
| `warning` | measured, holding, but heading the wrong way | 2 |
| `broken` | measured, and it does not hold | 1 |
| **`unmeasurable`** | **we tried to measure and could not** — never green | **3** |
| `unmeasured` | we chose not to run it here (too slow, too costly) | 0 |

## What you get

- **Promises in the words of whoever depends on the system.** `"photos still arrive"`, not `check_rsync_exit_code`.
- **"Since when."** Each run appends to a history file, so a promise says *"broken for 31 h"* instead of just *"broken"*.
- **Planted failures.** `--test` breaks each promise on purpose and demands the scale *sees* it. A scale nobody has seen fail is not a scale.
- **A generated promise table.** `--promises` prints your declarations as markdown, so documentation and code cannot drift apart.
- **The scale watches whether the scale ran.** `Scale(expect_every="24h")` adds one implicit promise: *this scale has actually been running*. Delete the cron entry and it goes `unmeasurable`.
- **Where a reading came from.** `@promise(source=...)` marks borrowed readings; `--own` drops them.
- **Expensive readings, carried with their age.** The full run leaves its readings; the fast run carries them forward, always saying when they were taken.

## Install

Copy `promise_scale.py` next to your code. That is the whole install.

```bash
python3 example.py           # a full worked example
python3 example.py --all     # including slow promises
python3 example.py --own     # only what this scale measures itself
python3 example.py --test    # planted failures
python3 example.py --promises # the promise table as markdown
```

## What this is not

Not a monitoring system, not an agent framework, not an orchestrator. This is the small piece that sits on top of whatever you already have and asks: **can you still tell?**

## Where it comes from

Extracted from a working system that runs several AI assistants on one home server under shared rules. Its scale weighs fourteen promises on a cron and has caught things quietly broken for hours. The orchestration part is not novel — this part I could not find anywhere, so here it is.

## Add it to your CI

This repo ships a GitHub Actions template: go to the *Actions* tab, click *New workflow*, search for *promise scale*. It writes the workflow including a daily schedule, because a scale that never ran looks exactly like a quiet night.

## Licence

MIT © Heroldo Escobedo
