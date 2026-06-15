"""
The BACKEND ("payment service"). The frontend calls /charge here.

It has two deliberate problems for you to FIND IN THE TRACES:
  * sometimes the card network is SLOW   -> a 1-2 second span
  * sometimes the charge FAILS           -> an error span (red in Jaeger)
"""

import random
import time

from flask import Flask, jsonify, request

# --- OpenTelemetry setup (same boilerplate as the frontend) ---------------
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import StatusCode

provider = TracerProvider(resource=Resource.create({"service.name": "backend"}))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
# ---------------------------------------------------------------------------


@app.route("/charge")
def charge():
    items = int(request.args.get("items", 1))

    with tracer.start_as_current_span("db: load customer") as span:
        span.set_attribute("db.rows", items)
        time.sleep(random.uniform(0.02, 0.08))

    with tracer.start_as_current_span("card-network: authorize") as span:
        span.set_attribute("amount.eur", round(items * 9.99, 2))

        if random.random() < 0.15:
            # The SLOW path — in Jaeger, sort traces by duration to find it.
            time.sleep(random.uniform(1.0, 2.0))
        else:
            time.sleep(random.uniform(0.05, 0.3))

        if random.random() < 0.10:
            # The FAILURE — Jaeger marks the span (and trace) with an error.
            span.set_status(StatusCode.ERROR, "card declined")
            return jsonify(error="card declined"), 500

    return jsonify(status="charged", items=items)


if __name__ == "__main__":
    print("Backend on :8000 (/charge)", flush=True)
    app.run(host="0.0.0.0", port=8000)
