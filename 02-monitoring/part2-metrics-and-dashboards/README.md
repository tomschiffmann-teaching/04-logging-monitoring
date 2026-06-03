# Part 2 — Metrics + Dashboards (Prometheus + Grafana)

**Goal:** stand up a real monitoring stack with Docker Compose and watch a system's
health on a live graph.

## The stack (3 containers)
```
  ┌─────────┐   scrapes /metrics    ┌────────────┐   queries    ┌─────────┐
  │   app   │◀──────every 5s────────│ Prometheus │◀─────────────│ Grafana │
  │ :8000   │                       │   :9090    │              │  :3000  │
  └─────────┘                       └────────────┘              └─────────┘
   exposes numbers                  stores time series          draws dashboards
```
- **app** — simulates work and exposes metrics (a Counter, a Gauge, a Histogram). See `app/app.py`.
- **Prometheus** — every 5s it reads `app:8000/metrics` and stores the numbers over time.
- **Grafana** — connects to Prometheus and draws graphs. Data source is auto-configured.

## 1. Start everything
```bash
docker compose up -d --build      # --build because the app has a Dockerfile
docker compose ps                 # app, prometheus, grafana should be 'running'
```

## 2. See the raw metrics (what the app exposes)
```bash
curl http://localhost:8000/metrics
```
Look for our metrics:
- `app_requests_total{status="ok"}` and `...{status="error"}`
- `app_sensor_temperature_celsius`
- `app_request_latency_seconds_bucket` (histogram buckets)

> These are just text numbers. Prometheus' job is to read them repeatedly and remember
> the history so you can graph *change over time*.

## 3. Check Prometheus is scraping
Open **http://localhost:9090** → top menu **Status → Targets**.
You should see `sample-app` as **UP** (green). If it's down, the app isn't reachable.

Try a query in the Prometheus UI (the "Graph" tab), paste:
```
app_sensor_temperature_celsius
```
and switch to the **Graph** tab. That's the temperature wiggling over time.

## 4. Build a dashboard in Grafana
Open **http://localhost:3000** (you're logged in automatically as Admin).

1. Left menu → **Dashboards → New → New dashboard → Add visualization**.
2. Pick the **Prometheus** data source (already there).
3. In the query box, paste one of these and watch the panel draw:

   **Request rate (requests per second), split by status:**
   ```
   rate(app_requests_total[1m])
   ```
   **Error rate only:**
   ```
   rate(app_requests_total{status="error"}[1m])
   ```
   **Live sensor temperature:**
   ```
   app_sensor_temperature_celsius
   ```
   **95th-percentile latency (95% of requests are faster than this):**
   ```
   histogram_quantile(0.95, rate(app_request_latency_seconds_bucket[1m]))
   ```
4. Give the panel a title, click **Apply**. Add a couple more panels. Set the
   time range (top-right) to **Last 15 minutes** and auto-refresh to **5s**.

🎉 You now have a live dashboard that updates as the app runs.

## 5. Make it react (see monitoring "catch" a problem)
Watch your error-rate panel, then stop the app and bring it back:
```bash
docker compose stop app          # app stops exposing metrics
# In Prometheus → Status → Targets, 'sample-app' goes DOWN (red).
docker compose start app         # it recovers; graphs resume
```
This is the core monitoring loop: **something changes → the metric moves → you see it
(and in production, an alert fires).**

## Logs vs metrics — the lesson
- In Part 1 you `grep`-ed logs for "error". That's reactive and per-machine.
- Here, `rate(app_requests_total{status="error"}[1m])` gives you a **number that trends**,
  across any number of machines, that you can graph and **alert on automatically**.

## Clean up
```bash
docker compose down
```

## Troubleshooting
- `app` won't build → check Docker is running: `docker info`.
- Target DOWN in Prometheus → make sure the service name in `prometheus/prometheus.yml`
  (`app:8000`) matches the compose service name (`app`).
- Grafana shows "No data" → wait ~30s for data to accumulate; set time range to
  *Last 15 minutes*; confirm the data source is **Prometheus**.
