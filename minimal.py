#!/usr/bin/env python3
"""The smallest possible scale. Copy this file, change the promises, run it.

    python3 minimal.py

That is the whole install. promise_scale.py is one file with no dependencies.
"""

from promise_scale import promise, Scale, CUMPLE, NO_CUMPLE, UNMEASURABLE


@promise("P1", "The disk has room", how="df on the data volume")
def _():
    free_gb = 314.0  # replace with: shutil.disk_usage("/").free / 1e9
    if free_gb is None:
        return UNMEASURABLE, "could not read disk", "check the mount"
    if free_gb < 10:
        return NO_CUMPLE, "%.0f GB free" % free_gb, "free some space now"
    return CUMPLE, "%.0f GB free" % free_gb, ""


@promise("P2", "The API answers", how="GET /health")
def _():
    # replace with: requests.get("https://your-api/health").status_code
    status = 200
    if status is None:
        return UNMEASURABLE, "the request failed", "check the URL and network"
    if status != 200:
        return NO_CUMPLE, "HTTP %d" % status, "check the service"
    return CUMPLE, "HTTP 200", ""


if __name__ == "__main__":
    import sys
    sys.exit(Scale(name="my system").run())
