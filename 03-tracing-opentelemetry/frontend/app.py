"""
The FRONTEND of a (tiny) shop. It receives /checkout requests and calls the
backend service to charge the card.

New concept — a TRACE:
- A LOG line tells you what ONE service did (Exercise 1).
- A METRIC tells you how the whole system trends over time (Exercise 2).
- A TRACE follows ONE request end-to-end THROUGH ALL services, as a tree of
  timed "spans". It answers: "where exactly did these 2 seconds go?"

OpenTelemetry (OTel) is the vendor-neutral standard for producing traces
(and metrics and logs too). We export them to Jaeger and look at them there.
"""

import os
import random
import threading
import time

import requests
from flask import Flask, jsonify

# --- OpenTelemetry setup (the one-time boilerplate every service needs) ---
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# "Who am I?" — this name is what you'll see in Jaeger's service dropdown.
provider = TracerProvider(resource=Resource.create({"service.name": "frontend"}))
# "Where do spans go?" — the exporter reads OTEL_EXPORTER_OTLP_ENDPOINT (compose file).
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)  # auto-span for every incoming request
RequestsInstrumentor().instrument()      # auto-span for every outgoing HTTP call
# ---------------------------------------------------------------------------

BACKEND = os.environ.get("BACKEND_URL", "http://backend:8000")


@app.route("/checkout")
def checkout():
    cart_items = random.randint(1, 5)

    # A custom span: our own named unit of work inside the request.
    with tracer.start_as_current_span("validate-cart") as span:
        span.set_attribute("cart.items", cart_items)
        time.sleep(random.uniform(0.01, 0.05))

    # Call the backend. The trace context travels along in an HTTP header
    # (traceparent), so the backend's spans land in the SAME trace.
    resp = requests.get(f"{BACKEND}/charge", params={"items": cart_items}, timeout=10)

    if resp.ok:
        return jsonify(status="ok", items=cart_items)
    return jsonify(status="payment-failed", items=cart_items), 502


def generate_traffic():
    """Simulate customers so traces show up without you doing anything."""
    import urllib.error
    import urllib.request  # NOT `requests`, so the simulator itself isn't traced

    time.sleep(3)  # let the servers finish starting
    while True:
        try:
            urllib.request.urlopen("http://localhost:8000/checkout", timeout=15)
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(random.uniform(1, 3))


if __name__ == "__main__":
    threading.Thread(target=generate_traffic, daemon=True).start()
    print("Frontend on :8000 (try /checkout)", flush=True)
    app.run(host="0.0.0.0", port=8000)
