# ML Trading Simulator Frontend-Backend Guide

## Overview

This guide explains how the Next.js frontend and FastAPI backend work together for strategy configuration and backtesting.

## Architecture

```text
Frontend (Next.js, port 3000)
        |
        | HTTP/JSON
        v
Backend (FastAPI, port 8000)
        |
        v
Strategy builder + trading engine + data fetcher
```

## How Frontend and Backend Communicate

- Frontend sends JSON requests to backend endpoints.
- Backend validates request payloads with Pydantic models.
- Backend builds indicator, ML, or hybrid strategies and runs the backtest.
- Backend returns performance metrics and trade history for frontend display.

For Docker:

- Frontend container talks to backend via `http://backend:8000`.

For local development:

- Frontend uses a localhost backend URL (commonly `http://localhost:8000`).

## Run Locally

### 1) Start backend

```bash
python api/main.py
```

### 2) Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 3) Optional integration check

```bash
python test_frontend_backend.py
```

## Core API Endpoints

- `GET /health` - service health.
- `GET /indicators` - available indicator definitions and categories.
- `GET /available-tickers` - currently available ticker symbols.
- `POST /backtest` - run configurable backtest (`strategy=ma|ml|hybrid`).

Docs UI:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

## Example Backtest Request

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
        "weight": 0.6,
        "parameters": {
          "period": 14,
          "overbought": 70,
          "oversold": 30
        }
      },
      {
        "id": "macd",
        "name": "MACD",
        "weight": 0.4,
        "parameters": {
          "fast_period": 12,
          "slow_period": 26,
          "signal_period": 9
        }
      }
    ]
  }'
```

## Strategy Modes Supported by Backend

- `ma`: indicator-based strategy from 1-3 selected indicators.
- `ml`: ML-only strategy (no indicators required).
- `hybrid`: combines indicator signals with ML signals (`ml_weight` required).

Available ML model IDs in backend:

- `logistic`
- `random_forest`
- `xgboost`
- `gradient_boosting`
- `svm`
- `knn`
- `lstm`

## Indicator Organization (20 total)

- Trend Following: `ma`, `macd`, `ema`, `sar`, `ppo`, `adx`
- Momentum: `rsi`, `stochastic`, `williams_r`, `cmo`
- Volatility: `bollinger`, `atr`, `std`, `rvi`
- Volume: `mfi`, `obv`, `vwap`
- Support/Resistance: `ibs`, `fibonacci`
- Mean Reversion: `mean_reversion`

## Troubleshooting

1. Backend connection issues: verify backend is running on port `8000`.
2. CORS issues: verify allowed origins in `api/main.py`.
3. Invalid indicator payload: use IDs from `/indicators`.
4. Date validation errors: use `YYYY-MM-DD` and start date before end date.