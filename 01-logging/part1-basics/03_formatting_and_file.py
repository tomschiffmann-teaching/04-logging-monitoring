"""
03 — Formatting + writing to console AND a file at the same time

Run it:
    python3 03_formatting_and_file.py

Then look at the new file:
    cat app.log

What's new here:
- A custom FORMAT string: timestamp | level | logger name | message
- TWO destinations ("handlers"):
    * the console (so you see it live)
    * a file app.log (so you have a permanent record)
- A named logger (logging.getLogger(__name__)) instead of the root logger,
  which is the normal, professional way to do it.
"""

import logging

# Format pieces: %(asctime)s = time, %(levelname)s = DEBUG/INFO/...,
#                %(name)s = logger name, %(message)s = your text
FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
formatter = logging.Formatter(FORMAT, datefmt="%H:%M:%S")

logger = logging.getLogger("shop")
logger.setLevel(logging.DEBUG)

# Handler 1: console
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)

# Handler 2: file (appends to app.log)
file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- Use it ---
logger.info("Service started")
logger.debug("Config loaded: max_items=50")
logger.warning("Cache miss for key 'user:42'")
logger.error("Failed to send confirmation email")

# BONUS: log an exception with the full traceback automatically.
try:
    result = 10 / 0
except ZeroDivisionError:
    logger.exception("Math blew up while computing result")
    # logger.exception() is like logger.error() but ALSO prints the traceback.

# TASKS:
# 1. Run it. You see logs in the console.
# 2. Run `cat app.log`. The same logs are saved there too.
# 3. Run the script a 2nd time. Notice the file GREW (FileHandler appends).
# 4. Different handlers can have different levels — try:
#       file_handler.setLevel(logging.ERROR)
#    Now the file only keeps errors, while the console still shows everything.
