# Exercise 2 — Monitoring

**Logging** answers *"what happened?"* (a stream of events).
**Monitoring** answers *"is the system healthy right now, and is it getting worse?"*
(numbers over time + alerts).

You already know Docker & Docker Compose, so we build on that.

> ⚠️ Before starting either part: **open Docker Desktop and make sure it's running**
> (whale icon in the menu bar). All terminal commands you need are in **`../SETUP.md`** (section 5).

Two parts:

1. **`part1-docker-logging/`** — Where do container logs go, and how do you read,
   follow, filter, and rotate them? This is the bridge from Exercise 1 (app logging)
   to operations (container logging).

2. **`part2-metrics-and-dashboards/`** — Run a real monitoring stack with Docker Compose:
   a sample app that exposes **metrics**, **Prometheus** that collects them, and
   **Grafana** that draws live **dashboards**. You'll build a graph and "watch" the system.

## The 3 pillars of observability (good mental model)
| Pillar | Question | Tool tonight |
|--------|----------|--------------|
| **Logs** | What happened, in detail? | Python logging, `docker logs` |
| **Metrics** | How much / how many / how fast, over time? | Prometheus + Grafana |
| **Traces** | Where did one request spend its time? | (not covered tonight) |

Start with `part1-docker-logging/`.
