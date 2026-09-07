# Contributing

Short, because there is only one rule that is unusual.

## The one rule

**A new promise arrives with its planted case, or it does not arrive.**

If you add a `@promise`, add at least one `@planted` case that breaks it on
purpose and demands the scale sees it — and tag the case with `key=` so
`--test` can tell that the promise is covered:

```python
@promise("P6", "The certificate is still valid", how="days to expiry")
def _():
    return judge_cert(days_to_expiry())

@planted("cert: expires in 3 days -> broken", NO_CUMPLE, key="P6")
def _():                 return judge_cert(3)

@planted("cert: cannot be read -> unmeasurable, NOT fine", UNMEASURABLE, key="P6")
def _():                 return judge_cert(None)
```

The second case is the one people skip, and it is the one this project exists
for. A probe that cannot answer must not be able to pass for one that answered
"fine".

To make that possible, **split the reading from the judgement**: the reading
goes out and gets a number, the judgement decides what the number means. A
judgement that reads the disk itself cannot be planted, only mocked.

## Running everything

```bash
python3 test_promise_scale.py     # the scale's own planted failures
python3 example.py --test         # the worked example's
python3 example.py --all --brief  # and it still runs
```

All three run in CI on Python 3.9, 3.11 and 3.13, on every push. They need no
dependencies, no virtualenv and no test framework — if any of that becomes
necessary, that is a change worth discussing first.

## What will be turned down

- **A dependency.** The install is "copy one file". A health check that can
  break during a `pip install` is a health check with a new way to fail.
- **A state that softens `unmeasurable`.** Downgrading it to a warning, letting
  it exit 0 behind a flag, or folding it into "not applicable" removes the only
  reason this exists.
- **A second file for the library.** The example, the tests and the docs are
  separate; `promise_scale.py` is not.
- **Anything that turns this into a monitoring system.** See "What this is not"
  in the README. It sits on top of whatever you already run.

## Renaming things

The stored state values (`kept`, `warning`, `broken`, `unmeasurable`,
`unmeasured`) are written into everyone's history file. Changing a value
silently restarts "since when" for every promise that used it, and the run that
does it looks completely normal. Same for a promise `key`: history is keyed on
it. Treat both as data, not as labels.

## Questions

Discussions are on. There is no wrong question — if something in the README
only makes sense to someone who already ran a home server into this problem,
that is a defect in the README, and saying so is a contribution.
