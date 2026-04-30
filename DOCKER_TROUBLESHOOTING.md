# Docker Troubleshooting Guide

Use this guide when Dockerized frontend/backend integration is not working as expected in ML Trading Simulator.

## Baseline Run Commands

```bash
docker compose build --no-cache
docker compose up
```

Legacy equivalent:

```bash
docker-compose build --no-cache
docker-compose up
```

## Confirm Service Health First

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

Expected access points:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Backend health endpoint: `http://localhost:8000/health`

## Common Issues and Fixes

### 1) "Failed to fetch" from frontend

Likely cause: frontend cannot reach backend container.

Checks:

- Confirm both services are up: `docker compose ps`
- Confirm backend is reachable from host: `http://localhost:8000/health`
- Confirm compose env is set to `NEXT_PUBLIC_API_URL=http://backend:8000`

Fix:

- Restart stack:

```bash
docker compose down
docker compose up --build
```

### 2) Port 3000 or 8000 already in use

Likely cause: another local process already binds these ports.

Checks and fix (macOS/Linux):

```bash
lsof -i :3000
lsof -i :8000
```

Stop or reconfigure conflicting processes, then restart compose.

### 3) CORS-related browser errors

Likely cause: request origin/API URL mismatch.

Checks:

- Frontend in Docker should call `http://backend:8000` (internal network).
- Browser accesses frontend at `http://localhost:3000`.
- Backend CORS list in `api/main.py` includes local dev origins.

### 4) Build failures

Likely cause: stale cache, dependency mismatch, or interrupted install.

Fix:

```bash
docker compose down
docker compose build --no-cache
docker compose up
```

You can also build services separately for clearer errors:

```bash
docker build -f Dockerfile.backend .
docker build -f frontend/Dockerfile ./frontend
```

### 5) Frontend native/dependency module issues

Likely cause: stale host artifacts mixed with container installs.

Fix:

```bash
rm -rf frontend/node_modules frontend/.next
docker compose build --no-cache
```

## Frontend-Backend Connection Model

- Host/browser -> Frontend: `http://localhost:3000`
- Host/browser -> Backend: `http://localhost:8000`
- Frontend container -> Backend container: `http://backend:8000`

If this mapping changes, update both `docker-compose.yml` and frontend API configuration accordingly.

## Quick Troubleshooting Loop

1. `docker compose ps`
2. `docker compose logs -f backend`
3. `docker compose logs -f frontend`
4. Hit `http://localhost:8000/health`
5. Reload `http://localhost:3000`
