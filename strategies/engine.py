# backend/core/engine.py
import pandas as pd
from .strategies import Strategy


class TradingEngine:
    def __init__(self, strategy: Strategy, ticker: str, data_path: str = "./data"):
        self.strategy = strategy
        self.ticker = ticker
        self.data = self._load_data(f"{data_path}/{ticker}.csv")
        self.trades = []

    def _load_data(self, filepath: str) -> pd.DataFrame:
        return pd.read_csv(filepath, index_col="Date", parse_dates=True)

    def run(self):
        """Runs the strategy and generates a log of trades."""
        signals = self.strategy.generate_signals(self.data)
        for i in range(len(signals)):
            if signals["positions"][i] == 1.0:  # Buy signal
                self.trades.append(("BUY", self.data.index[i], self.data["Close"][i]))
            elif signals["positions"][i] == -1.0:  # Sell signal
                self.trades.append(("SELL", self.data.index[i], self.data["Close"][i]))
        return self.trades
