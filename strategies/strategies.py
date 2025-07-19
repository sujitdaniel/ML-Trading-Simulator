from abc import ABC, abstractmethod
import pandas as pd
from typing import List, Dict, Tuple, Optional
import numpy as np


class Strategy(ABC):
    """Abstract base class for all trading strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        pass


class Indicator(ABC):
    """Abstract base class for all indicators."""
    
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate the indicator values."""
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate buy/sell signals based on the indicator."""
        pass


class MovingAverageIndicator(Indicator):
    """Moving Average Crossover indicator."""
    
    def __init__(self, short_window: int = 40, long_window: int = 100):
        self.short_window = short_window
        self.long_window = long_window
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        short_mavg = data["Close"].rolling(window=self.short_window, min_periods=1, center=False).mean()
        long_mavg = data["Close"].rolling(window=self.long_window, min_periods=1, center=False).mean()
        return short_mavg - long_mavg  # Return the difference
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        ma_diff = self.calculate(data)
        signals[self.short_window:] = (ma_diff[self.short_window:] > 0).astype(float)
        return signals


class RSIIndicator(Indicator):
    """RSI indicator."""
    
    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        
        avg_gain = gain.rolling(window=self.period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=1).mean()
        
        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        rsi = self.calculate(data)
        
        signals.loc[rsi < self.oversold] = 1.0  # Buy
        signals.loc[rsi > self.overbought] = -1.0  # Sell
        return signals


class BollingerBandsIndicator(Indicator):
    """Bollinger Bands indicator."""
    
    def __init__(self, window: int = 20, num_std: float = 2):
        self.window = window
        self.num_std = num_std
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rolling_mean = data["Close"].rolling(window=self.window, min_periods=1).mean()
        rolling_std = data["Close"].rolling(window=self.window, min_periods=1).std()
        
        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)
        
        # Return normalized position within bands (0 = at lower band, 1 = at upper band)
        return (data["Close"] - lower_band) / (upper_band - lower_band + 1e-10)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        bb_position = self.calculate(data)
        
        # Buy when price is near lower band, sell when near upper band
        signals.loc[bb_position < 0.2] = 1.0  # Near lower band
        signals.loc[bb_position > 0.8] = -1.0  # Near upper band
        return signals


class MeanReversionIndicator(Indicator):
    """Mean Reversion indicator using z-score."""
    
    def __init__(self, window: int = 20, entry_z: float = 1.0, exit_z: float = 0.0):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        rolling_mean = data["Close"].rolling(window=self.window, min_periods=1).mean()
        rolling_std = data["Close"].rolling(window=self.window, min_periods=1).std()
        z_score = (data["Close"] - rolling_mean) / (rolling_std + 1e-10)
        return z_score
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        z_score = self.calculate(data)
        
        # Buy when z-score < -entry_z, sell when z-score > entry_z
        signals.loc[z_score < -self.entry_z] = 1.0
        signals.loc[z_score > self.entry_z] = -1.0
        return signals


class CompositeStrategy(Strategy):
    """A strategy that combines multiple indicators with configurable weights."""
    
    def __init__(self, indicators: List[Tuple[Indicator, float]], 
                 signal_threshold: float = 0.5,
                 require_confirmation: bool = True):
        """
        Initialize composite strategy.
        
        Args:
            indicators: List of (indicator, weight) tuples. Max 3 indicators allowed.
            signal_threshold: Minimum weighted signal to trigger a trade (0.0 to 1.0)
            require_confirmation: If True, requires at least 2 indicators to agree
        """
        if len(indicators) > 3:
            raise ValueError("Maximum 3 indicators allowed")
        if len(indicators) < 1:
            raise ValueError("At least 1 indicator required")
        
        self.indicators = indicators
        self.signal_threshold = signal_threshold
        self.require_confirmation = require_confirmation
        
        # Normalize weights
        total_weight = sum(weight for _, weight in indicators)
        self.normalized_indicators = [(ind, weight/total_weight) for ind, weight in indicators]
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0
        
        # Calculate individual indicator signals
        indicator_signals = []
        for indicator, weight in self.normalized_indicators:
            indicator_signal = indicator.generate_signals(data)
            indicator_signals.append((indicator_signal, weight))
            signals[f"{indicator.__class__.__name__}_signal"] = indicator_signal
        
        # Calculate weighted composite signal
        composite_signal = pd.Series(0.0, index=data.index)
        for indicator_signal, weight in indicator_signals:
            composite_signal += indicator_signal * weight
        
        signals["composite_signal"] = composite_signal
        
        # Generate final signals based on threshold and confirmation
        if self.require_confirmation and len(self.indicators) > 1:
            # Count how many indicators agree on direction for each time point
            buy_agreement = pd.Series(0, index=data.index)
            sell_agreement = pd.Series(0, index=data.index)
            
            for indicator_signal, _ in indicator_signals:
                buy_agreement += (indicator_signal > 0).astype(int)
                sell_agreement += (indicator_signal < 0).astype(int)
            
            # Only trade if majority agrees
            min_agreement = max(1, len(self.indicators) // 2)
            
            signals.loc[(composite_signal > self.signal_threshold) & (buy_agreement >= min_agreement), "signal"] = 1.0
            signals.loc[(composite_signal < -self.signal_threshold) & (sell_agreement >= min_agreement), "signal"] = -1.0
        else:
            # Simple threshold-based signals
            signals.loc[composite_signal > self.signal_threshold, "signal"] = 1.0
            signals.loc[composite_signal < -self.signal_threshold, "signal"] = -1.0
        
        # Generate positions (1 for buy, -1 for sell, 0 for hold)
        signals["positions"] = signals["signal"].diff()
        return signals


class DefaultStrategy(Strategy):
    """Default strategy using Moving Average Crossover for basic usage."""
    
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
        # Get the index labels starting from short_window position
        start_idx = signals.index[self.short_window]
        signals.loc[start_idx:, 'signal'] = (signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:]).astype(float)
        
        # Generate trading orders (1 for buy, -1 for sell)
        signals["positions"] = signals["signal"].diff()
        return signals


# Legacy strategy classes for backward compatibility
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
        # Get the index labels starting from short_window position
        start_idx = signals.index[self.short_window]
        signals.loc[start_idx:, 'signal'] = (signals['short_mavg'][self.short_window:] > signals['long_mavg'][self.short_window:]).astype(float)
        
        # Generate trading orders (1 for buy, -1 for sell)
        signals["positions"] = signals["signal"].diff()
        return signals


class RSIReversal(Strategy):
    """A strategy based on RSI overbought/oversold signals."""

    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0

        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.rolling(window=self.period, min_periods=1).mean()
        avg_loss = loss.rolling(window=self.period, min_periods=1).mean()

        rs = avg_gain / (avg_loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        signals["rsi"] = rsi

        signals.loc[rsi < self.oversold, "signal"] = 1.0  # Buy
        signals.loc[rsi > self.overbought, "signal"] = -1.0  # Sell

        signals["positions"] = signals["signal"].diff()
        return signals


class BollingerBandsStrategy(Strategy):
    """A strategy based on Bollinger Bands."""

    def __init__(self, window: int = 20, num_std: float = 2):
        self.window = window
        self.num_std = num_std

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0

        rolling_mean = data["Close"].rolling(window=self.window, min_periods=1).mean()
        rolling_std = data["Close"].rolling(window=self.window, min_periods=1).std()

        upper_band = rolling_mean + (rolling_std * self.num_std)
        lower_band = rolling_mean - (rolling_std * self.num_std)

        signals["upper_band"] = upper_band
        signals["lower_band"] = lower_band
        signals["middle_band"] = rolling_mean

        # Buy when price crosses below lower band, sell when crosses above upper band
        signals.loc[data["Close"] < lower_band, "signal"] = 1.0
        signals.loc[data["Close"] > upper_band, "signal"] = -1.0

        signals["positions"] = signals["signal"].diff()
        return signals


class MeanReversionStrategy(Strategy):
    """A simple mean reversion strategy using z-score."""

    def __init__(self, window: int = 20, entry_z: float = 1.0, exit_z: float = 0.0):
        self.window = window
        self.entry_z = entry_z
        self.exit_z = exit_z

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0

        rolling_mean = data["Close"].rolling(window=self.window, min_periods=1).mean()
        rolling_std = data["Close"].rolling(window=self.window, min_periods=1).std()
        z_score = (data["Close"] - rolling_mean) / (rolling_std + 1e-10)
        signals["z_score"] = z_score

        # Buy when z-score < -entry_z, sell when z-score > entry_z
        signals.loc[z_score < -self.entry_z, "signal"] = 1.0
        signals.loc[z_score > self.entry_z, "signal"] = -1.0

        # Exit when z-score crosses back toward zero
        signals.loc[(signals["signal"].shift(1) == 1.0) & (z_score > -self.exit_z), "signal"] = 0.0
        signals.loc[(signals["signal"].shift(1) == -1.0) & (z_score < self.exit_z), "signal"] = 0.0

        signals["positions"] = signals["signal"].diff()
        return signals

