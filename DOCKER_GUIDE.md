# ML Trading Simulator Docker Guide

This guide explains how to run the backend and frontend together with Docker Compose for ML Trading Simulator.

## Prerequisites

- Docker Desktop installed and running.
- Docker Compose support (`docker compose` or legacy `docker-compose` command).
- Project files present:
  - `docker-compose.yml`
  - `Dockerfile.backend`
  - `frontend/Dockerfile` (used by compose for the frontend build context)
  - `requirements.txt`
  - `frontend/package.json`

## Ports and Service Layout

- Frontend container: port `3000` -> host `http://localhost:3000`
- Backend container: port `8000` -> host `http://localhost:8000`
- Internal container-to-container API URL: `http://backend:8000`

`docker-compose.yml` sets `NEXT_PUBLIC_API_URL=http://backend:8000` for the frontend service, so the frontend talks to the backend over the Docker network.

## Build Images

From the repository root:

```bash
docker compose build --no-cache
```

If your environment uses the legacy command, replace `docker compose` with `docker-compose`.

## Run Containers

```bash
docker compose up
```

Use detached mode if preferred:

```bash
docker compose up -d
```

## Stop Containers

```bash
docker compose down
```

## Common Docker Commands

```bash
# Show running services
docker compose ps

# Stream logs from all services
docker compose logs -f

# Logs for one service
docker compose logs -f backend
docker compose logs -f frontend

# Open shell in containers
docker compose exec backend bash
docker compose exec frontend sh
```

## Common Errors

### Frontend cannot reach backend ("Failed to fetch")

- Confirm both services are running: `docker compose ps`
- Check backend health endpoint: `http://localhost:8000/health`
- Verify frontend env var includes `NEXT_PUBLIC_API_URL=http://backend:8000`

### Port conflict on 3000 or 8000

- Stop conflicting local services, then rerun compose.
- Bring compose stack down before restarting: `docker compose down`

### Build issues after dependency changes

- Rebuild after updates to `requirements.txt` or `frontend/package.json`:

```bash
docker compose build --no-cache
```

### Frontend dependency/native module issues

- Remove local frontend build artifacts and rebuild:

```bash
rm -rf frontend/node_modules frontend/.next
docker compose build --no-cache
```

## Troubleshooting Checklist

1. Docker Desktop is running.
2. `docker compose ps` shows both `backend` and `frontend`.
3. Backend is reachable on `http://localhost:8000/health`.
4. Frontend is reachable on `http://localhost:3000`.
5. Logs show no repeated startup crashes.