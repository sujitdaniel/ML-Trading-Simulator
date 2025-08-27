import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import HybridMLIndicatorStrategy, RSIIndicator

def mock_ml_func(data):
    """A mock ML function that returns a predictable signal."""
    signals = pd.DataFrame(index=data.index)
    signals['ml_signal'] = 0
    signals.loc['2023-01-05', 'ml_signal'] = 1  # Buy signal
    signals.loc['2023-01-10', 'ml_signal'] = -1 # Sell signal
    return signals, {}

def create_hybrid_test_data():
    """Creates a dataset to test the hybrid strategy."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15']),
        'Open': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'High': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Low': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Close': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Volume': [1000] * 15
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_hybrid_strategy():
    """Tests the HybridMLIndicatorStrategy for correct signal combination."""
    print("\\n--- Testing Hybrid ML Indicator Strategy ---")

    data = create_hybrid_test_data()

    # We will use RSI as the indicator
    rsi_indicator = RSIIndicator(period=5, overbought=70, oversold=30)

    # The hybrid strategy will combine the RSI signal with the mock ML signal
    strategy = HybridMLIndicatorStrategy(
        indicators=[(rsi_indicator, 0.0)], # weight is 0
        ml_weight=1.0,
        signal_threshold=0.5,
        ml_func=mock_ml_func
    )

    engine = TradingEngine(strategy, "TEST_HYBRID", data=data, ml_func=mock_ml_func)
    trades = engine.run(strategy_type="ml")

    # We need to analyze the composite signal to determine the expected trades.
    # The composite signal is a weighted average of the RSI signal and the ML signal.
    # A trade is generated when the composite signal crosses the threshold.

    # Let's inspect the signals to be sure.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals)

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-06'), 85.0),
        ('SELL', pd.Timestamp('2023-01-11'), 110.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Hybrid ML Indicator Strategy test passed")

if __name__ == "__main__":
    test_hybrid_strategy()
