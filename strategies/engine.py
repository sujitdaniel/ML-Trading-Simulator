# backend/core/engine.py
import pandas as pd
from .strategies import (
    Strategy, DefaultStrategy, CompositeStrategy,
    MovingAverageIndicator, RSIIndicator, BollingerBandsIndicator, MeanReversionIndicator, MoneyFlowIndexIndicator,
    ParabolicSARIndicator, ChandeMomentumOscillatorIndicator, StochasticOscillatorIndicator, WilliamsPercentRangeIndicator,
    MACDIndicator, OBVIndicator, EMAIndicator, VWAPIndicator, ATRIndicator, IBSIndicator, FibonacciRetracementIndicator,
    PPOIndicator, ADXIndicator, StandardDeviationIndicator, RVIIndicator
)
from typing import List, Tuple, Optional


class TradingEngine:
    def __init__(self, strategy: Strategy, ticker: str, data_path: str = "./data/raw"):
        self.strategy = strategy
        self.ticker = ticker
        self.data = self._load_data(f"{data_path}/{ticker}.csv")
        self.trades = []
        self.signals = None

    def _load_data(self, filepath: str) -> pd.DataFrame:
        # Read the CSV file, skipping the first 3 header rows
        df = pd.read_csv(filepath, skiprows=3, header=None, index_col=0, parse_dates=True)
        df.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        return df

    def run(self):
        """Runs the strategy and generates a log of trades."""
        self.signals = self.strategy.generate_signals(self.data)
        self.trades = []
        
        for i in range(len(self.signals)):
            if self.signals["positions"].iloc[i] == 1.0:  # Buy signal
                self.trades.append(("BUY", self.data.index[i], self.data["Close"].iloc[i]))
            elif self.signals["positions"].iloc[i] == -1.0:  # Sell signal
                self.trades.append(("SELL", self.data.index[i], self.data["Close"].iloc[i]))
        return self.trades
    
    def get_signals(self):
        """Returns the generated signals DataFrame."""
        if self.signals is None:
            self.run()
        return self.signals
    
    def get_trade_summary(self):
        """Returns a summary of the trading performance."""
        if not self.trades:
            self.run()
        
        if not self.trades:
            return {"total_trades": 0, "buy_trades": 0, "sell_trades": 0}
        
        buy_trades = [trade for trade in self.trades if trade[0] == "BUY"]
        sell_trades = [trade for trade in self.trades if trade[0] == "SELL"]
        
        return {
            "total_trades": len(self.trades),
            "buy_trades": len(buy_trades),
            "sell_trades": len(sell_trades)
        }


