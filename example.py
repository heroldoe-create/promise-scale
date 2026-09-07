#!/usr/bin/env python3
"""A worked example: weighing a small home server.

Run it:
    python3 example.py                 # the fast promises
    python3 example.py --all           # including the slow one
    python3 example.py --test          # the planted failures
    python3 example.py --brief         # one line, for cron
    python3 example.py --promises      # the promise table, as markdown

No reading here touches your machine — they are faked so the example runs
anywhere. It does write one thing: its own history file, under
~/.local/share/example-scale/, because "broken for 31 h" needs somewhere to
count from. `--no-history` skips even that.

What is real is the SHAPE: notice that every promise splits its
*reading* (going out and getting a number) from its *judgement* (deciding what
the number means). That split is what makes planted failures possible: you can
feed the judgement a number you invented, and demand the scale sees it.

A judge that reads the disk itself cannot be planted, only mocked — and a scale
you cannot plant is a scale nobody has ever seen fail.
"""

from datetime import datetime, timedelta

from promise_scale import (
    AVISO, CUMPLE, NO_CUMPLE, UNMEASURABLE, Scale, planted, promise,
)

# ─────────────────────────── the judgements ─────────────────────────────────
# Pure functions: numbers in, verdict out. No disk, no network, no clock.

def judge_photos(n_last_24h):
    """The promise is that photos ARRIVE — not that the backup process is up.

    This is the one that started the whole idea. Four containers healthy, page
    returning 200, clean logs, and twenty hours without a single photo. Every
    watched thing was fine; nobody watched the thing the user cared about.
    """
    if n_last_24h is None:
        return (UNMEASURABLE, "cannot read the photo log",
                "check that the log file exists and is readable")
    if n_last_24h == 0:
        return (NO_CUMPLE, "0 photos in the last 24 h",
                "open the phone app and check it is still logged in")
    return CUMPLE, "%d photos arrived in 24 h" % n_last_24h, ""


def judge_backup(hours_old, size_mb):
    if hours_old is None:
        return UNMEASURABLE, "no backup log at all", "run the backup by hand once"
    if hours_old > 26:
        return (NO_CUMPLE, "last backup %.0f h ago (%d MB)" % (hours_old, size_mb),
                "run: backup-now")
    if size_mb == 0:
        # An empty backup is worse than a missing one: it looks like success.
        return NO_CUMPLE, "the backup ran but wrote 0 MB", "check the source path"
    if hours_old > 8:
        return AVISO, "last backup %.0f h ago (%d MB)" % (hours_old, size_mb), ""
    return CUMPLE, "%.0f h ago, %d MB" % (hours_old, size_mb), ""


def judge_logo_contrast(ratio):
    """"Does it load?" is not "can it be seen".

    A logo sat on a dark toolbar painting dark ink. The old test asked whether
    the image had loaded — and an image loads perfectly well when it paints
    dark-on-dark. It was invisible for hours behind a green check.
    """
    if ratio is None:
        return UNMEASURABLE, "could not compute the contrast", "check the selector"
    if ratio < 3:
        return (NO_CUMPLE, "%.2f:1 against its own background — invisible" % ratio,
                "the mark inherits the wrong colour")
    return CUMPLE, "%.2f:1" % ratio, ""


def judge_suite(passed, total):
    """Split out for the same reason as the others: so it can be planted.

    It was written inline in the promise below, and that alone was enough to
    leave P5 the one promise in this file nobody had ever seen fail — the exact
    thing the README asks you not to do, sitting in the file that teaches it.
    """
    if total is None:
        return UNMEASURABLE, "the suite did not report a total", "run it by hand"
    if passed < total:
        return NO_CUMPLE, "%d of %d checks pass" % (passed, total), "run the suite"
    return CUMPLE, "%d/%d" % (passed, total), ""


def judge_disk(free_gb, total_gb):
    if free_gb is None:
        return UNMEASURABLE, "df gave nothing", ""
    pct = 100 * free_gb / total_gb
    if pct < 5:
        return NO_CUMPLE, "%.0f GB free (%.0f%%)" % (free_gb, pct), "free some space now"
    if pct < 15:
        return AVISO, "%.0f GB free (%.0f%%)" % (free_gb, pct), ""
    return CUMPLE, "%.0f GB free (%.0f%%)" % (free_gb, pct), ""


