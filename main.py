# backend/main.py
from fastapi import FastAPI, HTTPException
from strategies.engine import TradingEngine
from strategies.strategies import MovingAverageCrossover
from backtester.backtester import run_backtest
from data.fetch_data import get_stock_data
import pandas as pd
from typing import Dict, Any
from datetime import datetime, timedelta

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

@app.get("/fetch-data/{ticker}", summary="Fetch and download stock data for a given ticker")
def fetch_stock_data(ticker: str, start_date: str = None, end_date: str = None, interval: str = "1d"):
    """
    Fetches and downloads stock data for a given ticker.
    If no dates are provided, defaults to last 1 year of data.
    """
    try:
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        print(f"Fetching data for {ticker} from {start_date} to {end_date}")
        
        # Fetch the data
        df = get_stock_data(ticker.upper(), start_date, end_date, interval)
        
        return {
            "ticker": ticker.upper(),
            "start_date": start_date,
            "end_date": end_date,
            "interval": interval,
            "data_points": len(df),
            "message": f"Successfully downloaded {len(df)} data points for {ticker.upper()}",
            "file_path": f"data/raw/{ticker.upper()}.csv"
        }
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch data for {ticker}: {str(e)}")


#   **Test:** Run `uvicorn main:app --reload`. 
#   Use a tool like Postman or `curl` to send a GET request to `http://127.0.0.1:8000/backtest/AAPL`. 
#   You should get a JSON response with performance metrics.
