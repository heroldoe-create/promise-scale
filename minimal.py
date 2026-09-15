#!/usr/bin/env python3
"""The smallest possible scale. Copy this file, change the promises, run it.

    python3 minimal.py                 # weigh the promises
    python3 minimal.py --test          # the planted failures

That is the whole install. promise_scale.py is one file with no dependencies.

Notice the SHAPE: each promise splits its *reading* (going out and getting a
number) from its *judgement* (deciding what the number means). That split is the
only reason the planted cases at the bottom can exist — you feed the judgement a
number you invented and demand the scale sees it. A judge that reads the disk
itself cannot be planted, only mocked, and a scale you cannot plant is a scale
nobody has ever seen fail.
"""

from promise_scale import (
    CUMPLE, NO_CUMPLE, UNMEASURABLE, Scale, planted, promise,
)


# ─────────────────────────── the judgements ─────────────────────────────────

def judge_disk(free_gb):
    if free_gb is None:
        return UNMEASURABLE, "could not read disk", "check the mount"
    if free_gb < 10:
        return NO_CUMPLE, "%.0f GB free" % free_gb, "free some space now"
    return CUMPLE, "%.0f GB free" % free_gb, ""


def judge_api(status):
    if status is None:
        return UNMEASURABLE, "the request failed", "check the URL and network"
    if status != 200:
        return NO_CUMPLE, "HTTP %d" % status, "check the service"
    return CUMPLE, "HTTP 200", ""


# ──────────────────────────── the promises ──────────────────────────────────

@promise("P1", "The disk has room", how="df on the data volume")
def _():
    free_gb = 314.0  # replace with: shutil.disk_usage("/").free / 1e9
    return judge_disk(free_gb)


@promise("P2", "The API answers", how="GET /health")
def _():
    # replace with: requests.get("https://your-api/health").status_code
    status = 200
    return judge_api(status)


# ─────────────────────── the planted failures ───────────────────────────────
# Break each promise on purpose and demand the scale SEES it. A new promise
# arrives with its planted case, or it does not arrive. Copy this file and these
# come with it: a scale that starts with no planted case starts green with
# nothing wired behind it, which is the thing this project exists to catch.

@planted("disk: 3 GB free -> broken", NO_CUMPLE, key="P1")
def _():                 return judge_disk(3.0)


@planted("disk: unreadable -> unmeasurable, NOT fine", UNMEASURABLE, key="P1")
def _():                 return judge_disk(None)


@planted("api: HTTP 503 -> broken", NO_CUMPLE, key="P2")
def _():                 return judge_api(503)


@planted("api: request failed -> unmeasurable, not 'down'", UNMEASURABLE, key="P2")
def _():                 return judge_api(None)


if __name__ == "__main__":
    import sys
    sys.exit(Scale(name="my system").run())