# ─────────────────────────── the readings ───────────────────────────────────
# In a real system these go out and measure. Here they are faked on purpose.

def read_photos():       return 41
def read_backup():       return 3.2, 288
def read_logo():         return 14.74
def read_disk():         return 314.0, 466.0
def read_slow_suite():   return 34, 34


# ─────────────────────────── the promises ───────────────────────────────────

@promise("P1", "Photos from the phone still arrive",
         how="count of files added in the last 24 h, read from the backup log")
def _():
    return judge_photos(read_photos())


@promise("P2", "There is a backup, it is recent, and it is not empty",
         how="age and size of the newest backup file")
def _():
    return judge_backup(*read_backup())


@promise("P3", "The brand mark can actually be seen",
         how="computed contrast of the mark against the background it hangs on")
def _():
    return judge_logo_contrast(read_logo())


@promise("P4", "There is room on the disk", how="df on the data volume")
def _():
    return judge_disk(*read_disk())


@promise("P5", "The test suite still catches what it promises to catch",
         mode="slow", how="the full suite with a browser — about 3 minutes")
def _():
    return judge_suite(*read_slow_suite())


# ─────────────────────── the planted failures ───────────────────────────────
# Break each promise on purpose and demand the scale SEES it. A new promise
# arrives with its planted case, or it does not arrive.
#
# `key=` names the promise each case belongs to, so `--test` can close the loop
# and tell you which promises nobody has ever seen fail. Run it: the last line
# says "every promise has a planted case". Delete one of these and it says which.

@planted("photos: 0 in 24 h -> broken", NO_CUMPLE, key="P1")
def _():                 return judge_photos(0)


@planted("photos: log unreadable -> unmeasurable, NOT fine", UNMEASURABLE, key="P1")
def _():                 return judge_photos(None)


@planted("photos: 41 arrived -> kept", CUMPLE, key="P1")
def _():                 return judge_photos(41)


@planted("backup: 30 h old -> broken", NO_CUMPLE, key="P2")
def _():                 return judge_backup(30, 100)


@planted("backup: ran but wrote 0 MB -> broken (looks like success)", NO_CUMPLE, key="P2")
def _():                 return judge_backup(1, 0)


@planted("backup: 12 h old -> warning", AVISO, key="P2")
def _():                 return judge_backup(12, 100)


@planted("logo: 1.04:1, dark on dark -> broken", NO_CUMPLE, key="P3")
def _():                 return judge_logo_contrast(1.04)


@planted("logo: 14.7:1 -> kept", CUMPLE, key="P3")
def _():                 return judge_logo_contrast(14.74)


@planted("disk: 3% free -> broken", NO_CUMPLE, key="P4")
def _():                 return judge_disk(14.0, 466.0)


@planted("suite: 33 of 34 pass -> broken", NO_CUMPLE, key="P5")
def _():                 return judge_suite(33, 34)


@planted("suite: no total reported -> unmeasurable, not 'all pass'", UNMEASURABLE, key="P5")
def _():                 return judge_suite(0, None)


# And the rule itself, planted: unmeasurable must not exit 0.
@planted("verdict: one unmeasurable -> exit 3, never 0", 3)
def _():
    v = Scale.verdict([{"key": "a", "state": UNMEASURABLE},
                       {"key": "b", "state": CUMPLE}])
    return v["exit_code"], str(v), ""


@planted("verdict: one skipped by mode -> exit 0 (not a failure)", 0)
def _():
    v = Scale.verdict([{"key": "a", "state": "unmeasured"},
                       {"key": "b", "state": CUMPLE}])
    return v["exit_code"], str(v), ""


if __name__ == "__main__":
    import sys
    sys.exit(Scale(
        name="home server",
        version="v1.4.2",
        history="~/.local/share/example-scale/history.jsonl".replace(
            "~", str(__import__("pathlib").Path.home())),
    ).run())
