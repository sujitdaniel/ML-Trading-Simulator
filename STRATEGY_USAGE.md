# Algonex Strategy System - User Guide

## Overview

The Algonex strategy system allows you to create flexible trading strategies by combining multiple technical indicators. You can use up to 3 indicators at a time, with at least 1 required. The system provides a default strategy for basic usage and allows for custom combinations with configurable weights.

## Quick Start

### 1. Default Strategy (Recommended for Beginners)

```python
from strategies.engine import TradingEngine, StrategyBuilder

# Create and run default strategy
default_strategy = StrategyBuilder.create_default_strategy()
engine = TradingEngine(default_strategy, "AAPL")
trades = engine.run()
summary = engine.get_trade_summary()

print(f"Total trades: {summary['total_trades']}")
```

### 2. Single Indicator Strategy

```python
# RSI Strategy
rsi_strategy = StrategyBuilder.create_single_indicator_strategy('rsi', period=14)
engine = TradingEngine(rsi_strategy, "AAPL")
trades = engine.run()
```

### 3. Dual Indicator Strategy

```python
# Moving Average + RSI combination
dual_strategy = StrategyBuilder.create_dual_indicator_strategy(
    'ma', 'rsi',
    weight1=0.6, weight2=0.4,  # MA has higher weight
    ind1_short_window=20, ind1_long_window=50,
    ind2_period=14
)
engine = TradingEngine(dual_strategy, "AAPL")
trades = engine.run()
```

### 4. Triple Indicator Strategy

```python
# MA + RSI + Bollinger Bands
triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'rsi', 'bollinger',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_short_window=20, ind1_long_window=50,
    ind2_period=14,
    ind3_window=20, ind3_num_std=2
)
engine = TradingEngine(triple_strategy, "AAPL")
trades = engine.run()
```

## Available Indicators

### 1. Moving Average Crossover (`ma`)
- **Parameters**: `short_window`, `long_window`
- **Description**: Generates signals when short MA crosses above/below long MA
- **Default**: `short_window=40`, `long_window=100`

```python
ma_strategy = StrategyBuilder.create_single_indicator_strategy(
    'ma', 
    short_window=20, 
    long_window=50
)
```

### 2. Relative Strength Index (`rsi`)
- **Parameters**: `period`, `overbought`, `oversold`
- **Description**: Generates buy signals when oversold, sell signals when overbought
- **Default**: `period=14`, `overbought=70`, `oversold=30`

```python
rsi_strategy = StrategyBuilder.create_single_indicator_strategy(
    'rsi', 
    period=10, 
    overbought=75, 
    oversold=25
)
```

### 3. Bollinger Bands (`bollinger`)
- **Parameters**: `window`, `num_std`
- **Description**: Generates signals based on price position within bands
- **Default**: `window=20`, `num_std=2`

```python
bb_strategy = StrategyBuilder.create_single_indicator_strategy(
    'bollinger', 
    window=15, 
    num_std=1.5
)
```

### 4. Mean Reversion (`mean_reversion`)
- **Parameters**: `window`, `entry_z`, `exit_z`
- **Description**: Generates signals based on price deviation from mean
- **Default**: `window=20`, `entry_z=1.0`, `exit_z=0.0`

```python
mr_strategy = StrategyBuilder.create_single_indicator_strategy(
    'mean_reversion', 
    window=30, 
    entry_z=1.5, 
    exit_z=0.5
)
```

## Advanced Usage

### Custom Weights and Parameters

When combining multiple indicators, you can specify custom weights and parameters:

```python
# Custom strategy with specific parameters
custom_strategy = StrategyBuilder.create_dual_indicator_strategy(
    'rsi', 'bollinger',
    weight1=0.7, weight2=0.3,  # RSI has higher weight
    ind1_period=10,  # Shorter RSI period for more sensitivity
    ind2_window=15, ind2_num_std=1.5  # Tighter Bollinger Bands
)
```

