import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import MoneyFlowIndexIndicator, CompositeStrategy

def create_mfi_test_data():
    """Creates a dataset to test the MFI indicator."""
    # Re-using the rsi test data as it's suitable for MFI as well
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15']),
        'Open': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'High': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Low': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Close': [100, 95, 90, 85, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1300, 1200, 1100, 1000, 1100, 1200, 1300, 1400, 1500, 1600]
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_mfi_indicator():
    """Tests the Money Flow Index indicator for correct signal generation."""
    print("\\n--- Testing Money Flow Index Indicator ---")

    data = create_mfi_test_data()
    indicator = MoneyFlowIndexIndicator(period=5, overbought=80, oversold=20)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_MFI", data=data)
    trades = engine.run()

    # A buy signal should be generated when MFI is oversold,
    # and a sell signal when it is overbought.
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

    print("   ✓ Money Flow Index Indicator test passed")

from strategies.strategies import OBVIndicator

def create_obv_test_data():
    """Creates a dataset to test the OBV indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 101, 102, 103, 104, 103, 102, 101, 100, 99],
        'High': [101, 102, 103, 104, 105, 104, 103, 102, 101, 100],
        'Low': [99, 100, 101, 102, 103, 102, 101, 100, 99, 98],
        'Close': [100, 101, 102, 103, 104, 103, 102, 101, 100, 99],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_obv_indicator():
    """Tests the OBV indicator for correct signal generation."""
    print("\\n--- Testing OBV Indicator ---")

    data = create_obv_test_data()
    indicator = OBVIndicator(period=5)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_OBV", data=data)
    trades = engine.run()

    # A buy signal should be generated when OBV crosses above its MA,
    # and a sell signal when it crosses below.

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 102.0),
        ('SELL', pd.Timestamp('2023-01-08'), 101.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ OBV Indicator test passed")


from strategies.strategies import VWAPIndicator

def create_vwap_test_data():
    """Creates a dataset to test the VWAP indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 101, 102, 103, 104, 103, 102, 101, 100, 99],
        'High': [101, 102, 103, 104, 105, 104, 103, 102, 101, 100],
        'Low': [99, 100, 101, 102, 103, 102, 101, 100, 99, 98],
        'Close': [100, 101, 102, 103, 104, 103, 102, 101, 100, 99],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_vwap_indicator():
    """Tests the VWAP indicator for correct signal generation."""
    print("\\n--- Testing VWAP Indicator ---")

    data = create_vwap_test_data()
    indicator = VWAPIndicator(period=5)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_VWAP", data=data)
    trades = engine.run()

    # A buy signal should be generated when Close crosses above VWAP,
    # and a sell signal when it crosses below.

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 102.0),
        ('SELL', pd.Timestamp('2023-01-08'), 101.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ VWAP Indicator test passed")


if __name__ == "__main__":
    test_mfi_indicator()
    test_obv_indicator()
    test_vwap_indicator()
