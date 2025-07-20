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

## 📊 **Available Indicators**

### 1. **Moving Average Crossover** (`ma`)
- **Class**: `MovingAverageIndicator`
- **Parameters**: 
  - `short_window` (default: 40)
  - `long_window` (default: 100)
- **Description**: Generates signals when short MA crosses above/below long MA
- **Signal Logic**: Buy when short MA > long MA, Sell when short MA < long MA

### 2. **Relative Strength Index** (`rsi`)
- **Class**: `RSIIndicator`
- **Parameters**: 
  - `period` (default: 14)
  - `overbought` (default: 70)
  - `oversold` (default: 30)
- **Description**: Generates buy signals when oversold, sell signals when overbought
- **Signal Logic**: Buy when RSI < oversold, Sell when RSI > overbought

### 3. **Bollinger Bands** (`bollinger`)
- **Class**: `BollingerBandsIndicator`
- **Parameters**: 
  - `window` (default: 20)
  - `num_std` (default: 2)
- **Description**: Generates signals based on price position within bands
- **Signal Logic**: Buy when price near lower band, Sell when price near upper band

### 4. **Mean Reversion** (`mean_reversion`)
- **Class**: `MeanReversionIndicator`
- **Parameters**: 
  - `window` (default: 20)
  - `entry_z` (default: 1.0)
  - `exit_z` (default: 0.0)
- **Description**: Generates signals based on price deviation from mean using z-score
- **Signal Logic**: Buy when z-score < -entry_z, Sell when z-score > entry_z

### 5. **Money Flow Index** (`mfi`)
- **Class**: `MoneyFlowIndexIndicator`
- **Parameters**: 
  - `period` (default: 14)
  - `overbought` (default: 80)
  - `oversold` (default: 20)
- **Description**: Combines price and volume data to identify overbought/oversold conditions
- **Signal Logic**: Buy when MFI < oversold, Sell when MFI > overbought

### 6. **Parabolic SAR** (`sar`)
- **Class**: `ParabolicSARIndicator`
- **Parameters**: 
  - `acceleration` (default: 0.02)
  - `maximum` (default: 0.2)
- **Description**: Trend following indicator that provides stop and reverse signals
- **Signal Logic**: Buy when Close > SAR, Sell when Close < SAR

### 7. **Chande Momentum Oscillator** (`cmo`)
- **Class**: `ChandeMomentumOscillatorIndicator`
- **Parameters**: 
  - `period` (default: 14)
  - `overbought` (default: 50)
  - `oversold` (default: -50)
- **Description**: Momentum oscillator that measures the rate of price changes
- **Signal Logic**: Buy when CMO < oversold, Sell when CMO > overbought

## 🔧 **How to Use Each Indicator**

### **Single Indicator Usage**
```python
from strategies.engine import StrategyBuilder

# Moving Average
ma_strategy = StrategyBuilder.create_single_indicator_strategy('ma', short_window=20, long_window=50)

# RSI
rsi_strategy = StrategyBuilder.create_single_indicator_strategy('rsi', period=14, overbought=75, oversold=25)

# Bollinger Bands
bb_strategy = StrategyBuilder.create_single_indicator_strategy('bollinger', window=20, num_std=2)

# Mean Reversion
mr_strategy = StrategyBuilder.create_single_indicator_strategy('mean_reversion', window=30, entry_z=1.5, exit_z=0.5)

# Money Flow Index
mfi_strategy = StrategyBuilder.create_single_indicator_strategy('mfi', period=14, overbought=80, oversold=20)

# Parabolic SAR
sar_strategy = StrategyBuilder.create_single_indicator_strategy('sar', acceleration=0.02, maximum=0.2)

# Chande Momentum Oscillator
cmo_strategy = StrategyBuilder.create_single_indicator_strategy('cmo', period=14, overbought=50, oversold=-50)

### **Combination Usage**
```python
# Dual indicators
dual_strategy = StrategyBuilder.create_dual_indicator_strategy(
    'ma', 'rsi',
    weight1=0.6, weight2=0.4,
    ind1_short_window=20, ind1_long_window=50,
    ind2_period=14
)

