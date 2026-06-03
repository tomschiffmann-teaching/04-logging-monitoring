"""
A tiny fake web service that logs to STDOUT (standard output).

IMPORTANT IDEA: a containerized app should NOT manage its own log files.
It just prints to stdout/stderr, and Docker captures that. This is the
"12-factor" approach — the container engine owns the logs.

This script just loops forever, logging fake requests.
"""

import logging
import random
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | web | %(message)s",
)

PATHS = ["/", "/login", "/cart", "/checkout", "/api/items"]

logging.info("web service started")

while True:
    path = random.choice(PATHS)
    roll = random.random()
    if roll < 0.05:
        logging.error("500 Internal Server Error on %s", path)
    elif roll < 0.20:
        logging.warning("slow response (1.8s) on %s", path)
    else:
        logging.info("200 OK on %s", path)
    time.sleep(1)
