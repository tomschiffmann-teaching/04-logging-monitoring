"""
A second fake service: a background worker processing jobs.

Having TWO services lets you practice reading logs from a specific service
vs. all services at once.
"""

import logging
import random
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | worker | %(message)s",
)

logging.info("worker started, waiting for jobs")

job_id = 0
while True:
    job_id += 1
    logging.info("processing job #%d", job_id)
    time.sleep(2)
    if random.random() < 0.10:
        logging.error("job #%d FAILED (timeout talking to database)", job_id)
    else:
        logging.info("job #%d done", job_id)