# Triple indicators
triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'rsi', 'bollinger',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_short_window=20, ind1_long_window=50,
    ind2_period=14,
    ind3_window=20, ind3_num_std=2
)
```

## 📈 **Indicator Characteristics**

| Indicator | Best For | Sensitivity | Timeframe |
|-----------|----------|-------------|-----------|
| **MA Crossover** | Trend following | Medium | Medium to Long |
| **RSI** | Momentum/Reversal | High | Short to Medium |
| **Bollinger Bands** | Volatility/Mean reversion | Medium | Short to Medium |
| **Mean Reversion** | Mean reversion | High | Short to Medium |
| **Money Flow Index** | Volume-based momentum | High | Short to Medium |
| **Parabolic SAR** | Trend following | Medium | Medium to Long |
| **Chande Momentum Oscillator** | Momentum analysis | High | Short to Medium |

## 🎯 **Recommended Combinations**

1. **Conservative**: RSI + Bollinger Bands (equal weights)
2. **Trend Following**: MA + RSI (MA higher weight)
3. **Aggressive**: All three indicators with equal weights
4. **Volatility Trading**: Bollinger Bands + Mean Reversion
5. **Volume-Based**: MFI + RSI (volume confirmation)
6. **Comprehensive**: MA + MFI + Bollinger Bands (trend + volume + volatility)
7. **Trend Confirmation**: SAR + MA (trend following)
8. **Momentum Analysis**: CMO + RSI (momentum confirmation)

All indicators are designed to work together seamlessly, and you can combine any 1-3 of them with custom weights and parameters to create your ideal trading strategy!

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


## 🔧 **Detailed Indicator Reference**

### **8. Stochastic Oscillator** (`stochastic`)
- **Parameters**: 
  - `k_period` (default: 14) - Period for %K calculation
  - `d_period` (default: 3) - Period for %D calculation
  - `overbought` (default: 80) - Overbought threshold
  - `oversold` (default: 20) - Oversold threshold
- **Description**: Momentum oscillator that compares closing price to price range
- **Signal Logic**: Buy when %K < oversold, Sell when %K > overbought
- **Best For**: Momentum analysis, overbought/oversold conditions

```python
# Basic Stochastic
stoch_strategy = StrategyBuilder.create_single_indicator_strategy('stochastic', k_period=14, d_period=3)

# Aggressive Stochastic
stoch_agg = StrategyBuilder.create_single_indicator_strategy('stochastic', k_period=10, overbought=85, oversold=15)
```

### **9. Williams %R** (`williams_r`)
- **Parameters**: 
  - `period` (default: 14) - Lookback period
  - `overbought` (default: -20) - Overbought threshold
  - `oversold` (default: -80) - Oversold threshold
- **Description**: Momentum oscillator measuring overbought/oversold levels
- **Signal Logic**: Buy when %R < oversold, Sell when %R > overbought
- **Best For**: Momentum analysis, reversal signals

```python
# Basic Williams %R
williams_strategy = StrategyBuilder.create_single_indicator_strategy('williams_r', period=14)

# Aggressive Williams %R
williams_agg = StrategyBuilder.create_single_indicator_strategy('williams_r', period=10, overbought=-15, oversold=-85)
```

### **10. MACD** (`macd`)
- **Parameters**: 
  - `fast_period` (default: 12) - Fast EMA period
  - `slow_period` (default: 26) - Slow EMA period
  - `signal_period` (default: 9) - Signal line period
- **Description**: Trend-following momentum indicator
- **Signal Logic**: Buy when MACD > Signal, Sell when MACD < Signal
- **Best For**: Trend identification, momentum confirmation

```python
# Standard MACD
macd_strategy = StrategyBuilder.create_single_indicator_strategy('macd', fast_period=12, slow_period=26, signal_period=9)

# Fast MACD
macd_fast = StrategyBuilder.create_single_indicator_strategy('macd', fast_period=8, slow_period=21, signal_period=5)
```

### **11. On-Balance Volume** (`obv`)
- **Parameters**: 
  - `period` (default: 20) - Moving average period
- **Description**: Volume-based indicator measuring buying/selling pressure
- **Signal Logic**: Buy when OBV > OBV MA, Sell when OBV < OBV MA
- **Best For**: Volume analysis, trend confirmation

```python
# Basic OBV
obv_strategy = StrategyBuilder.create_single_indicator_strategy('obv', period=20)

