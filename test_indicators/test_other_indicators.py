import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import MeanReversionIndicator, CompositeStrategy

def create_mean_reversion_test_data():
    """Creates a dataset to test the Mean Reversion indicator."""
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

def test_mean_reversion_indicator():
    """Tests the Mean Reversion indicator for correct signal generation."""
    print("\\n--- Testing Mean Reversion Indicator ---")

    data = create_mean_reversion_test_data()
    indicator = MeanReversionIndicator(window=5, entry_z=1.0, exit_z=0.0)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_MR", data=data)
    trades = engine.run()

    # A buy signal should be generated when z-score crosses up through -entry_z,
    # and a sell signal when it crosses down through entry_z.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07'), 90.0),
        ('SELL', pd.Timestamp('2023-01-08'), 95.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Mean Reversion Indicator test passed")

from strategies.strategies import IBSIndicator

def create_ibs_test_data():
    """Creates a dataset to test the IBS indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 98, 96, 94, 92, 94, 96, 98, 100, 102],
        'High': [105, 103, 101, 99, 97, 99, 101, 103, 105, 107],
        'Low': [95, 93, 91, 89, 87, 89, 91, 93, 95, 97],
        # Close near low, then near high
        'Close': [96, 94, 92, 90, 88, 98, 100, 102, 104, 106],
        'Volume': [1000] * 10
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_ibs_indicator():
    """Tests the IBS indicator for correct signal generation."""
    print("\\n--- Testing IBS Indicator ---")

    data = create_ibs_test_data()
    indicator = IBSIndicator(overbought=0.8, oversold=0.2)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_IBS", data=data)
    trades = engine.run()

    # A buy signal should be generated when IBS crosses above oversold,
    # and a sell signal when it crosses below overbought.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07'), 96.0),
        ('SELL', pd.Timestamp('2023-01-08'), 98.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ IBS Indicator test passed")


from strategies.strategies import FibonacciRetracementIndicator

def create_fib_test_data():
    """Creates a dataset to test the Fibonacci Retracement indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 110, 120, 115, 110, 105, 100, 105, 110, 115],
        'High': [105, 115, 125, 120, 115, 110, 105, 110, 115, 120],
        'Low': [95, 105, 115, 110, 105, 100, 95, 100, 105, 110],
        'Close': [100, 110, 120, 115, 110, 105, 100, 105, 110, 115],
        'Volume': [1000] * 10
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_fib_indicator():
    """Tests the Fibonacci Retracement indicator for correct signal generation."""
    print("\\n--- Testing Fibonacci Retracement Indicator ---")

    data = create_fib_test_data()
    indicator = FibonacciRetracementIndicator(period=5, retracement_level=0.5)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_FIB", data=data)
    trades = engine.run()

    # A buy signal should be generated when price crosses above the fib level,
    # and a sell signal when it crosses below.
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('SELL', pd.Timestamp('2023-01-05'), 110.0),
        ('BUY', pd.Timestamp('2023-01-09'), 110.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'SELL'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'BUY'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Fibonacci Retracement Indicator test passed")


if __name__ == "__main__":
    test_mean_reversion_indicator()
    test_ibs_indicator()
    test_fib_indicator()
