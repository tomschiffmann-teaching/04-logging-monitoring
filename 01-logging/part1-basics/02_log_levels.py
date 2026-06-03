"""
02 — The five log levels (the "volume knob")

Run it:
    python3 02_log_levels.py

The five levels, from least to most severe:
    DEBUG     - tiny details, useful while developing / debugging
    INFO      - normal events ("server started", "user logged in")
    WARNING   - something unexpected, but we keep going
    ERROR     - something failed, this operation could not complete
    CRITICAL  - the whole program/service is in danger

KEY IDEA: basicConfig(level=...) is the volume knob.
Only messages at that level OR MORE SEVERE are shown.
"""

import logging

# Try changing this ONE line to logging.WARNING, then re-run.
# Watch the DEBUG and INFO lines disappear — without deleting any code.
logging.basicConfig(level=logging.DEBUG)

logging.debug("Loaded 1,250 rows from cache")
logging.info("User 'anna' logged in")
logging.warning("Disk is 85% full")
logging.error("Payment service returned HTTP 500")
logging.critical("Out of memory — shutting down")

# TASKS:
# 1. Run as-is. You see all 5 lines.
# 2. Change level to logging.WARNING. Re-run. Now only WARNING/ERROR/CRITICAL show.
# 3. Change level to logging.ERROR. What survives?
# 4. In your own words: why is this better than deleting print() lines?
