# backend/main.py
from fastapi import FastAPI
from strategies.engine import TradingEngine
from strategies.strategies import MovingAverageCrossover
from backtester.backtester import run_backtest
import pandas as pd
from typing import Dict, Any

app = FastAPI(
    title="Algorithmic Trading Platform API",
    description="API for backtesting and simulating trading strategies.",
    version="0.1.0",
)


@app.get("/health", summary="Health Check")
def health_check():
    """Check if the API is running."""
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "Welcome to ALGONEX"}


@app.get("/backtest/{ticker}", summary="Run a backtest for a given ticker")
def get_backtest(ticker):
    """
    Runs a backtest using the Moving Average Crossover strategy.
    """
    try:
        # 1. Initialize Strategy and Engine
        print(f"# Working on strategy for {ticker}")
        strategy = MovingAverageCrossover(short_window=50, long_window=200)
        engine = TradingEngine(strategy=strategy, ticker=f"{ticker.upper()}")

        # 2. Run the engine to get trades
        print("# Working on trades")
        trades = engine.run()
        
        # 3. Run the backtester on the trades
        print("# Working on backtest")
        performance_metrics = run_backtest(trades)

        return {
            "ticker": ticker,
            "strategy": "Moving Average Crossover",
            "performance": performance_metrics
        }
    except Exception as e:
        print(f"Error in backtest: {str(e)}")
        return {"error": str(e), "ticker": ticker}


@app.post("/backtest/{ticker}", summary="Run a backtest for a given ticker")
def post_backtest(ticker):
    """
    Runs a backtest using the Moving Average Crossover strategy.
    """
    try:
        # 1. Initialize Strategy and Engine
        print(f"# Working on strategy for {ticker}")
        strategy = MovingAverageCrossover(short_window=50, long_window=200)
        engine = TradingEngine(strategy=strategy, ticker=f"{ticker.upper()}")

        # 2. Run the engine to get trades
        print("# Working on trades")
        trades = engine.run()

        # 3. Run the backtester on the trades
        print("# Working on backtest")
        performance_metrics = run_backtest(trades)

        return {
            "ticker": ticker,
            "strategy": "Moving Average Crossover",
            "performance": performance_metrics
        }
    except Exception as e:
        print(f"Error in backtest: {str(e)}")
        return {"error": str(e), "ticker": ticker}

#   **Test:** Run `uvicorn main:app --reload`. Use a tool like Postman or `curl` to send a GET request to `http://127.0.0.1:8000/backtest/AAPL`. You should get a JSON response with performance metrics.
