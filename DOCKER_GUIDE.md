# 🚀 Algonex Docker Guide

This guide will help you run the **Algonex** project (backend + frontend) using Docker and Docker Compose. You do **not** need to install Python, Node.js, or TensorFlow on your host—everything runs in containers!

---

## 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your machine
- Project files:
  - `Dockerfile.backend`
  - `Dockerfile.frontend`
  - `docker-compose.yml`
  - `.dockerignore`
  - `requirements.txt`
  - Your code folders (`api/`, `frontend/`, etc.)

---

## 2. Clean Up Your Host (Recommended)
Before building, remove any local frontend build artifacts:

```sh
rm -rf frontend/node_modules frontend/.next
```

---

## 3. Build the Docker Images

```sh
docker-compose build --no-cache
```

---

## 4. Start the Containers

```sh
docker-compose up
```

- **Backend (FastAPI):** [http://localhost:8000](http://localhost:8000)
- **Frontend (Next.js):** [http://localhost:3000](http://localhost:3000)

---

## 5. Stop the Containers

Press `Ctrl+C` in the terminal, then run:

```sh
docker-compose down
```

---

## 6. Development Workflow
- Code changes in `frontend/` or backend code are reflected live in the containers (thanks to the `volumes` setting in `docker-compose.yml`).
- To run a shell in a container:
  ```sh
  docker-compose exec backend bash
  docker-compose exec frontend sh
  ```
- If you change `requirements.txt` or `package.json`, always re-run `docker-compose build --no-cache`.

---

## 7. Troubleshooting
- **Native module errors (e.g., `lightningcss`):**
  - Make sure you did **not** copy `node_modules` from your host.
  - Clean up with `rm -rf frontend/node_modules frontend/.next` and rebuild.
- **Dependency errors:**
  - Check your `requirements.txt` for version conflicts (see project docs for recommended versions).
- **Port conflicts:**
  - Make sure ports 8000 (backend) and 3000 (frontend) are free on your host.

---

## 8. File Reference

| File                | Purpose                        |
|---------------------|-------------------------------|
| Dockerfile.backend  | Backend (Python 3.11 + FastAPI)|
| Dockerfile.frontend | Frontend (Node.js + Next.js)   |
| docker-compose.yml  | Orchestrates both services     |
| .dockerignore       | Prevents copying build artifacts|

---

## 9. Updating Dependencies
- If you update `requirements.txt` or `package.json`, always rebuild:
  ```sh
  docker-compose build --no-cache
  ```

---

## 10. Need Help?
If you hit any issues, check the logs or open a shell in the container for debugging. You can also ask for help in the project community!

---

Happy hacking! 🎉 