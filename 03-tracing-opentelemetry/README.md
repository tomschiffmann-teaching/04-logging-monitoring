# Exercise 3 — Tracing with OpenTelemetry + Jaeger

**Goal:** follow ONE request as it travels **through multiple services**, and use the
trace to find out *where* time is lost and *where* an error happened.

## Why a third tool?
You already have two views of a system:
- **Logs** (Exercise 1): one line per event, per service. Great detail, but stitching
  a single user's journey across services together by hand is painful.
- **Metrics** (Exercise 2): trends and alerts ("error rate is rising!"), but no detail
  about any *single* request.

A **trace** is the missing piece: one request, end-to-end, drawn as a tree of timed
**spans** across every service it touched. **OpenTelemetry (OTel)** is the
vendor-neutral standard for producing this data; **Jaeger** is a tool to view it.

## The stack (3 containers)
```
   /checkout   ┌──────────┐  /charge   ┌─────────┐
  ───────────▶ │ frontend │───────────▶│ backend │     both send spans
               │  :8001   │            │ (no port│         │ (OTLP)
               └──────────┘            │ exposed)│         ▼
                                       └─────────┘    ┌────────┐
                                                      │ Jaeger │ UI :16686
                                                      └────────┘
```
- **frontend** — receives `/checkout`, validates the cart, calls the backend.
  It also simulates customers, so traffic flows by itself.
- **backend** — the "payment service". Sometimes **slow**, sometimes **fails** (on purpose).
- **jaeger** — collects the spans and draws them as trace timelines.

## 1. Start everything
```bash
docker compose up -d --build
docker compose ps          # frontend, backend, jaeger should be 'running'
```

## 2. Make a request yourself
```bash
curl http://localhost:8001/checkout
```
You get `{"status": "ok", ...}` — or occasionally `payment-failed`. From the outside
you can't tell **why** it failed or why it was slow. Logs would show you two
disconnected lines in two services. Let's see the trace instead.

## 3. Look at a trace in Jaeger
Open **http://localhost:16686**.
1. In the **Service** dropdown (left), pick **frontend** → **Find Traces**.
2. Click any trace. You'll see a timeline like:
   ```
   frontend  GET /checkout            ━━━━━━━━━━━━━━━━━━━━  240ms
   frontend    validate-cart          ━━                     30ms
   frontend    GET                      ━━━━━━━━━━━━━━━━    200ms   (the HTTP call)
   backend       GET /charge            ━━━━━━━━━━━━━━      195ms
   backend         db: load customer    ━━                   40ms
   backend         card-network: authorize ━━━━━━━━━        150ms
   ```
   One request, **two services, one picture**. Click a span to see its
   **attributes** (e.g. `cart.items`, `amount.eur`).

## 4. Find the slow one and the broken one
- **Slow:** in the search results, look at the duration dots/list — some traces take
  **1–2 s** instead of ~0.3 s. Open one: which span ate the time?
  (You should be able to name the guilty service AND the guilty step.)
- **Broken:** search again with **Tags** = `error=true` (or just spot the red icons).
  Open one and click the failing span — the status says **card declined**.

> That's the everyday superpower of tracing: "checkout is slow" stops being a
> debate between teams and becomes *"the card-network call in backend takes 1.8s"*.

## 5. Add your own span (small task)
Open `backend/app.py` — the tracing setup is ~10 lines of boilerplate, then spans are
created with `with tracer.start_as_current_span("name") as span:`.

1. In `charge()`, wrap a new step in its own span, e.g. `"send receipt email"`
   with a `time.sleep(random.uniform(0.05, 0.1))` inside.
2. Add an attribute: `span.set_attribute("email.to", "customer@example.com")`.
3. Rebuild and restart: `docker compose up -d --build backend`.
4. Find a fresh trace in Jaeger — your span should appear in the tree.

## Optional / stretch tasks (for the fast finishers)
Done early? Pick any of these — they go deeper, in roughly increasing difficulty.
None are required to "pass" the exercise.

**A. Hunt traces like a pro (no code).**
- In the search form, set **Min Duration** = `1s` and **Find Traces** — now you get
  *only* the slow ones, no eyeballing.
- In the **Tags** box try `error=true`, then `http.status_code=500`.
- Open the **System Architecture** tab (top of the page). After some traffic Jaeger
  draws a `frontend → backend` dependency graph — built entirely from the spans,
  which nobody declared by hand. That's a map of your system, for free.

**B. Make the error span actually useful (small code change).**
Right now the failing span only says "card declined". Attach the real exception so
Jaeger shows it as an event. In `backend/app.py`, change the failure branch to:
```python
        if random.random() < 0.10:
            err = RuntimeError("card declined")
            span.record_exception(err)        # <-- adds an exception event to the span
            span.set_status(StatusCode.ERROR, "card declined")
            return jsonify(error="card declined"), 500
```
`docker compose up -d --build backend`, find a failed trace, click the red span →
the **Logs/Events** now contain an `exception` with its type and message.

**C. Nest a span inside a span (small code change).**
Spans form a *tree* — a span can have children. Inside `card-network: authorize`,
wrap a sub-step in its own span:
```python
    with tracer.start_as_current_span("card-network: authorize") as span:
        span.set_attribute("amount.eur", round(items * 9.99, 2))

        with tracer.start_as_current_span("fraud-check"):   # <-- child of authorize
            time.sleep(random.uniform(0.01, 0.03))
        ...
```
Rebuild the backend. In Jaeger, `fraud-check` now appears **indented under**
`card-network: authorize` — the tree got one level deeper.

**D. Tune the chaos and watch it change (experiment).**
The backend's "slow" and "fail" rates are just two numbers. Bump the slow chance from
`0.15` to `0.8` (or the failure chance from `0.10` to `0.5`), rebuild the backend, and
watch almost every trace turn slow / red in Jaeger. This is the same idea as the
metrics exercise: *change a behaviour → see it in the data.* **Put the numbers back**
when you're done so the next person gets the realistic mix.

## The lesson — three pillars, one standard
| | Question it answers | Exercise |
|---|---|---|
| **Logs** | What happened in this service? | 1 |
| **Metrics** | How is the system trending? Alert me! | 2 |
| **Traces** | Where in the chain did THIS request spend its time / fail? | 3 |

OpenTelemetry can produce **all three** with one SDK and ship them anywhere
(Jaeger, Prometheus, Grafana, Datadog, ...) — that's why it has become *the*
industry standard for instrumenting services.

## Clean up
```bash
docker compose down
```

## Troubleshooting
- **Port already in use** → Exercise 2 still running? `docker compose down` in
  `02-monitoring/part2-metrics-and-dashboards` first.
- **No traces in Jaeger** → wait ~10 s (traffic starts after a short delay and spans
  are sent in batches), then click **Find Traces** again. Check the services are up:
  `docker compose ps` and `docker compose logs frontend`.
- **Only `frontend` in the Service dropdown** → make a few requests
  (`curl http://localhost:8001/checkout`) and refresh; the dropdown fills as spans arrive.
