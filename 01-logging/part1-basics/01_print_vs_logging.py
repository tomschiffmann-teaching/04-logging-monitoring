"""
01 — print() vs logging

Run it:
    python3 01_print_vs_logging.py

Notice the difference in the output:
- print() gives you ONLY the text. No time, no severity, no source.
- logging gives you a structured line you can filter and route.
"""

import logging

# --- The old way --------------------------------------------------------
print("Starting the app")
print("Connecting to database")
print("Could not connect!")   # Is this a disaster or no big deal? print can't tell you.

print("-" * 50)

# --- The logging way ----------------------------------------------------
# basicConfig sets up a default "where does it go / how does it look".
# level=DEBUG means: show me everything down to DEBUG.
logging.basicConfig(level=logging.DEBUG)

logging.info("Starting the app")
logging.debug("Connecting to database")
logging.error("Could not connect!")   # Clearly an ERROR. The level tells you.

# TASK: Run this file. Compare the two blocks of output.
#       Which one would you rather read at 2am when something is broken?
