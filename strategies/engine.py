# backend/core/engine.py
import pandas as pd
from .strategies import Strategy


class TradingEngine:
    def __init__(self, strategy: Strategy, ticker: str, data_path: str = "./data/raw"):
        self.strategy = strategy
        self.ticker = ticker
        self.data = self._load_data(f"{data_path}/{ticker}.csv")
        self.trades = []

    def _load_data(self, filepath: str) -> pd.DataFrame:
        # Read the CSV file, skipping the first 3 header rows
        df = pd.read_csv(filepath, skiprows=3, header=None, index_col=0, parse_dates=True)
        df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        return df

    def run(self):
        """Runs the strategy and generates a log of trades."""
        signals = self.strategy.generate_signals(self.data)
        for i in range(len(signals)):
            if signals["positions"].iloc[i] == 1.0:  # Buy signal
                self.trades.append(("BUY", self.data.index[i], self.data["Close"].iloc[i]))
            elif signals["positions"].iloc[i] == -1.0:  # Sell signal
                self.trades.append(("SELL", self.data.index[i], self.data["Close"].iloc[i]))
        return self.trades