### Signal Analysis

Get detailed signal information:

```python
engine = TradingEngine(strategy, "AAPL")
trades = engine.run()
signals = engine.get_signals()

# View available signal columns
print(signals.columns)

# Analyze composite signal strength
print(signals['composite_signal'].tail(10))

# Check individual indicator signals
print(signals['RSIIndicator_signal'].tail(10))
```

### Trade Summary

Get performance metrics:

```python
summary = engine.get_trade_summary()
print(f"Total trades: {summary['total_trades']}")
print(f"Buy trades: {summary['buy_trades']}")
print(f"Sell trades: {summary['sell_trades']}")
```

## Strategy Configuration Options

### Signal Threshold
Control the sensitivity of the strategy:

```python
# More conservative signals (higher threshold)
conservative_strategy = CompositeStrategy(
    [(rsi_indicator, 1.0)], 
    signal_threshold=0.7,  # Requires stronger signals
    require_confirmation=False
)

# More aggressive signals (lower threshold)
aggressive_strategy = CompositeStrategy(
    [(rsi_indicator, 1.0)], 
    signal_threshold=0.3,  # Triggers on weaker signals
    require_confirmation=False
)
```

### Confirmation Requirements
Require multiple indicators to agree:

```python
# Requires at least 2 out of 3 indicators to agree
triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'rsi', 'bollinger',
    weight1=0.4, weight2=0.3, weight3=0.3
)
# require_confirmation=True by default for multi-indicator strategies
```

## Best Practices

### 1. Start Simple
- Begin with the default strategy to understand the system
- Test single indicators before combining them

### 2. Parameter Tuning
- Adjust indicator parameters based on your trading timeframe
- Use shorter periods for day trading, longer for swing trading

### 3. Weight Optimization
- Give higher weights to indicators that perform better for your asset
- Consider market conditions when setting weights

### 4. Risk Management
- Use `require_confirmation=True` for more conservative signals
- Monitor the `composite_signal` strength for signal quality

### 5. Backtesting
- Test strategies on historical data before live trading
- Compare different indicator combinations

## Example Strategies

### Conservative Strategy
```python
# RSI + Bollinger Bands with confirmation
conservative = StrategyBuilder.create_dual_indicator_strategy(
    'rsi', 'bollinger',
    weight1=0.5, weight2=0.5,
    ind1_period=14,
    ind2_window=20, ind2_num_std=2.5  # Wider bands
)
```

### Aggressive Strategy
```python
# Triple indicator with lower thresholds
aggressive = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'rsi', 'mean_reversion',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_short_window=10, ind1_long_window=30,  # Faster MA
    ind2_period=7,  # Shorter RSI
    ind3_window=10, ind3_entry_z=1.0  # Faster mean reversion
)
```

### Trend Following Strategy
```python
# Heavy weight on Moving Average
trend_following = StrategyBuilder.create_dual_indicator_strategy(
    'ma', 'rsi',
    weight1=0.8, weight2=0.2,  # Heavy MA weight
    ind1_short_window=50, ind1_long_window=200,  # Longer periods
    ind2_period=21  # Longer RSI
)
```

## Troubleshooting

### Common Issues

1. **No trades generated**: Lower the `signal_threshold` or adjust indicator parameters
2. **Too many trades**: Increase the `signal_threshold` or use `require_confirmation=True`
3. **Poor performance**: Try different indicator combinations or adjust weights

### Performance Tips

1. **Data Quality**: Ensure your price data is clean and complete
2. **Parameter Stability**: Avoid over-optimizing on small datasets
3. **Market Conditions**: Different strategies work better in different market environments

## Running the Examples

Execute the example script to see the system in action:

```bash
python example_usage.py
```

This will run various strategy combinations on AAPL data and show the results.

## Support

For questions or issues:
1. Check the example usage script
2. Review the indicator parameters
3. Test with different combinations
4. Monitor signal quality using the `composite_signal` column 