# SOLUTION — only open after you tried with logs!

## Program 1 — `buggy_discount.py`
**Symptom:** prints `23.00`, expected `20.55`. The 10% discount (2.45) never happened.

**What the logs show:** the value going *into* `apply_discount` is `24.50`, and the
value coming *out* is still `24.50`. The discount step is the culprit.

**The bug** — in `apply_discount`:
```python
def apply_discount(total):
    if total > 20:
        discount = total * 0.10
        discounted = total - discount   # correct value is computed here...
    return total                        # BUG: returns the ORIGINAL total, not `discounted`
```
It correctly *computes* the discount but then **returns the wrong variable**. This is
exactly the kind of bug you'd skim right past while reading ("yep, discount logic, looks
fine") — but logging the in/out values makes it obvious in seconds.

**Fix:** `return discounted` when the discount applies:
```python
def apply_discount(total):
    if total > 20:
        discount = total * 0.10
        return total - discount
    return total
```
Now: 24.50 − 2.45 − 1.50 = **20.55** ✅

---

## Program 2 — `buggy_pipeline.py`
**Symptom:** reports `2` hot readings, expected `4`.

**What the logs show:** logging the converted list reveals values like
`[100.0, 100.0, 101.0, 102.0, 99.0, 96.0]`. But 37.9°C should be **100.22**, not 100.0 —
the conversion is *flooring* the result. Two readings that should be just over 100 land
*exactly on* 100, so the `> 100` filter drops them.

**The bug** — in `celsius_to_fahrenheit`:
```python
f = c * 9 // 5 + 32   # BUG: // is INTEGER division (floors the result)
```
`//` throws away the fractional part. `37.9 * 9 // 5 = 341.1 // 5 = 68.0` → `+32 = 100.0`
instead of `100.22`.

**Fix:** use normal division `/`:
```python
f = c * 9 / 5 + 32
```
Now the converted values are `[100.22, 100.40, 101.30, 102.20, 99.50, 96.80]` and the
count is **4** ✅

---

## The takeaway
Neither bug was a crash. Reading the code, both functions "look correct." Only by making
the program **report its actual intermediate values** did the wrong step reveal itself.
That's the skill: when something is wrong and you don't know why, **add logs and let the
program show you** — start broad (one log per step), then zoom into the bad step.
