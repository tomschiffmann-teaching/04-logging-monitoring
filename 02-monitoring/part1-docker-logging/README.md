# Part 1 — Docker container logging

**Goal:** understand where container logs go and how to read them like an operator.

## The key concept
Inside a container, a well-behaved app **does not write log files**. It just prints to
**stdout/stderr**, and the Docker engine captures that stream. You then read it with
`docker logs` / `docker compose logs`. (Our two services here do exactly that — see
`app.py` and `worker.py`: plain `logging` to the console.)

## Start it
```bash
docker compose up -d        # start both services in the background
docker compose ps           # confirm 'web' and 'worker' are running
```

## Core commands to practice
```bash
# 1. Show all logs from all services
docker compose logs

# 2. FOLLOW logs live (like tail -f). Ctrl+C to stop following (services keep running)
docker compose logs -f

# 3. Only ONE service
docker compose logs -f web
docker compose logs worker

# 4. Only the last N lines, then follow
docker compose logs --tail 20 -f

# 5. Only recent logs (time-based)
docker compose logs --since 30s
docker compose logs --since 2m web

# 6. Add timestamps from Docker itself
docker compose logs -t web
```

### Filtering for problems (where logging meets monitoring)
Find just the errors across everything:
```bash
docker compose logs | grep -i error
docker compose logs -f web | grep -i "500\|error"
```

> This `grep` is "manual monitoring." It works for one machine, but doesn't scale —
> which is exactly why Part 2 introduces real metrics + dashboards.

## Tasks
1. Start the stack. Follow the combined logs for ~30s. Spot the `WARNING` and `ERROR`
   lines that randomly appear.
2. Show logs from **only** `worker`. How often does a job fail?
3. Use `--since` and `--tail` to look at just the most recent activity.
4. Use `grep` to show only error lines from `web`.

## Log rotation (don't fill the disk!)
Look at the `logging:` block in `docker-compose.yml`:
```yaml
logging:
  driver: json-file
  options:
    max-size: "1m"     # rotate after each log file reaches 1 MB
    max-file: "3"      # keep at most 3 rotated files (3 MB total, then oldest deleted)
```
Without this, a chatty container can fill your disk over days. This is a real,
common production incident. Inspect the effective config:
```bash
docker inspect -f '{{json .HostConfig.LogConfig}}' $(docker compose ps -q web)
```

## Where are the raw logs on disk? (optional, peek behind the curtain)
The `json-file` driver stores them as JSON. On Linux:
`/var/lib/docker/containers/<container-id>/<container-id>-json.log`
On Docker Desktop (Mac/Windows) that path lives inside the Docker VM, so just use
`docker logs` — that's the whole point of the command.

## Clean up
```bash
docker compose down
```

When done → go to `../part2-metrics-and-dashboards/`.
