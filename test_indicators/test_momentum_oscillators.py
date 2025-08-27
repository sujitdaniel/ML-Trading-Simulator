import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import RSIIndicator, CompositeStrategy

def create_rsi_test_data():
    """Creates a dataset to test the RSI indicator."""
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

def test_rsi_indicator():
    """Tests the RSI indicator for correct signal generation."""
    print("\\n--- Testing RSI Indicator ---")

    data = create_rsi_test_data()
    indicator = RSIIndicator(period=5, overbought=70, oversold=30)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_RSI", data=data)
    trades = engine.run()

    # A buy signal should be generated when RSI is oversold,
    # and a sell signal when it is overbought.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-08'), 95.0),
        ('SELL', pd.Timestamp('2023-01-09'), 100.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ RSI Indicator test passed")

from strategies.strategies import StochasticOscillatorIndicator

def test_stochastic_indicator():
    """Tests the Stochastic Oscillator indicator for correct signal generation."""
    print("\\n--- Testing Stochastic Oscillator Indicator ---")

    data = create_rsi_test_data()
    indicator = StochasticOscillatorIndicator(k_period=5, d_period=3, overbought=80, oversold=20)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_STOCHASTIC", data=data)
    trades = engine.run()

    # A buy signal should be generated when the stochastic is oversold,
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

    print("   ✓ Stochastic Oscillator Indicator test passed")


from strategies.strategies import ChandeMomentumOscillatorIndicator

def test_cmo_indicator():
    """Tests the Chande Momentum Oscillator indicator for correct signal generation."""
    print("\\n--- Testing Chande Momentum Oscillator Indicator ---")

    data = create_rsi_test_data()
    indicator = ChandeMomentumOscillatorIndicator(period=5, overbought=50, oversold=-50)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_CMO", data=data)
    trades = engine.run()

    # A buy signal should be generated when CMO is oversold,
    # and a sell signal when it is overbought.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-08'), 95.0),
        ('SELL', pd.Timestamp('2023-01-09'), 100.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Chande Momentum Oscillator Indicator test passed")


if __name__ == "__main__":
    test_rsi_indicator()
    test_stochastic_indicator()
    test_cmo_indicator()
