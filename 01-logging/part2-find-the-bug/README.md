# Part 2 — Find the bug WITHOUT reading the logic

> 🆕 How to run a script and how to "add a log statement" is in **`../../SETUP.md`** (section 4).

Two programs. Each one runs fine (no crash) but produces a **wrong answer**.

Run them from a terminal inside this folder, e.g. `python3 buggy_discount.py`.

## THE RULES (this is the whole point of the exercise)
1. ❌ Do **not** sit and read the code trying to "spot" the bug in your head.
2. ✅ **Run** the program. See that the output is wrong.
3. ✅ **Add log statements** to watch what the values *actually* are at each step.
4. ✅ Let the logs tell you **which step** turns a right number into a wrong one.

This is how you debug real systems you don't understand: you make the program
*tell you* what it's doing, step by step, instead of guessing.

> Reading code tells you what you *think* it does.
> Logging tells you what it *actually* does. They are often different.

---

## Program 1 — `buggy_discount.py` (easier)

A shop checkout. Run it:
```
python3 buggy_discount.py
```
It prints a final price. The expected correct total is written at the top of the file.
**The printed total is wrong.** Find where.

### How to attack it
The program passes a number through a few functions:
`calculate_cart_total → apply_discount → apply_loyalty_points`.

Add a log line **after each step** showing the running total, e.g.:
```python
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s | %(message)s")

subtotal = calculate_cart_total(cart)
logging.debug("after calculate_cart_total: %s", subtotal)

discounted = apply_discount(subtotal)
logging.debug("after apply_discount: %s", discounted)   # <-- watch this one
...
```
One of those numbers will be "stuck" or "jump" the wrong way. That function holds the bug.
**Tip:** also add a log *inside* the suspicious function to see its local variables.

---

## Program 2 — `buggy_pipeline.py` (harder, subtle)

A sensor data pipeline (fits the monitoring theme!). It reads Celsius readings,
converts them to Fahrenheit, and counts how many are "hot" (> 100°F).

Run it:
```
python3 buggy_pipeline.py
```
The expected count is written at the top of the file. **The program reports the wrong count.**

### How to attack it
The numbers are *close* to correct, so you can't eyeball it — you must log the
**intermediate list** after the conversion step and compare a couple of values by hand:
```python
fahrenheit = celsius_to_fahrenheit(celsius)
logging.debug("converted values: %s", fahrenheit)
# Pick one: 37.8°C should be ~100.04°F. What did the program compute? Why is it off?
```
When you see the converted numbers, the bug becomes obvious.

---

## When you think you found each bug
- Write down (in one sentence) which line is wrong and what it *should* be.
- Only THEN open `SOLUTION.md` to check yourself.
- Did the logs lead you there faster than reading would have? That's the lesson.
