# Part 1 — Logging basics (tasks)

> 🆕 Never run a Python file before? See **`../../SETUP.md`** — it shows how to open a
> terminal, `cd` into this folder, and run a script. No Python knowledge needed.

Work through the three scripts **in order**. Each one is short and has TASKS at the bottom.

First, open a terminal and move into this folder:
```bash
cd 01-logging/part1-basics      # (run from the course root folder)
```
Then run each script:
```bash
python3 01_print_vs_logging.py
python3 02_log_levels.py
python3 03_formatting_and_file.py
```
(On Windows, use `python` instead of `python3` if `python3` isn't found.)

## Checklist — you "get it" when you can answer:
- [ ] What information does a log line give you that a `print()` does not?
- [ ] Name the 5 levels from least to most severe.
- [ ] If the level is set to `WARNING`, will `logging.info(...)` show up? Why not?
- [ ] What is a *handler*? Name two destinations a log can go to.
- [ ] What does `logger.exception(...)` add compared to `logger.error(...)`?

## Mini-challenge (5 min)
Copy `03_formatting_and_file.py` to `my_logger.py` and:
1. Change the time format to include the date (`%Y-%m-%d %H:%M:%S`).
2. Make the **console** show everything but the **file** keep only `WARNING` and worse.
3. Add an `INFO` log every time a "user logs in" (just make up a loop of 3 fake users).

When done → go to `../part2-find-the-bug/`.
