# backend/core/engine.py
import pandas as pd
from pathlib import Path
from .strategies import (
    Strategy, DefaultStrategy, CompositeStrategy, HybridMLIndicatorStrategy,
    MovingAverageIndicator, RSIIndicator, BollingerBandsIndicator, MeanReversionIndicator, MoneyFlowIndexIndicator,
    ParabolicSARIndicator, ChandeMomentumOscillatorIndicator, StochasticOscillatorIndicator, WilliamsPercentRangeIndicator,
    MACDIndicator, OBVIndicator, EMAIndicator, VWAPIndicator, ATRIndicator, IBSIndicator, FibonacciRetracementIndicator,
    PPOIndicator, ADXIndicator, StandardDeviationIndicator, RVIIndicator
)
from typing import List, Tuple, Optional, Dict, Any
import sys
import os

# Add ml module to path for ML strategy import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from ml.logistic_model import generate_ml_signals


class TradingEngine:
    def __init__(self, strategy: Strategy, ticker: str, data_file: str = None, initial_capital: float = 10000.0, ml_func=None, data: pd.DataFrame = None):
        self.strategy = strategy
        self.ticker = ticker
        self.data_file = data_file
        self.initial_capital = initial_capital
        self.data = data
        self.trades = []
        self.signals = None
        self.portfolio_value = initial_capital
        self.ml_func = ml_func
        if self.data is None:
            self._load_data()

    def _load_data(self) -> None:
        """Load and preprocess data efficiently."""
        if self.data_file:
            filepath = Path(self.data_file)
        else:
            # Fallback to static data
            filepath = Path("./data/raw") / f"{self.ticker}.csv"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Optimized data loading with specific dtypes and parsing
        try:
            # Read CSV with optimized settings
            df = pd.read_csv(
                filepath, 
                skiprows=3, 
                header=None, 
                index_col=0, 
                parse_dates=True
            )
            
            # Handle different column counts
            if len(df.columns) == 7:  # Old format: Date, Open, High, Low, Close, Volume, Dividends
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
            elif len(df.columns) == 6:  # New format: Date, Open, High, Low, Close, Volume
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends']
            else:
                # Use only the columns we need
                df = df.iloc[:, :5]  # Take first 5 columns: Open, High, Low, Close, Volume
                df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Ensure data is sorted by date
            df.sort_index(inplace=True)
            
            # Remove any rows with NaN values
            df.dropna(inplace=True)
            
            self.data = df
            
        except Exception as e:
            raise ValueError(f"Error loading data from {filepath}: {e}")

    def run(self, strategy_type: str = "ma") -> List[Tuple[str, pd.Timestamp, float]]:
        """Runs the strategy and generates a log of trades efficiently."""
        if self.data is None or self.data.empty:
            raise ValueError("No data available for analysis")
        
        print(f"Running strategy on {len(self.data)} data points")
        print(f"Data range: {self.data.index.min()} to {self.data.index.max()}")
        
        # Handle ML strategy separately
        if strategy_type == "ml":
            print(f"Running ML strategy ({self.ml_func.__name__ if self.ml_func else 'Logistic Regression'})")
            if self.ml_func is not None:
                self.signals, self.ml_metrics = self.ml_func(self.data)
            else:
                from ml.logistic_model import generate_ml_signals
                self.signals, self.ml_metrics = generate_ml_signals(self.data)
            # ML strategy uses 'ml_signal' column instead of 'positions'
            self.trades = self._extract_trades_ml()
        else:
            # Generate signals using traditional strategy
            self.signals = self.strategy.generate_signals(self.data)
            # Efficiently extract trades using vectorized operations
            self.trades = self._extract_trades()
        
        return self.trades
    
    def _extract_trades(self) -> List[Tuple[str, pd.Timestamp, float]]:
        """Extract trades efficiently using vectorized operations."""
        if self.signals is None or 'positions' not in self.signals.columns:
            return []
        
        trades = []
        positions = self.signals['positions']
        
        # Find buy and sell signals efficiently
        buy_signals = positions == 1.0
        sell_signals = positions == -1.0
        
        # Get indices where signals occur
        buy_indices = buy_signals[buy_signals].index
        sell_indices = sell_signals[sell_signals].index
        
        # Create trades efficiently
        for idx in buy_indices:
            trades.append(("BUY", idx, self.data.loc[idx, "Close"]))
        
        for idx in sell_indices:
            trades.append(("SELL", idx, self.data.loc[idx, "Close"]))
        
        return trades
    
    def _extract_trades_ml(self) -> List[Tuple[str, pd.Timestamp, float]]:
        """Extract trades from ML strategy signals."""
        if self.signals is None or 'ml_signal' not in self.signals.columns:
            return []
        
        trades = []
        ml_signals = self.signals['ml_signal']
        
        # Find buy and sell signals efficiently
        buy_signals = ml_signals == 1
        sell_signals = ml_signals == -1
        
        # Get indices where signals occur
        buy_indices = buy_signals[buy_signals].index
        sell_indices = sell_signals[sell_signals].index
        
        # Create trades efficiently
        for idx in buy_indices:
            trades.append(("BUY", idx, self.data.loc[idx, "Close"]))
        
        for idx in sell_indices:
            trades.append(("SELL", idx, self.data.loc[idx, "Close"]))
        
        return trades
    
    def get_signals(self) -> pd.DataFrame:
        """Returns the generated signals DataFrame."""
        if self.signals is None:
            self.run()
        return self.signals
    
    def filter_data_by_date_range(self, start_date, end_date):
        """Filter data to the specified date range."""
        if self.data is not None and not self.data.empty:
            original_length = len(self.data)
            mask = (self.data.index >= pd.Timestamp(start_date)) & (self.data.index <= pd.Timestamp(end_date))
            self.data = self.data.loc[mask]
            print(f"Filtered data from {original_length} to {len(self.data)} rows for date range {start_date} to {end_date}")
            print(f"Data range after filtering: {self.data.index.min()} to {self.data.index.max()}")

    def get_trade_summary(self) -> Dict[str, int]:
        """Returns a summary of the trading performance efficiently."""
        if not self.trades:
            self.run()
        
        if not self.trades:
            return {"total_trades": 0, "buy_trades": 0, "sell_trades": 0}
        
        # Count trades efficiently using list comprehension
        buy_trades = sum(1 for trade in self.trades if trade[0] == "BUY")
        sell_trades = sum(1 for trade in self.trades if trade[0] == "SELL")
        
        return {
            "total_trades": len(self.trades),
            "buy_trades": buy_trades,
            "sell_trades": sell_trades
        }

    def calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate real performance metrics from trades."""
        if not self.trades:
            return {
                "win_rate": 0.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "final_portfolio_value": self.initial_capital,
                "total_profit_loss": 0.0
            }
        
        # Calculate returns from trades with proper portfolio tracking
        position = 0  # 0 = no position, 1 = long position
        entry_price = 0
        shares_held = 0
        returns = []
        equity_curve = [self.initial_capital]
        cash = self.initial_capital
        
        for trade in self.trades:
            action, date, price = trade
            
            if action == "BUY" and position == 0:
                # Enter long position
                position = 1
                entry_price = price
                shares_held = cash / price
                cash = 0
            elif action == "SELL" and position == 1:
                # Exit long position
                position = 0
                cash = shares_held * price
                trade_return = (price - entry_price) / entry_price
                returns.append(trade_return)
                shares_held = 0
                
                # Update equity curve
                current_equity = cash
                equity_curve.append(current_equity)
        
        # Calculate final portfolio value
        if position == 1:
            # Still holding position at end
            final_portfolio_value = shares_held * self.trades[-1][2]  # Last trade price
        else:
            final_portfolio_value = cash
        
        total_profit_loss = final_portfolio_value - self.initial_capital
        
        if not returns:
            return {
                "win_rate": 0.0,
                "total_return": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "final_portfolio_value": final_portfolio_value,
                "total_profit_loss": total_profit_loss
            }
        
        # Calculate metrics
        winning_trades = sum(1 for r in returns if r > 0)
        win_rate = winning_trades / len(returns) if returns else 0.0
        
        total_return = (final_portfolio_value - self.initial_capital) / self.initial_capital
        
        # Calculate Sharpe ratio (simplified)
        avg_return = sum(returns) / len(returns) if returns else 0.0
        std_return = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0.0
        sharpe_ratio = avg_return / std_return if std_return > 0 else 0.0
        
        # Calculate max drawdown
        peak = equity_curve[0]
        max_drawdown = 0.0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak if peak > 0 else 0.0
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            "win_rate": win_rate,
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "final_portfolio_value": final_portfolio_value,
            "total_profit_loss": total_profit_loss
        }

    def get_ml_metrics(self):
        return getattr(self, "ml_metrics", {})


class StrategyBuilder:
    """Helper class to build composite strategies efficiently."""
    
    # Cache for indicator creation to avoid repeated string operations
    _INDICATOR_MAP = {
        'ma': MovingAverageIndicator,
        'rsi': RSIIndicator,
        'bollinger': BollingerBandsIndicator,
        'mean_reversion': MeanReversionIndicator,
        'mfi': MoneyFlowIndexIndicator,
        'sar': ParabolicSARIndicator,
        'cmo': ChandeMomentumOscillatorIndicator,
        'stochastic': StochasticOscillatorIndicator,
        'williams_r': WilliamsPercentRangeIndicator,
        'macd': MACDIndicator,
        'obv': OBVIndicator,
        'ema': EMAIndicator,
        'vwap': VWAPIndicator,
        'atr': ATRIndicator,
        'ibs': IBSIndicator,
        'fibonacci': FibonacciRetracementIndicator,
        'ppo': PPOIndicator,
        'adx': ADXIndicator,
        'std': StandardDeviationIndicator,
        'rvi': RVIIndicator
    }
    
    @staticmethod
    def create_default_strategy() -> DefaultStrategy:
        """Create a default strategy using Moving Average Crossover."""
        return DefaultStrategy()
    
    @staticmethod
    def create_single_indicator_strategy(indicator_type: str, **kwargs) -> CompositeStrategy:
        """
        Create a strategy with a single indicator.
        
        Args:
            indicator_type: Indicator type (e.g., 'ma', 'rsi', 'bollinger')
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
        # Extract parameters efficiently using dict comprehension
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
        # Extract parameters efficiently
        ind1_params = {k.replace('ind1_', ''): v for k, v in kwargs.items() if k.startswith('ind1_')}
        ind2_params = {k.replace('ind2_', ''): v for k, v in kwargs.items() if k.startswith('ind2_')}
        ind3_params = {k.replace('ind3_', ''): v for k, v in kwargs.items() if k.startswith('ind3_')}
        
        indicator1 = StrategyBuilder._create_indicator(indicator1_type, **ind1_params)
        indicator2 = StrategyBuilder._create_indicator(indicator2_type, **ind2_params)
        indicator3 = StrategyBuilder._create_indicator(indicator3_type, **ind3_params)
        
        return CompositeStrategy([(indicator1, weight1), (indicator2, weight2), (indicator3, weight3)])
    
    @staticmethod
    def create_hybrid_ml_indicator_strategy(indicator_types: list, indicator_weights: list, ml_weight: float = 0.5, signal_threshold: float = 0.5, require_confirmation: bool = True, **kwargs) -> HybridMLIndicatorStrategy:
        """
        Create a hybrid strategy that combines ML signals with indicator signals.
        Args:
            indicator_types: List of indicator type strings (e.g., ['ma', 'rsi'])
            indicator_weights: List of floats for indicator weights (must sum with ml_weight to 1.0)
            ml_weight: Weight for ML signal
            signal_threshold: Threshold for composite signal
            require_confirmation: Require agreement for trade
            **kwargs: Indicator-specific parameters (use prefix like 'ind1_', 'ind2_')
        Returns:
            HybridMLIndicatorStrategy instance
        """
        if len(indicator_types) != len(indicator_weights):
            raise ValueError("indicator_types and indicator_weights must have the same length")
        indicators = []
        for i, (ind_type, weight) in enumerate(zip(indicator_types, indicator_weights)):
            ind_kwargs = {k.replace(f'ind{i+1}_', ''): v for k, v in kwargs.items() if k.startswith(f'ind{i+1}_')}
            indicator = StrategyBuilder._create_indicator(ind_type, **ind_kwargs)
            indicators.append((indicator, weight))
        return HybridMLIndicatorStrategy(indicators, ml_weight=ml_weight, signal_threshold=signal_threshold, require_confirmation=require_confirmation)
    
    @staticmethod
    def _create_indicator(indicator_type: str, **kwargs):
        """Create an indicator instance based on type using cached mapping."""
        indicator_type = indicator_type.lower()
        
        if indicator_type not in StrategyBuilder._INDICATOR_MAP:
            raise ValueError(f"Unknown indicator type: {indicator_type}")
        
        return StrategyBuilder._INDICATOR_MAP[indicator_type](**kwargs)


def create_strategy_examples() -> Dict[str, CompositeStrategy]:
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
