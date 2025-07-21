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


class MoneyFlowIndexIndicator(Indicator):
    """Money Flow Index indicator that combines price and volume data."""
    
    def __init__(self, period: int = 14, overbought: float = 80, oversold: float = 20):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # Calculate typical price
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        
        # Calculate raw money flow
        raw_money_flow = typical_price * data['Volume']
        
        # Determine positive and negative money flow
        positive_flow = pd.Series(0.0, index=data.index)
        negative_flow = pd.Series(0.0, index=data.index)
        
        # Compare current typical price with previous
        price_diff = typical_price.diff()
        positive_flow.loc[price_diff > 0] = raw_money_flow.loc[price_diff > 0]
        negative_flow.loc[price_diff < 0] = raw_money_flow.loc[price_diff < 0]
        
        # Calculate positive and negative money flow sums
        positive_mf = positive_flow.rolling(window=self.period, min_periods=1).sum()
        negative_mf = negative_flow.rolling(window=self.period, min_periods=1).sum()
        
        # Calculate money ratio
        money_ratio = positive_mf / (negative_mf + 1e-10)
        
        # Calculate Money Flow Index
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        mfi = self.calculate(data)
        
        # Buy when MFI is oversold, sell when overbought
        signals.loc[mfi < self.oversold] = 1.0  # Buy signal
        signals.loc[mfi > self.overbought] = -1.0  # Sell signal
        return signals


class ParabolicSARIndicator(Indicator):
    """Parabolic SAR (Stop and Reverse) indicator for trend following."""
    
    def __init__(self, acceleration: float = 0.02, maximum: float = 0.2):
        self.acceleration = acceleration
        self.maximum = maximum
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Parabolic SAR values."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Initialize SAR array
        sar = pd.Series(index=data.index, dtype=float)
        ep = pd.Series(index=data.index, dtype=float)  # Extreme Point
        af = pd.Series(index=data.index, dtype=float)  # Acceleration Factor
        trend = pd.Series(index=data.index, dtype=int)  # 1 for uptrend, -1 for downtrend
        
        # Initialize first values
        sar.iloc[0] = low.iloc[0]
        ep.iloc[0] = high.iloc[0]
        af.iloc[0] = self.acceleration
        trend.iloc[0] = 1
        
        # Calculate SAR for each period
        for i in range(1, len(data)):
            prev_sar = sar.iloc[i-1]
            prev_ep = ep.iloc[i-1]
            prev_af = af.iloc[i-1]
            prev_trend = trend.iloc[i-1]
            
            current_high = high.iloc[i]
            current_low = low.iloc[i]
            
            # Calculate SAR
            if prev_trend == 1:  # Uptrend
                sar.iloc[i] = prev_sar + prev_af * (prev_ep - prev_sar)
                # Check if we need to reverse
                if current_low < sar.iloc[i]:
                    trend.iloc[i] = -1
                    sar.iloc[i] = prev_ep
                    ep.iloc[i] = current_low
                    af.iloc[i] = self.acceleration
                else:
                    trend.iloc[i] = 1
                    if current_high > prev_ep:
                        ep.iloc[i] = current_high
                        af.iloc[i] = min(prev_af + self.acceleration, self.maximum)
                    else:
                        ep.iloc[i] = prev_ep
                        af.iloc[i] = prev_af
            else:  # Downtrend
                sar.iloc[i] = prev_sar + prev_af * (prev_ep - prev_sar)
                # Check if we need to reverse
                if current_high > sar.iloc[i]:
                    trend.iloc[i] = 1
                    sar.iloc[i] = prev_ep
                    ep.iloc[i] = current_high
                    af.iloc[i] = self.acceleration
                else:
                    trend.iloc[i] = -1
                    if current_low < prev_ep:
                        ep.iloc[i] = current_low
                        af.iloc[i] = min(prev_af + self.acceleration, self.maximum)
                    else:
                        ep.iloc[i] = prev_ep
                        af.iloc[i] = prev_af
        
        return sar
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        sar = self.calculate(data)
        
        # Generate signals based on price position relative to SAR
        # Buy when close > SAR (uptrend), Sell when close < SAR (downtrend)
        signals.loc[data['Close'] > sar] = 1.0  # Buy signal
        signals.loc[data['Close'] < sar] = -1.0  # Sell signal
        return signals