# Short-term OBV
obv_short = StrategyBuilder.create_single_indicator_strategy('obv', period=10)
```

### **12. Exponential Moving Average** (`ema`)
- **Parameters**: 
  - `short_period` (default: 12) - Short EMA period
  - `long_period` (default: 26) - Long EMA period
- **Description**: Trend-following indicator using exponential moving averages
- **Signal Logic**: Buy when Short EMA > Long EMA, Sell when Short EMA < Long EMA
- **Best For**: Trend following, momentum analysis

```python
# Standard EMA
ema_strategy = StrategyBuilder.create_single_indicator_strategy('ema', short_period=12, long_period=26)

# Fast EMA
ema_fast = StrategyBuilder.create_single_indicator_strategy('ema', short_period=8, long_period=21)
```

### **13. VWAP** (`vwap`)
- **Parameters**: 
  - `period` (default: 20) - Calculation period
- **Description**: Volume-weighted average price for fair value assessment
- **Signal Logic**: Buy when Close > VWAP, Sell when Close < VWAP
- **Best For**: Fair value analysis, institutional trading

```python
# Standard VWAP
vwap_strategy = StrategyBuilder.create_single_indicator_strategy('vwap', period=20)

# Short-term VWAP
vwap_short = StrategyBuilder.create_single_indicator_strategy('vwap', period=10)
```

### **14. Average True Range** (`atr`)
- **Parameters**: 
  - `period` (default: 14) - ATR calculation period
  - `multiplier` (default: 2.0) - Band multiplier
- **Description**: Volatility indicator for stop-loss and position sizing
- **Signal Logic**: Buy when Close < Lower Band, Sell when Close > Upper Band
- **Best For**: Volatility analysis, stop-loss placement

```python
# Standard ATR
atr_strategy = StrategyBuilder.create_single_indicator_strategy('atr', period=14, multiplier=2.0)

# Conservative ATR
atr_cons = StrategyBuilder.create_single_indicator_strategy('atr', period=10, multiplier=1.5)
```

### **15. Internal Bar Strength** (`ibs`)
- **Parameters**: 
  - `overbought` (default: 0.8) - Overbought threshold
  - `oversold` (default: 0.2) - Oversold threshold
- **Description**: Measures position of close within the bar's range
- **Signal Logic**: Buy when IBS < oversold, Sell when IBS > overbought
- **Best For**: Intraday analysis, bar strength measurement

```python
# Standard IBS
ibs_strategy = StrategyBuilder.create_single_indicator_strategy('ibs', overbought=0.8, oversold=0.2)

# Aggressive IBS
ibs_agg = StrategyBuilder.create_single_indicator_strategy('ibs', overbought=0.7, oversold=0.3)
```

### **16. Fibonacci Retracement** (`fibonacci`)
- **Parameters**: 
  - `period` (default: 20) - Swing calculation period
  - `retracement_level` (default: 0.618) - Fibonacci level (0.5, 0.618, 0.786)
- **Description**: Support/resistance levels based on Fibonacci ratios
- **Signal Logic**: Buy when Close < Fibonacci level, Sell when Close > Fibonacci level
- **Best For**: Support/resistance analysis, retracement trading

```python
# Golden Ratio (61.8%)
fib_strategy = StrategyBuilder.create_single_indicator_strategy('fibonacci', period=20, retracement_level=0.618)

# 50% Retracement
fib_50 = StrategyBuilder.create_single_indicator_strategy('fibonacci', period=30, retracement_level=0.5)
```

### **17. Percentage Price Oscillator** (`ppo`)
- **Parameters**: 
  - `fast_period` (default: 12) - Fast EMA period
  - `slow_period` (default: 26) - Slow EMA period
  - `signal_period` (default: 9) - Signal line period
- **Description**: MACD variant expressed as percentage
- **Signal Logic**: Buy when PPO > Signal, Sell when PPO < Signal
- **Best For**: MACD alternative, percentage-based analysis

```python
# Standard PPO
ppo_strategy = StrategyBuilder.create_single_indicator_strategy('ppo', fast_period=12, slow_period=26, signal_period=9)

