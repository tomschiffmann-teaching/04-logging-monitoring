# SETUP — How to run everything (read this first if you're new)

You do **not** need to know Python. You only need to **type commands in a terminal**.
This page shows every command you'll use tonight.

---

## 1. Open a terminal
- **macOS:** press `Cmd + Space`, type `Terminal`, hit Enter.
- **Windows:** open `PowerShell` (Start menu → type "PowerShell").
- **Linux:** open your `Terminal` app.

A terminal is just a window where you type commands and press Enter.

---

## 2. Check the tools are installed
Type each line, press Enter. You should see a version number, not an error.
```bash
python3 --version      # e.g. Python 3.12.2   (on Windows try: python --version)
docker --version       # e.g. Docker version 27.x
docker compose version # e.g. Docker Compose version v2.x
```
- No Python? Install from https://www.python.org/downloads/ (tick "Add to PATH" on Windows).
- No Docker? Install **Docker Desktop** from https://www.docker.com/products/docker-desktop/
  and make sure it's **running** (whale icon in the menu bar / system tray) before Part 2.

> On Windows, if `python3` says "not found", use `python` instead everywhere in this course.

---

## 3. Go into the exercise folder ("cd" = change directory)
First, navigate to where this course lives. Example:
```bash
cd ~/Desktop/BS_2026_01/repos/04-logging-monitoring
```
**Easiest trick:** type `cd ` (with a space), then **drag the folder** from Finder/Explorer
into the terminal — it pastes the path for you. Press Enter.

Check you're in the right place:
```bash
ls        # macOS/Linux: lists files. You should see 01-logging and 02-monitoring
dir       # Windows PowerShell equivalent
```

---

## 4. Run a Python script
A Python file ends in `.py`. To run one, type `python3` then the path to the file.

Move into the folder, then run the file:
```bash
cd 01-logging/part1-basics
python3 01_print_vs_logging.py
```
That's it — the program runs and prints its output right there in the terminal.
To run the next one, just change the filename:
```bash
python3 02_log_levels.py
```

Go **back up** one folder with `cd ..`:
```bash
cd ..                      # up one level
cd ../part2-find-the-bug   # up one and into another folder
```

### How to "add a log statement" (you'll do this in Part 2 of the logging exercise)
1. Open the `.py` file in any text editor (VS Code, Notepad, TextEdit in plain-text mode).
2. Add a line like this where you want to peek at a value:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.debug("value here is: %s", some_variable)
   ```
3. **Save** the file, then run it again with `python3 thefile.py`. Your new line prints.

Nothing to install — `logging` comes built into Python.

### To stop a running program
Press `Ctrl + C` in the terminal. (Some scripts in Part 2 loop forever on purpose.)

---

## 5. Run a Docker exercise
Docker exercises have a `docker-compose.yml` file. You `cd` into that folder and run:
```bash
docker compose up -d        # start everything in the background
docker compose ps           # see what's running
docker compose logs -f      # watch the logs live (Ctrl+C to stop watching)
docker compose down         # stop and remove everything when finished
```
Make sure **Docker Desktop is open and running** first, or these will error.

---

## Cheat sheet
| I want to... | Command |
|---|---|
| See where I am / list files | `ls` (mac/linux) · `dir` (windows) · `pwd` shows full path |
| Go into a folder | `cd foldername` |
| Go up one folder | `cd ..` |
| Run a Python file | `python3 filename.py` (or `python filename.py` on Windows) |
| Stop a running program | `Ctrl + C` |
| Start a Docker stack | `docker compose up -d` |
| Watch Docker logs | `docker compose logs -f` |
| Stop a Docker stack | `docker compose down` |

Now go to `README.md` and start with Exercise 1.