class StrategyBuilder:
    """Helper class to build composite strategies easily."""
    
    @staticmethod
    def create_default_strategy() -> DefaultStrategy:
        """Create a default strategy using Moving Average Crossover."""
        return DefaultStrategy()
    
    @staticmethod
    def create_single_indicator_strategy(indicator_type: str, **kwargs) -> CompositeStrategy:
        """
        Create a strategy with a single indicator.
        
        Args:
            indicator_type: 'ma', 'rsi', 'bollinger', 'mean_reversion'
            **kwargs: Parameters for the specific indicator
        """
        indicator = StrategyBuilder._create_indicator(indicator_type, **kwargs)
        return CompositeStrategy([(indicator, 1.0)], require_confirmation=False)
    
    @staticmethod
    def create_dual_indicator_strategy(indicator1_type: str, indicator2_type: str,
                                     weight1: float = 0.5, weight2: float = 0.5,
                                     **kwargs) -> CompositeStrategy:
        """
        Create a strategy with two indicators.
        
        Args:
            indicator1_type: First indicator type
            indicator2_type: Second indicator type
            weight1: Weight for first indicator (0.0 to 1.0)
            weight2: Weight for second indicator (0.0 to 1.0)
            **kwargs: Parameters for the indicators (use prefix like 'ind1_' or 'ind2_')
        """
        # Extract parameters for each indicator
        ind1_params = {k.replace('ind1_', ''): v for k, v in kwargs.items() if k.startswith('ind1_')}
        ind2_params = {k.replace('ind2_', ''): v for k, v in kwargs.items() if k.startswith('ind2_')}
        
        indicator1 = StrategyBuilder._create_indicator(indicator1_type, **ind1_params)
        indicator2 = StrategyBuilder._create_indicator(indicator2_type, **ind2_params)
        
        return CompositeStrategy([(indicator1, weight1), (indicator2, weight2)])
    
    @staticmethod
    def create_triple_indicator_strategy(indicator1_type: str, indicator2_type: str, indicator3_type: str,
                                       weight1: float = 0.33, weight2: float = 0.33, weight3: float = 0.34,
                                       **kwargs) -> CompositeStrategy:
        """
        Create a strategy with three indicators.
        
        Args:
            indicator1_type: First indicator type
            indicator2_type: Second indicator type
            indicator3_type: Third indicator type
            weight1: Weight for first indicator
            weight2: Weight for second indicator
            weight3: Weight for third indicator
            **kwargs: Parameters for the indicators (use prefix like 'ind1_', 'ind2_', 'ind3_')
        """
        # Extract parameters for each indicator
        ind1_params = {k.replace('ind1_', ''): v for k, v in kwargs.items() if k.startswith('ind1_')}
        ind2_params = {k.replace('ind2_', ''): v for k, v in kwargs.items() if k.startswith('ind2_')}
        ind3_params = {k.replace('ind3_', ''): v for k, v in kwargs.items() if k.startswith('ind3_')}
        
        indicator1 = StrategyBuilder._create_indicator(indicator1_type, **ind1_params)
        indicator2 = StrategyBuilder._create_indicator(indicator2_type, **ind2_params)
        indicator3 = StrategyBuilder._create_indicator(indicator3_type, **ind3_params)
        
        return CompositeStrategy([(indicator1, weight1), (indicator2, weight2), (indicator3, weight3)])
    
    @staticmethod
    def _create_indicator(indicator_type: str, **kwargs):
        """Create an indicator instance based on type."""
        indicator_type = indicator_type.lower()
        
        if indicator_type == 'ma':
            return MovingAverageIndicator(**kwargs)
        elif indicator_type == 'rsi':
            return RSIIndicator(**kwargs)
        elif indicator_type == 'bollinger':
            return BollingerBandsIndicator(**kwargs)
        elif indicator_type == 'mean_reversion':
            return MeanReversionIndicator(**kwargs)
        elif indicator_type == 'mfi':
            return MoneyFlowIndexIndicator(**kwargs)
        elif indicator_type == 'sar':
            return ParabolicSARIndicator(**kwargs)
        elif indicator_type == 'cmo':
            return ChandeMomentumOscillatorIndicator(**kwargs)
        elif indicator_type == 'stochastic':
            return StochasticOscillatorIndicator(**kwargs)
        elif indicator_type == 'williams_r':
            return WilliamsPercentRangeIndicator(**kwargs)
        elif indicator_type == 'macd':
            return MACDIndicator(**kwargs)
        elif indicator_type == 'obv':
            return OBVIndicator(**kwargs)
        elif indicator_type == 'ema':
            return EMAIndicator(**kwargs)
        elif indicator_type == 'vwap':
            return VWAPIndicator(**kwargs)
        elif indicator_type == 'atr':
            return ATRIndicator(**kwargs)
        elif indicator_type == 'ibs':
            return IBSIndicator(**kwargs)
        elif indicator_type == 'fibonacci':
            return FibonacciRetracementIndicator(**kwargs)
        elif indicator_type == 'ppo':
            return PPOIndicator(**kwargs)
        elif indicator_type == 'adx':
            return ADXIndicator(**kwargs)
        elif indicator_type == 'std':
            return StandardDeviationIndicator(**kwargs)
        elif indicator_type == 'rvi':
            return RVIIndicator(**kwargs)
        else:
            raise ValueError(f"Unknown indicator type: {indicator_type}")


# Example usage functions
def create_strategy_examples():
    """Create example strategies for demonstration."""
    examples = {}
    
    # Example 1: Single RSI strategy
    examples['rsi_only'] = StrategyBuilder.create_single_indicator_strategy('rsi', period=14)
    
    # Example 2: Moving Average + RSI combination
    examples['ma_rsi'] = StrategyBuilder.create_dual_indicator_strategy(
        'ma', 'rsi', 
        weight1=0.6, weight2=0.4,
        ind1_short_window=20, ind1_long_window=50,
        ind2_period=14
    )
    
    # Example 3: Triple indicator strategy
    examples['triple'] = StrategyBuilder.create_triple_indicator_strategy(
        'ma', 'rsi', 'bollinger',
        weight1=0.4, weight2=0.3, weight3=0.3,
        ind1_short_window=20, ind1_long_window=50,
        ind2_period=14,
        ind3_window=20, ind3_num_std=2
    )
    
    return examples