class ChandeMomentumOscillatorIndicator(Indicator):
    """Chande Momentum Oscillator (CMO) indicator."""
    
    def __init__(self, period: int = 14, overbought: float = 50, oversold: float = -50):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Chande Momentum Oscillator."""
        close = data['Close']
        
        # Calculate price changes
        price_change = close.diff()
        
        # Separate gains and losses
        gains = price_change.where(price_change > 0, 0.0)
        losses = -price_change.where(price_change < 0, 0.0)
        
        # Calculate sum of gains and losses over the period
        sum_gains = gains.rolling(window=self.period, min_periods=1).sum()
        sum_losses = losses.rolling(window=self.period, min_periods=1).sum()
        
        # Calculate CMO
        cmo = 100 * (sum_gains - sum_losses) / (sum_gains + sum_losses + 1e-10)
        
        return cmo
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        cmo = self.calculate(data)
        
        # Generate signals based on CMO levels
        # Buy when CMO is oversold (negative), Sell when overbought (positive)
        signals.loc[cmo < self.oversold] = 1.0  # Buy signal
        signals.loc[cmo > self.overbought] = -1.0  # Sell signal
        return signals


class StochasticOscillatorIndicator(Indicator):
    """Stochastic Oscillator indicator."""
    
    def __init__(self, k_period: int = 14, d_period: int = 3, overbought: float = 80, oversold: float = 20):
        self.k_period = k_period
        self.d_period = d_period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Stochastic Oscillator %K."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate %K
        lowest_low = low.rolling(window=self.k_period, min_periods=1).min()
        highest_high = high.rolling(window=self.k_period, min_periods=1).max()
        
        k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low + 1e-10)
        
        return k_percent
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        k_percent = self.calculate(data)
        
        # Generate signals based on overbought/oversold levels
        signals.loc[k_percent < self.oversold] = 1.0  # Buy signal
        signals.loc[k_percent > self.overbought] = -1.0  # Sell signal
        return signals


class WilliamsPercentRangeIndicator(Indicator):
    """Williams %R indicator."""
    
    def __init__(self, period: int = 14, overbought: float = -20, oversold: float = -80):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Williams %R."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate Williams %R
        highest_high = high.rolling(window=self.period, min_periods=1).max()
        lowest_low = low.rolling(window=self.period, min_periods=1).min()
        
        williams_r = -100 * (highest_high - close) / (highest_high - lowest_low + 1e-10)
        
        return williams_r
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        williams_r = self.calculate(data)
        
        # Generate signals (note: Williams %R is inverted)
        signals.loc[williams_r < self.oversold] = 1.0  # Buy signal
        signals.loc[williams_r > self.overbought] = -1.0  # Sell signal
        return signals


class MACDIndicator(Indicator):
    """Moving Average Convergence Divergence (MACD) indicator."""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate MACD line."""
        close = data['Close']
        
        # Calculate EMA
        ema_fast = close.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate MACD line
        macd_line = ema_fast - ema_slow
        
        return macd_line
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        macd_line = self.calculate(data)
        
        # Calculate signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # Generate signals based on MACD crossover
        signals.loc[macd_line > signal_line] = 1.0  # Buy signal
        signals.loc[macd_line < signal_line] = -1.0  # Sell signal
        return signals


class OBVIndicator(Indicator):
    """On-Balance Volume (OBV) indicator."""
    
    def __init__(self, period: int = 20):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume."""
        close = data['Close']
        volume = data['Volume']
        
        # Calculate price change
        price_change = close.diff()
        
        # Calculate OBV
        obv = pd.Series(0.0, index=data.index)
        obv.iloc[0] = volume.iloc[0]
        
        for i in range(1, len(data)):
            if price_change.iloc[i] > 0:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif price_change.iloc[i] < 0:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        obv = self.calculate(data)
        
        # Calculate OBV moving average
        obv_ma = obv.rolling(window=self.period, min_periods=1).mean()
        
        # Generate signals based on OBV vs its moving average
        signals.loc[obv > obv_ma] = 1.0  # Buy signal
        signals.loc[obv < obv_ma] = -1.0  # Sell signal
        return signals


class EMAIndicator(Indicator):
    """Exponential Moving Average (EMA) indicator."""
    
    def __init__(self, short_period: int = 12, long_period: int = 26):
        self.short_period = short_period
        self.long_period = long_period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate EMA difference."""
        close = data['Close']
        
        # Calculate EMAs
        ema_short = close.ewm(span=self.short_period, adjust=False).mean()
        ema_long = close.ewm(span=self.long_period, adjust=False).mean()
        
        # Return the difference
        return ema_short - ema_long
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        ema_diff = self.calculate(data)
        
        # Generate signals based on EMA crossover
        signals.loc[ema_diff > 0] = 1.0  # Buy signal
        signals.loc[ema_diff < 0] = -1.0  # Sell signal
        return signals


class VWAPIndicator(Indicator):
    """Volume Weighted Average Price (VWAP) indicator."""
    
    def __init__(self, period: int = 20):
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate VWAP."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        volume = data['Volume']
        
        # Calculate typical price
        typical_price = (high + low + close) / 3
        
        # Calculate VWAP
        vwap = (typical_price * volume).rolling(window=self.period, min_periods=1).sum() / \
               volume.rolling(window=self.period, min_periods=1).sum()
        
        return vwap
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        vwap = self.calculate(data)
        close = data['Close']
        
        # Generate signals based on price vs VWAP
        signals.loc[close > vwap] = 1.0  # Buy signal
        signals.loc[close < vwap] = -1.0  # Sell signal
        return signals


