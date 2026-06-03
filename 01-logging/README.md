# Exercise 1 — Logging

Two parts:

1. **`part1-basics/`** — Learn the logging module: levels, formatting, writing to a file.
2. **`part2-find-the-bug/`** — Two small programs give *wrong answers*. Your job: find the bug **without trying to read/understand the logic** — only by **running the program and adding log statements** to watch what the values actually do.

## Why logging (not `print`)?
`print()` is fine for a quick check, but real software needs:
- **Levels** — separate "just info" from "something is wrong" (DEBUG / INFO / WARNING / ERROR / CRITICAL).
- **Context** — automatic timestamp, which module, which line.
- **Control** — turn detail on/off without deleting code (change one line: the log *level*).
- **Destinations** — console *and* a file (or later: a central system) at the same time.

Mental model:
> You sprinkle log statements at **every level of detail**. Then you turn a single "volume knob" (the level) to decide how much you actually see. Nothing gets deleted — you just lower the volume in production and raise it when hunting a bug.

Start with `part1-basics/`.
