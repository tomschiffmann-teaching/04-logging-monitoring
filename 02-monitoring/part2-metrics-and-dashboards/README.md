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

1. Left menu → **Dashboards** → **New** (top right) → **New dashboard**.
   You land on an empty dashboard that says *"Add a panel to visualize your data"*.
2. Click the **Panel** tile in the **Add** sidebar on the right (the little graph
   thumbnail with the big **+**). This opens the **Edit panel** view.
3. At the bottom, under **Queries**, the data source should already say
   **Prometheus** — leave it.
4. The query editor starts in **Builder** mode (dropdowns like *Select metric*).
   To paste a ready-made query, switch the toggle on the right of the query row
   from **Builder** to **Code** — now you get a text box.
5. Paste one of these into the code box and click **Run queries** to watch the
   panel draw:

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
6. Give the panel a title (right-hand pane → **Panel options → Title**), then click
   **Back to dashboard** (top left) — or **Save** (top right) to keep it.
7. Add a couple more panels the same way (**+ Add → Panel**). Set the time range
   (top-right clock, e.g. *Last 6 hours*) to **Last 15 minutes** and the
   auto-refresh dropdown next to **Refresh** to **5s**. When you're done
   arranging, click **Save**, then **Exit edit**.

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

## 6. (Optional) Get an email when it breaks
In step 5 *you* watched the graph. Now let Grafana watch it and email **you**.

**a) Give Grafana a mail account to send from (your own):**
```bash
cp .env.example .env              # then edit .env with your address + password
docker compose up -d grafana      # restart Grafana so it picks up the settings
```
For Gmail you need an **app password** (Google Account → Security →
2-Step Verification → App passwords) — your normal password won't work.
Any provider is fine; just set its SMTP host and credentials in `.env`.
> The `.env` file contains a real password — don't commit it to git.

**b) Tell Grafana where alerts should go:**
1. Left menu → **Alerting → Contact points** → edit **grafana-default-email**.
2. Put your own address in **Addresses** and click **Test** — you should get a
   test mail within seconds (check spam). If not, fix `.env` before continuing.
3. **Save contact point**.

**c) Create the alert rule ("the app is down"):**
1. **Alerting → Alert rules → New alert rule**, name it `App down`.
2. In the query (switch **Builder → Code** like before), enter:
   ```
   up{job="sample-app"}
   ```
   Prometheus sets this to `1` while it can scrape the app, `0` when it can't.
3. In the condition below, set: **WHEN last() OF A IS BELOW 1**.
4. Under evaluation, create a folder (e.g. `lab`) and an evaluation group with a
   **10s** interval, and set the **pending period** to **0s** (= fire immediately;
   in production you'd wait a minute or two to avoid flapping).
5. Pick **grafana-default-email** as the contact point and **Save rule and exit**.

**d) Break it and check your inbox:**
```bash
docker compose stop app           # alert goes Pending -> Firing
docker compose start app          # a 'Resolved' email follows
```
Give it 1–2 minutes — alert evaluation isn't instant. You can watch the state
change under **Alerting → Alert rules** while you wait.

> That email is the difference between *monitoring* and *staring at dashboards*:
> nobody watches graphs at 3 a.m. — the alert does.

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