class ATRIndicator(Indicator):
    """Average True Range (ATR) indicator."""
    
    def __init__(self, period: int = 14, multiplier: float = 2.0):
        self.period = period
        self.multiplier = multiplier
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate ATR."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR
        atr = true_range.rolling(window=self.period, min_periods=1).mean()
        
        return atr
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        atr = self.calculate(data)
        close = data['Close']
        
        # Calculate upper and lower bands
        upper_band = close + (self.multiplier * atr)
        lower_band = close - (self.multiplier * atr)
        
        # Generate signals based on price vs bands
        signals.loc[close < lower_band] = 1.0  # Buy signal
        signals.loc[close > upper_band] = -1.0  # Sell signal
        return signals


class IBSIndicator(Indicator):
    """Internal Bar Strength (IBS) indicator."""
    
    def __init__(self, overbought: float = 0.8, oversold: float = 0.2):
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Internal Bar Strength."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate IBS
        ibs = (close - low) / (high - low + 1e-10)
        
        return ibs
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        ibs = self.calculate(data)
        
        # Generate signals based on IBS levels
        signals.loc[ibs < self.oversold] = 1.0  # Buy signal
        signals.loc[ibs > self.overbought] = -1.0  # Sell signal
        return signals


class FibonacciRetracementIndicator(Indicator):
    """Fibonacci Retracement Indicator."""
    
    def __init__(self, period: int = 20, retracement_level: float = 0.618):
        self.period = period
        self.retracement_level = retracement_level
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Fibonacci retracement levels."""
        high = data['High']
        low = data['Low']
        
        # Calculate swing high and low
        swing_high = high.rolling(window=self.period, min_periods=1).max()
        swing_low = low.rolling(window=self.period, min_periods=1).min()
        
        # Calculate Fibonacci retracement
        range_size = swing_high - swing_low
        fib_level = swing_high - (range_size * self.retracement_level)
        
        return fib_level
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        fib_level = self.calculate(data)
        close = data['Close']
        
        # Generate signals based on price vs Fibonacci level
        signals.loc[close < fib_level] = 1.0  # Buy signal
        signals.loc[close > fib_level] = -1.0  # Sell signal
        return signals


class PPOIndicator(Indicator):
    """Percentage Price Oscillator (PPO) indicator."""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate PPO line."""
        close = data['Close']
        
        # Calculate EMAs
        ema_fast = close.ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=self.slow_period, adjust=False).mean()
        
        # Calculate PPO
        ppo = 100 * (ema_fast - ema_slow) / ema_slow
        
        return ppo
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        ppo = self.calculate(data)
        
        # Calculate signal line
        signal_line = ppo.ewm(span=self.signal_period, adjust=False).mean()
        
        # Generate signals based on PPO crossover
        signals.loc[ppo > signal_line] = 1.0  # Buy signal
        signals.loc[ppo < signal_line] = -1.0  # Sell signal
        return signals


class ADXIndicator(Indicator):
    """Average Directional Index (ADX) indicator."""
    
    def __init__(self, period: int = 14, threshold: float = 25.0):
        self.period = period
        self.threshold = threshold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate ADX."""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate Directional Movement
        dm_plus = high - high.shift(1)
        dm_minus = low.shift(1) - low
        
        dm_plus = dm_plus.where((dm_plus > dm_minus) & (dm_plus > 0), 0)
        dm_minus = dm_minus.where((dm_minus > dm_plus) & (dm_minus > 0), 0)
        
        # Calculate smoothed values
        tr_smooth = true_range.rolling(window=self.period, min_periods=1).sum()
        dm_plus_smooth = dm_plus.rolling(window=self.period, min_periods=1).sum()
        dm_minus_smooth = dm_minus.rolling(window=self.period, min_periods=1).sum()
        
        # Calculate DI+ and DI-
        di_plus = 100 * dm_plus_smooth / tr_smooth
        di_minus = 100 * dm_minus_smooth / tr_smooth
        
        # Calculate DX
        dx = 100 * abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
        
        # Calculate ADX
        adx = dx.rolling(window=self.period, min_periods=1).mean()
        
        return adx
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        adx = self.calculate(data)
        
        # Generate signals based on ADX threshold
        # High ADX indicates strong trend
        signals.loc[adx > self.threshold] = 1.0  # Strong trend signal
        signals.loc[adx < self.threshold] = -1.0  # Weak trend signal
        return signals


class StandardDeviationIndicator(Indicator):
    """Standard Deviation Indicator."""
    
    def __init__(self, period: int = 20, multiplier: float = 2.0):
        self.period = period
        self.multiplier = multiplier
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate Standard Deviation."""
        close = data['Close']
        
        # Calculate rolling standard deviation
        std = close.rolling(window=self.period, min_periods=1).std()
        
        return std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        std = self.calculate(data)
        close = data['Close']
        
        # Calculate mean
        mean = close.rolling(window=self.period, min_periods=1).mean()
        
        # Calculate bands
        upper_band = mean + (self.multiplier * std)
        lower_band = mean - (self.multiplier * std)
        
        # Generate signals based on price vs bands
        signals.loc[close < lower_band] = 1.0  # Buy signal
        signals.loc[close > upper_band] = -1.0  # Sell signal
        return signals


