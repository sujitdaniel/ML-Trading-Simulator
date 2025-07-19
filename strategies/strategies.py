from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    """Abstract base class for all trading strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass


class MovingAverageCrossover(Strategy):
    """A simple moving average crossover strategy."""

    def __init__(self, short_window: int = 40, long_window: int = 100):
        self.short_window = short_window
        self.long_window = long_window

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0

        # Create short and long simple moving averages
        signals["short_mavg"] = (
            data["Close"]
            .rolling(window=self.short_window, min_periods=1, center=False)
            .mean()
        )
        signals["long_mavg"] = (
            data["Close"]
            .rolling(window=self.long_window, min_periods=1, center=False)
            .mean()
        )

        # Generate signal when short MA crosses above long MA
        signals["signal"][self.short_window :] = (
            signals["short_mavg"][self.short_window :]
            > signals["long_mavg"][self.short_window :]
        ).astype(float)

        # Generate trading orders (1 for buy, -1 for sell)
        signals["positions"] = signals["signal"].diff()
        return signals
