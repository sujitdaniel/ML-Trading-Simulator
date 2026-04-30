# ML Trading Simulator Strategy Usage Guide

## Overview

The strategy engine supports:

- Default strategy (`create_default_strategy`)
- Single indicator strategies
- Dual/triple indicator combinations with weights
- Hybrid ML + indicator strategies

Indicator creation is handled by `StrategyBuilder` in `strategies/engine.py`.

## Strategy Organization

Indicator IDs currently supported in code:

- `ma`, `rsi`, `bollinger`, `mean_reversion`, `mfi`
- `sar`, `cmo`, `stochastic`, `williams_r`, `macd`
- `obv`, `ema`, `vwap`, `atr`, `ibs`
- `fibonacci`, `ppo`, `adx`, `std`, `rvi`

These IDs map to indicator classes in `strategies/strategies.py` through `StrategyBuilder._INDICATOR_MAP`.

## Quick Start (Python)

```python
from strategies.engine import TradingEngine, StrategyBuilder

# Default strategy
strategy = StrategyBuilder.create_default_strategy()
engine = TradingEngine(strategy, "AAPL")
engine.run()
print(engine.get_trade_summary())
```

## Single, Dual, and Triple Indicator Examples

### Single indicator

```python
rsi_strategy = StrategyBuilder.create_single_indicator_strategy("rsi", period=14)
engine = TradingEngine(rsi_strategy, "AAPL")
engine.run()
```

### Dual indicator

```python
dual_strategy = StrategyBuilder.create_dual_indicator_strategy(
    "ma",
    "rsi",
    weight1=0.6,
    weight2=0.4,
    ind1_short_window=20,
    ind1_long_window=50,
    ind2_period=14,
)
engine = TradingEngine(dual_strategy, "AAPL")
engine.run()
```

### Triple indicator

```python
triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
    "ma",
    "rsi",
    "bollinger",
    weight1=0.4,
    weight2=0.3,
    weight3=0.3,
    ind1_short_window=20,
    ind1_long_window=50,
    ind2_period=14,
    ind3_window=20,
    ind3_num_std=2,
)
engine = TradingEngine(triple_strategy, "AAPL")
engine.run()
```

## Hybrid Strategy and ML Models

The backend supports hybrid runs (`strategy=hybrid`) that combine indicators with one ML model.

Supported ML model IDs:

- `logistic`
- `random_forest`
- `xgboost`
- `gradient_boosting`
- `svm`
- `knn`
- `lstm`

For hybrid requests, provide:

- indicator list (1-3 indicators),
- indicator weights,
- `ml_weight`,
- optional `ml_model`.

## Run a Sample Backtest (API)

```bash
curl -X POST "http://127.0.0.1:8000/backtest?strategy=hybrid" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 10000,
    "ml_weight": 0.4,
    "ml_model": "logistic",
    "indicators": [
      {
        "id": "rsi",
        "name": "Relative Strength Index",
        "weight": 0.6,
        "parameters": {
          "period": 14,
          "overbought": 70,
          "oversold": 30
        }
      }
    ]
  }'
```

## Validate and Test Strategy Behavior

```bash
# API/integration checks
python test_api_connection.py
python test_frontend_backend.py

# Indicator tests
pytest test_indicators
python test_indicators/quick_test.py
```

## Notes

- Backtests are simulation outputs based on historical data and selected parameters.
- Results depend heavily on data range, indicator settings, and strategy mode.
- Use this project for experimentation and evaluation, not as a production trading system.