class RVIIndicator(Indicator):
    """Relative Volatility Index (RVI) indicator."""
    
    def __init__(self, period: int = 14, overbought: float = 60, oversold: float = 40):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
    
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """Calculate RVI."""
        close = data['Close']
        
        # Calculate price change
        price_change = close.diff()
        
        # Calculate standard deviation
        std = price_change.rolling(window=self.period, min_periods=1).std()
        
        # Calculate RVI
        rvi = 100 * (std - std.rolling(window=self.period, min_periods=1).min()) / \
              (std.rolling(window=self.period, min_periods=1).max() - std.rolling(window=self.period, min_periods=1).min() + 1e-10)
        
        return rvi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0.0, index=data.index)
        rvi = self.calculate(data)
        
        # Generate signals based on RVI levels
        signals.loc[rvi < self.oversold] = 1.0  # Buy signal
        signals.loc[rvi > self.overbought] = -1.0  # Sell signal
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


class HybridMLIndicatorStrategy(Strategy):
    """A strategy that combines ML signals with indicator signals and configurable weights."""
    def __init__(self, indicators: List[Tuple[Indicator, float]], ml_weight: float = 0.5, signal_threshold: float = 0.5, require_confirmation: bool = True):
        if len(indicators) > 3:
            raise ValueError("Maximum 3 indicators allowed")
        if len(indicators) < 1:
            raise ValueError("At least 1 indicator required")
        if not (0.0 <= ml_weight <= 1.0):
            raise ValueError("ml_weight must be between 0.0 and 1.0")
        self.indicators = indicators
        self.ml_weight = ml_weight
        self.signal_threshold = signal_threshold
        self.require_confirmation = require_confirmation
        # Normalize indicator weights so that (sum + ml_weight) == 1
        total_weight = sum(weight for _, weight in indicators) + ml_weight
        self.normalized_indicators = [(ind, weight/total_weight) for ind, weight in indicators]
        self.normalized_ml_weight = ml_weight / total_weight

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        from ml.logistic_model import generate_ml_signals
        signals = pd.DataFrame(index=data.index)
        signals["signal"] = 0.0
        # Calculate indicator signals
        indicator_signals = []
        for indicator, weight in self.normalized_indicators:
            indicator_signal = indicator.generate_signals(data)
            indicator_signals.append((indicator_signal, weight))
            signals[f"{indicator.__class__.__name__}_signal"] = indicator_signal
        # Calculate ML signal
        ml_df, _ = generate_ml_signals(data)
        ml_signal = ml_df.reindex(data.index)["ml_signal"].fillna(0)
        signals["ml_signal"] = ml_signal
        # Calculate weighted composite signal
        composite_signal = pd.Series(0.0, index=data.index)
        for indicator_signal, weight in indicator_signals:
            composite_signal += indicator_signal * weight
        composite_signal += ml_signal * self.normalized_ml_weight
        signals["composite_signal"] = composite_signal
        # Generate final signals based on threshold and confirmation
        if self.require_confirmation and len(self.indicators) > 1:
            buy_agreement = pd.Series(0, index=data.index)
            sell_agreement = pd.Series(0, index=data.index)
            for indicator_signal, _ in indicator_signals:
                buy_agreement += (indicator_signal > 0).astype(int)
                sell_agreement += (indicator_signal < 0).astype(int)
            # ML signal counts as one vote
            buy_agreement += (ml_signal > 0).astype(int)
            sell_agreement += (ml_signal < 0).astype(int)
            min_agreement = max(1, (len(self.indicators) + 1) // 2)
            signals.loc[(composite_signal > self.signal_threshold) & (buy_agreement >= min_agreement), "signal"] = 1.0
            signals.loc[(composite_signal < -self.signal_threshold) & (sell_agreement >= min_agreement), "signal"] = -1.0
        else:
            signals.loc[composite_signal > self.signal_threshold, "signal"] = 1.0
            signals.loc[composite_signal < -self.signal_threshold, "signal"] = -1.0
        signals["positions"] = signals["signal"].diff()
        return signals