# Fast PPO
ppo_fast = StrategyBuilder.create_single_indicator_strategy('ppo', fast_period=8, slow_period=21, signal_period=5)
```

### **18. Average Directional Index** (`adx`)
- **Parameters**: 
  - `period` (default: 14) - ADX calculation period
  - `threshold` (default: 25.0) - Trend strength threshold
- **Description**: Measures trend strength regardless of direction
- **Signal Logic**: Buy when ADX > threshold (strong trend), Sell when ADX < threshold (weak trend)
- **Best For**: Trend strength analysis, market condition assessment

```python
# Standard ADX
adx_strategy = StrategyBuilder.create_single_indicator_strategy('adx', period=14, threshold=25.0)

# Strong Trend ADX
adx_strong = StrategyBuilder.create_single_indicator_strategy('adx', period=10, threshold=30.0)
```

### **19. Standard Deviation** (`std`)
- **Parameters**: 
  - `period` (default: 20) - Calculation period
  - `multiplier` (default: 2.0) - Band multiplier
- **Description**: Volatility-based bands using standard deviation
- **Signal Logic**: Buy when Close < Lower Band, Sell when Close > Upper Band
- **Best For**: Volatility analysis, statistical trading

```python
# Standard Deviation
std_strategy = StrategyBuilder.create_single_indicator_strategy('std', period=20, multiplier=2.0)

# Conservative Standard Deviation
std_cons = StrategyBuilder.create_single_indicator_strategy('std', period=30, multiplier=1.5)
```

### **20. Relative Volatility Index** (`rvi`)
- **Parameters**: 
  - `period` (default: 14) - Calculation period
  - `overbought` (default: 60) - Overbought threshold
  - `oversold` (default: 40) - Oversold threshold
- **Description**: Volatility-based oscillator
- **Signal Logic**: Buy when RVI < oversold, Sell when RVI > overbought
- **Best For**: Volatility analysis, momentum confirmation

```python
# Standard RVI
rvi_strategy = StrategyBuilder.create_single_indicator_strategy('rvi', period=14)

# Aggressive RVI
rvi_agg = StrategyBuilder.create_single_indicator_strategy('rvi', period=10, overbought=65, oversold=35)
```

---

## 🎯 **Recommended Strategy Combinations**

### **Momentum Strategies**
```python
# Triple Oscillator
momentum_trio = StrategyBuilder.create_triple_indicator_strategy(
    'rsi', 'stochastic', 'williams_r',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_period=14, ind1_overbought=70, ind1_oversold=30,
    ind2_k_period=14, ind2_overbought=80, ind2_oversold=20,
    ind3_period=14, ind3_overbought=-20, ind3_oversold=-80
)

# Volume + Momentum
volume_momentum = StrategyBuilder.create_dual_indicator_strategy(
    'obv', 'rsi',
    weight1=0.6, weight2=0.4,
    ind1_period=20,
    ind2_period=14, ind2_overbought=70, ind2_oversold=30
)
```

### **Trend Following Strategies**
```python
# Classic Trend Trio
trend_trio = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'macd', 'adx',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_short_window=20, ind1_long_window=50,
    ind2_fast_period=12, ind2_slow_period=26, ind2_signal_period=9,
    ind3_period=14, ind3_threshold=25.0
)

# EMA + MACD
ema_macd = StrategyBuilder.create_dual_indicator_strategy(
    'ema', 'macd',
    weight1=0.5, weight2=0.5,
    ind1_short_period=12, ind1_long_period=26,
    ind2_fast_period=12, ind2_slow_period=26, ind2_signal_period=9
)
```

### **Volatility Strategies**
```python
# Volatility Analysis
volatility_combo = StrategyBuilder.create_triple_indicator_strategy(
    'atr', 'std', 'rvi',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_period=14, ind1_multiplier=2.0,
    ind2_period=20, ind2_multiplier=2.0,
    ind3_period=14, ind3_overbought=60, ind3_oversold=40
)

# Bollinger + Standard Deviation
bb_std = StrategyBuilder.create_dual_indicator_strategy(
    'bollinger', 'std',
    weight1=0.6, weight2=0.4,
    ind1_window=20, ind1_num_std=2,
    ind2_period=20, ind2_multiplier=2.0
)
```

### **Support/Resistance Strategies**
```python
# Fibonacci + SAR
fib_sar = StrategyBuilder.create_dual_indicator_strategy(
    'fibonacci', 'sar',
    weight1=0.5, weight2=0.5,
    ind1_period=20, ind1_retracement_level=0.618,
    ind2_acceleration=0.02, ind2_maximum=0.2
)

