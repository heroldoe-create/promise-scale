# Changelog

## The tag lags the code, and that is said out loud

`__version__` in `promise_scale.py` is what the file on disk actually is. The
GitHub release is cut by hand, separately, and it can be behind. **Right now it
is: the code says `0.2.0` and the newest release is `v0.1.0`.**

That gap is written here instead of being avoided, because the alternative was
leaving `__version__` at `0.1.0` while the file had grown three capabilities —
a project about not rounding your own state up, rounding its own state up. A
declared gap is a fact; an undeclared one is the thing this whole repository is
against.

The release for `0.2.0` is one command, and it belongs to whoever owns the
repository:

```bash
gh release create v0.2.0 --title "v0.2.0 — the scale weighs itself" \
  --notes "The scale now watches whether the scale ran, marks readings it did not take itself, and carries expensive readings forward with their age. See CHANGELOG.md."
```

---

## 0.2.0 — the scale weighs itself (2026-09-07)

Three capabilities the README implied and the file did not have. All additive:
a scale written against `0.1.0` behaves identically until it asks for them. No
new files, no dependencies, still Python 3.9+.

### The scale watches whether the scale ran

`Scale(expect_every="24h")` adds one promise, always measured, before yours:
*this scale has actually been running*. Delete the cron entry and it goes
`unmeasurable` — never `broken`, because you have not learned that the system
is bad, you have learned that you stopped looking.

- late at the cadence plus a tenth of it, so cron jitter is not an alarm
- no history file, or a cadence it cannot parse, or a key already taken by one
  of your promises: each one says exactly that instead of failing quietly
- `judge_last_run()` is exported and pure, so you can plant it
- `--test` counts it: it names `scale` among the promises nobody has ever seen
  fail until you write its case

*Asked for by name by the state of the art: "track check execution rates to
verify monitors run on schedule" (upstat.io, Monitoring the Monitors,
2025-10-16); "heartbeat signals or execution receipts […] so a missing
heartbeat triggers an alert rather than silent absence" (SD Times, Your Agents
Aren't Failing. They're Not Running., 2026-08-03).*

### Where a reading came from, and `--own`

`@promise(..., source="the sentinel's report")` marks a reading this scale did
not take. The source travels into the printed report, `--json` and
`--promises`, and `--own` drops every borrowed reading — so the layer that
wrote that report can run the scale without reading its own output back and
presenting it as a fresh measurement.

This gives a mechanism to *"don't let one layer certify another layer's
reading"*, which until now was the one piece of hard advice in the README that
the project could recommend but not check.

### Expensive readings, carried with their age

`Scale(carry="last-full.json", carry_max_age="26h")` lets the full run leave
its readings for the fast run to carry forward. The age is welded into the
text — there is no way to print a carried reading without saying when it was
taken. Past the limit it becomes `unmeasurable`, not `unmeasured`: once you
have asked for carried readings, not having one is not a choice you made in
this run. A carried reading is never written back to the store, or its clock
would restart on every run and it would never expire.

### Smaller

- an unreadable state is folded into `unmeasurable` on *every* path now, not
  just on a probe that was just run — a carried reading comes out of a file
  anyone can edit
- `--no-history` now means "record nothing", history and carried readings alike
- `Scale(history="~/...")` expands `~` instead of creating a directory called
  `~` beside the script
- the example grew a sixth promise (a borrowed reading) and switches on both
  `expect_every` and `carry`, so all three capabilities are demonstrated by a
  command you can run
- CI runs the example twice and demands the first run exit 3: if the self-watch
  ever goes quiet, the first run comes back green and that step catches it
- self-test cases 31 → 80, all planted; every one of the three mechanisms was
  mutation-tested to prove the cases actually bite

### Found while building this

The first fast run stored its own *"there is no stored reading yet"* line — an
`unmeasurable` about the absence of a reading — and the next run carried it
forward as though it were one. Caught by running the example end to end on a
clean machine, after the new cases were already green. A note saying "I could
not measure this" is not a measurement, and filing it as one turns the whole
mechanism into the stale green it exists to prevent.

## 0.1.0 — first public version (2026-09-02)

Five states with `unmeasurable` never counting as green and sorting above
warnings, exit codes for cron and CI, "since when" from a JSONL history,
planted failures with `--test`, and a generated promise table.
