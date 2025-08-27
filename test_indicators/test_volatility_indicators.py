import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import BollingerBandsIndicator, CompositeStrategy

def create_volatility_test_data():
    """Creates a dataset for volatility indicators."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15']),
        'Open': [100, 95, 90, 85, 80, 82, 84, 86, 88, 90, 100, 110, 120, 130, 140],
        'High': [102, 97, 92, 87, 82, 84, 86, 88, 90, 92, 102, 112, 122, 132, 142],
        'Low': [98, 93, 88, 83, 78, 80, 82, 84, 86, 88, 98, 108, 118, 128, 138],
        'Close': [100, 95, 90, 85, 80, 82, 84, 86, 88, 90, 100, 110, 120, 130, 140],
        'Volume': [1000] * 15
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_bb_indicator():
    """Tests the Bollinger Bands indicator for correct signal generation."""
    print("\\n--- Testing Bollinger Bands Indicator ---")

    data = create_volatility_test_data()
    indicator = BollingerBandsIndicator(window=5, num_std=2)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_BB", data=data)
    trades = engine.run()

    # A buy signal should be generated when price crosses above the lower band,
    # and a sell signal when it crosses below the upper band.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07'), 84.0),
        ('SELL', pd.Timestamp('2023-01-08'), 86.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Bollinger Bands Indicator test passed")

from strategies.strategies import RVIIndicator

def test_rvi_indicator():
    """Tests the RVI indicator for correct signal generation."""
    print("\\n--- Testing RVI Indicator ---")

    data = create_volatility_test_data()
    indicator = RVIIndicator(period=5, overbought=60, oversold=40)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_RVI", data=data)
    trades = engine.run()

    # A buy signal should be generated when RVI crosses above the oversold line,
    # and a sell signal when it crosses below the overbought line.
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07'), 84.0),
        ('SELL', pd.Timestamp('2023-01-15'), 140.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ RVI Indicator test passed")


if __name__ == "__main__":
    test_bb_indicator()
    test_rvi_indicator()
