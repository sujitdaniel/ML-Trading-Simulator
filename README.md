# ML Trading Simulator

ML Trading Simulator is a machine learning and indicator-driven trading simulator for experimenting with strategy ideas on historical market data. The project combines a FastAPI backend, a Next.js frontend, and a Python strategy/backtesting engine so you can configure strategies, run backtests, and review trade and performance outputs.

## Overview

This repository focuses on simulation and evaluation workflows:

- Build strategies from technical indicators (single, dual, or triple combinations).
- Run pure ML and hybrid ML + indicator backtests.
- Fetch historical ticker data for requested date ranges.
- Compare outputs through API responses and frontend visual feedback.

This is not presented as a production trading system or a guarantee of trading profitability.

## Key Features

- FastAPI backend endpoints for health checks, indicators, ticker discovery, and backtesting.
- Strategy engine supporting indicator-based, ML-based, and hybrid workflows.
- Multiple ML signal generators, including logistic regression and tree-based models.
- Next.js frontend for selecting indicators, date ranges, and strategy inputs.
- Docker setup for running backend and frontend together.
- Test scripts for API connectivity, frontend/backend integration, and indicator behavior.

## Tech Stack

- Backend: Python, FastAPI, Uvicorn, Pydantic
- Data + Analysis: pandas, numpy, yfinance
- ML: scikit-learn, XGBoost, TensorFlow
- Frontend: Next.js, React, TypeScript, Tailwind CSS
- Tooling: Docker, Docker Compose, pytest

## Documentation Map

- `FRONTEND_BACKEND_GUIDE.md` - frontend/backend API flow and integration usage.
- `STRATEGY_USAGE.md` - strategy builder patterns and backtest request examples.
- `DOCKER_GUIDE.md` - Docker setup, run commands, ports, and common issues.
- `DOCKER_TROUBLESHOOTING.md` - focused troubleshooting workflow for containerized runs.

## Project Structure

```text
ML-Trading-Simulator/
├── api/                    # FastAPI service and endpoints
├── strategies/             # Strategy classes and strategy builder
├── backtester/             # Backtesting utilities
├── ml/                     # ML signal generation models
├── data/                   # Data fetching logic and CSV storage
├── frontend/               # Next.js frontend app
├── test_indicators/        # Indicator-focused test scripts
├── docker-compose.yml      # Multi-service local container setup
├── Dockerfile.backend      # Backend container image
├── Dockerfile.frontend     # Frontend container image
└── *.md / test_*.py        # Guides and integration/API checks
```

## Setup (Local)

### 1) Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python api/main.py
```

Backend default URL: `http://127.0.0.1:8000`

### 2) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend default URL: `http://localhost:3000`

## Run With Docker

```bash
docker-compose build --no-cache
docker-compose up
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Internal frontend-to-backend URL in Docker: `http://backend:8000`

## Running Backend and Frontend Separately

Run the backend from repo root:

```bash
python api/main.py
```

Run the frontend from `frontend/`:

```bash
npm run dev
```

For local (non-Docker) frontend usage, configure API access to the backend host (typically `http://localhost:8000`).

## Testing

Available scripts in this repository include:

```bash
python test_api_connection.py
python test_frontend_backend.py
pytest test_indicators
python test_indicators/quick_test.py
```

## Example Usage

### API example: run a backtest

```bash
curl -X POST "http://127.0.0.1:8000/backtest?strategy=ma" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 10000,
    "indicators": [
      {
        "id": "rsi",
        "name": "Relative Strength Index",
        "weight": 1.0,
        "parameters": {
          "period": 14,
          "overbought": 70,
          "oversold": 30
        }
      }
    ]
  }'
```

### Python example script

```bash
python example_usage.py
```

## Future Improvements

- Expand automated test coverage for API edge cases and strategy validation.
- Add reproducible benchmark datasets for consistent backtest comparisons.
- Improve model evaluation reporting and experiment tracking.
- Add deployment templates for staging environments.
- Improve UI-level observability and error surfacing for failed runs.
