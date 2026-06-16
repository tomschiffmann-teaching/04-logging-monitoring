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

## 3. Orient yourself — how to read a trace
This section is just a tour so you know what you're looking at; the **graded
exercises start right after it**.

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

---

# Your exercises

These are the tasks to complete. They're mostly **investigation** — you read real
traces in Jaeger and figure out what happened — plus one small code change at the end.
Keep a scratch file (or paper) and **write down the short answer asked for in each
exercise**; that's your deliverable. Work on the live traffic that's already flowing.

> Tip: every exercise lives in the Jaeger UI at **http://localhost:16686**. The search
> form is on the left; results are a clickable list; clicking a trace opens its span
> tree; clicking a span opens its **Tags / attributes** and **Logs / Events**.

## Exercise 1 — Read one trace end to end
Open any normal (non-red) `frontend` trace and study it.

**Write down:**
1. How many **services** and how many **spans** are in this one request?
2. List the spans **in order** and which service each belongs to. Which span is the
   **parent** of all the others (the root)?
3. Click the `validate-cart` span — what is the value of its `cart.items` attribute?
   Then find a span whose attributes mention that same number of items.

> Goal: get comfortable reading a span tree as *one request's journey across services*,
> not a pile of disconnected log lines.

## Exercise 2 — Find the slow request
Most checkouts finish in ~0.3 s, but some take **1–2 s**. Find one without scanning by eye:
in the search form set **Min Duration** = `1s`, then **Find Traces**. Open a slow trace.

**Write down:**
1. Which **service** and which **span** ate the time? (Name the exact span.)
2. Roughly how long did that span take, and what fraction of the whole trace is it?
3. Open a *fast* trace and look at the same span — how does its duration compare?
   What does that tell you about *where* the slowness comes from?

> "Checkout is slow" is now a precise fact: *"the `card-network: authorize` span in
> backend took 1.8 s."* No cross-team guessing.

## Exercise 3 — Find the broken request
About 1 in 10 checkouts fail. Find them: in the **Tags** box type `error=true` and
**Find Traces** (failed traces also show a red ⊘ icon in the list). Open one and click
the span marked with the error.

**Write down:**
1. Which **span** in which **service** actually failed, and what is its status
   **message**?
2. The frontend's top-level `GET /checkout` span is *also* flagged as errored even
   though the real failure is deeper. Why is that useful rather than confusing?
3. From the *outside*, the customer just saw `payment-failed`. What does the trace tell
   you that the outside response did not?

## Exercise 4 — Two services, one trace (context propagation)
A request touches **two** separate containers, yet they show up in **one** trace. Prove
it. Open any trace and click the frontend's outgoing `GET` span, then the backend's
`GET /charge` span.

**Write down:**
1. Find the **Trace ID** (shown at the top of the trace view). Do the frontend spans
   and backend spans share the **same** Trace ID?
2. Read the top of `frontend/app.py` and `backend/app.py`. Which two lines make this
   automatic linking happen? (Hint: one *injects* context into the outgoing HTTP call,
   one *reads* it on the way in — search for `Instrumentor`.)

> The frontend stamps a `traceparent` header onto its HTTP call to the backend; the
> backend reads it and continues the same trace. That's *distributed* tracing.

## Exercise 5 — Let Jaeger draw your system
Click the **System Architecture** tab at the top of the Jaeger UI (give it some traffic
first).

**Write down:**
1. What graph does Jaeger draw, and what do the nodes and the arrow represent?
2. Nobody wrote this diagram by hand — where did Jaeger get it from? Why is this
   valuable once a real system has dozens of services?

## Exercise 6 — Add your own span (one small code change)
Now produce a little trace data yourself. Open `backend/app.py` — the tracing setup is
~10 lines of boilerplate, then spans are created with
`with tracer.start_as_current_span("name") as span:`.

1. In `charge()`, wrap a new step in its own span, e.g. `"send receipt email"`, with a
   `time.sleep(random.uniform(0.05, 0.1))` inside.
2. Add an attribute: `span.set_attribute("email.to", "customer@example.com")`.
3. Rebuild and restart: `docker compose up -d --build backend`.
4. Wait ~10 s for fresh traffic, then **Find Traces** again.

**Write down:** where does your new span appear in the tree, and does clicking it show
your `email.to` attribute?

---

## Optional / stretch tasks (for the fast finishers)
Done early? Pick any of these — they go deeper, in roughly increasing difficulty.
None are required to "pass" the exercise.

**A. Make the error span actually useful (small code change).**
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

**B. Nest a span inside a span (small code change).**
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

**C. Tune the chaos and watch it change (experiment).**
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