# VWAP + ATR
vwap_atr = StrategyBuilder.create_dual_indicator_strategy(
    'vwap', 'atr',
    weight1=0.6, weight2=0.4,
    ind1_period=20,
    ind2_period=14, ind2_multiplier=2.0
)
```

### **Volume-Based Strategies**
```python
# Volume Analysis Trio
volume_trio = StrategyBuilder.create_triple_indicator_strategy(
    'obv', 'mfi', 'vwap',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_period=20,
    ind2_period=14, ind2_overbought=80, ind2_oversold=20,
    ind3_period=20
)
```

---

## 🚀 **Advanced Usage Examples**

### **Custom Parameter Optimization**
```python
# Aggressive Day Trading Strategy
day_trading = StrategyBuilder.create_triple_indicator_strategy(
    'stochastic', 'rsi', 'atr',
    weight1=0.4, weight2=0.3, weight3=0.3,
    ind1_k_period=10, ind1_overbought=85, ind1_oversold=15,
    ind2_period=10, ind2_overbought=75, ind2_oversold=25,
    ind3_period=10, ind3_multiplier=1.5
)

# Conservative Swing Trading Strategy
swing_trading = StrategyBuilder.create_triple_indicator_strategy(
    'ma', 'macd', 'adx',
    weight1=0.5, weight2=0.3, weight3=0.2,
    ind1_short_window=50, ind1_long_window=200,
    ind2_fast_period=21, ind2_slow_period=55, ind2_signal_period=13,
    ind3_period=21, ind3_threshold=30.0
)
```

### **Market Condition Adaptation**
```python
# Bull Market Strategy
bull_market = StrategyBuilder.create_dual_indicator_strategy(
    'ema', 'rsi',
    weight1=0.7, weight2=0.3,  # Heavy weight on trend
    ind1_short_period=8, ind1_long_period=21,
    ind2_period=14, ind2_overbought=80, ind2_oversold=40  # Higher oversold
)

# Bear Market Strategy
bear_market = StrategyBuilder.create_dual_indicator_strategy(
    'sar', 'williams_r',
    weight1=0.6, weight2=0.4,
    ind1_acceleration=0.01, ind1_maximum=0.1,  # More conservative
    ind2_period=10, ind2_overbought=-10, ind2_oversold=-90
)
```

---

## 📈 **Indicator Categories**

| Category | Indicators | Best For |
|----------|------------|----------|
| **Trend Following** | MA, EMA, MACD, PPO, ADX, SAR | Trend identification and following |
| **Momentum** | RSI, Stochastic, Williams %R, CMO, RVI | Momentum analysis and reversals |
| **Volume** | OBV, MFI, VWAP | Volume analysis and confirmation |
| **Volatility** | Bollinger Bands, ATR, Standard Deviation | Volatility analysis and bands |
| **Support/Resistance** | Fibonacci, IBS | Support/resistance levels |
| **Mean Reversion** | Mean Reversion | Statistical arbitrage |

---

## 🎯 **Strategy Building Tips**

1. **Start Simple**: Begin with 1-2 indicators to understand their behavior
2. **Combine Categories**: Mix different indicator categories for comprehensive analysis
3. **Weight Appropriately**: Give higher weights to indicators that perform better for your asset
4. **Parameter Tuning**: Adjust parameters based on your trading timeframe and style
5. **Market Conditions**: Adapt strategies based on bull/bear market conditions
6. **Risk Management**: Use ATR or Standard Deviation for position sizing
7. **Confirmation**: Use multiple indicators to confirm signals

---

## 🧪 **Testing Your Strategies**

Run the comprehensive test to verify all indicators work:

```bash
python test_strategies/test_all_indicators.py
```

This will test:
- ✅ All 20 indicators individually
- ✅ Various indicator combinations
- ✅ Signal analysis
- ✅ Custom parameters
- ✅ Advanced combinations

---

## 📊 **Complete System Features**

- **20 Professional Indicators**: All major technical analysis indicators
- **Flexible Combinations**: Any 1-3 indicators with custom weights
- **Parameter Customization**: All indicators have configurable parameters
- **Signal Analysis**: Detailed signal generation and analysis
- **Trade Summary**: Performance metrics and trade statistics
- **Error Handling**: Robust error handling and validation
- **Extensible**: Easy to add new indicators

Your Algonex system is now a comprehensive trading platform with professional-grade indicators! 