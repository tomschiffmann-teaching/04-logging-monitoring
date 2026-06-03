"""
A sample app that exposes METRICS for Prometheus to collect.

Difference from logging:
- A LOG is one line per event ("200 OK on /cart").
- A METRIC is a NUMBER that Prometheus reads over and over, building a time series
  it can graph and alert on ("requests_total = 5821 and rising").

This app does NOT serve real traffic — it simulates work in a loop and updates
3 classic metric types:
  * Counter   -> only goes up   (total requests)
  * Gauge     -> goes up & down (current temperature)
  * Histogram -> distribution   (request latency buckets)

It publishes them at http://<host>:8000/metrics in Prometheus' text format.
"""

import random
import time

from prometheus_client import Counter, Gauge, Histogram, start_http_server

# --- Define the metrics -------------------------------------------------
# Counter with a label so we can split OK vs error.
REQUESTS = Counter(
    "app_requests_total", "Total requests processed", ["status"]
)
# Gauge: a value that goes up and down.
TEMPERATURE = Gauge(
    "app_sensor_temperature_celsius", "Simulated sensor temperature"
)
# Histogram: buckets of how long requests took.
LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds"
)


def do_one_request():
    # Simulate the request taking some time, measured into the histogram.
    with LATENCY.time():
        time.sleep(random.uniform(0.01, 0.4))

    # ~10% of requests "fail".
    if random.random() < 0.10:
        REQUESTS.labels(status="error").inc()
    else:
        REQUESTS.labels(status="ok").inc()

    # Update the "sensor" reading.
    TEMPERATURE.set(round(20 + random.uniform(-5, 15), 2))


if __name__ == "__main__":
    # Expose metrics at http://0.0.0.0:8000/metrics
    start_http_server(8000)
    print("Serving metrics on :8000/metrics", flush=True)
    while True:
        do_one_request()
        time.sleep(random.uniform(0.1, 0.5))
