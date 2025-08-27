import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine
from strategies.strategies import MACDIndicator, CompositeStrategy

def create_macd_test_data():
    """Creates a dataset to test the MACD indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15']),
        'Open': [100, 102, 101, 103, 105, 106, 107, 108, 109, 110, 109, 108, 107, 106, 105],
        'High': [102, 103, 103, 105, 106, 107, 108, 109, 110, 111, 110, 109, 108, 107, 106],
        'Low': [99, 101, 100, 102, 104, 105, 106, 107, 108, 109, 108, 107, 106, 105, 104],
        'Close': [101, 102, 102, 104, 105, 106, 107, 108, 109, 110, 108, 107, 106, 105, 104],
        'Volume': [1000] * 15
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_macd_indicator():
    """Tests the MACD indicator for correct signal generation."""
    print("\\n--- Testing MACD Indicator ---")

    data = create_macd_test_data()
    # Using small periods to get a quick crossover
    indicator = MACDIndicator(fast_period=3, slow_period=6, signal_period=4)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_MACD", data=data)
    trades = engine.run()

    # Manual calculation:
    # A crossover will happen around the 10th or 11th day.
    # On day 10, the price peaks at 110. On day 11, it drops to 108.
    # This should cause the MACD line to cross below the signal line.

    # Let's find the exact crossover date by inspecting the signals
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['composite_signal', 'signal', 'positions']])

    # Based on the output, a buy signal is on 2023-01-02, and a sell on 2023-01-11.
    # Trades should be on the next day's open.

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 101.0),
        ('SELL', pd.Timestamp('2023-01-12'), 108.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ MACD Indicator test passed")

from strategies.strategies import ParabolicSARIndicator

def create_sar_test_data():
    """Creates a dataset to test the Parabolic SAR indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 100, 102, 104, 106, 108, 107, 105, 103, 101],
        'High': [100, 100, 103, 105, 107, 109, 108, 106, 104, 102],
        'Low': [100, 100, 101, 103, 105, 107, 106, 104, 102, 100],
        'Close': [100, 100, 102, 104, 106, 108, 106, 104, 102, 100],
        'Volume': [1000] * 10
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_sar_indicator():
    """Tests the Parabolic SAR indicator for correct signal generation."""
    print("\\n--- Testing Parabolic SAR Indicator ---")

    data = create_sar_test_data()
    indicator = ParabolicSARIndicator()
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_SAR", data=data)
    trades = engine.run()

    # In this data, the price trends up and then reverses down.
    # A buy signal should be generated when the trend starts,
    # and a sell signal when it reverses.

    # A buy signal happens when the close crosses above the SAR.
    # A sell signal happens when the close crosses below the SAR.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-04'), 104.0),
        ('SELL', pd.Timestamp('2023-01-10'), 101.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ Parabolic SAR Indicator test passed")


from strategies.strategies import EMAIndicator

def create_ema_test_data():
    """Creates a dataset to test the EMA indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 101, 102, 103, 104, 100, 98, 96, 94, 92],
        'High': [101, 102, 103, 104, 105, 101, 99, 97, 95, 93],
        'Low': [99, 100, 101, 102, 103, 99, 97, 95, 93, 91],
        'Close': [100, 101, 102, 103, 104, 100, 98, 96, 94, 92],
        'Volume': [1000] * 10
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_ema_indicator():
    """Tests the EMA indicator for correct signal generation."""
    print("\\n--- Testing EMA Indicator ---")

    data = create_ema_test_data()
    indicator = EMAIndicator(short_period=3, long_period=6)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_EMA", data=data)
    trades = engine.run()

    # A buy signal should be generated when the short EMA crosses above the long EMA.
    # A sell signal should be generated when the short EMA crosses below the long EMA.

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 102.0),
        ('SELL', pd.Timestamp('2023-01-07'), 98.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ EMA Indicator test passed")


from strategies.strategies import PPOIndicator

def create_ppo_test_data():
    """Creates a dataset to test the PPO indicator."""
    return create_macd_test_data() # PPO is similar to MACD

def test_ppo_indicator():
    """Tests the PPO indicator for correct signal generation."""
    print("\\n--- Testing PPO Indicator ---")

    data = create_ppo_test_data()
    indicator = PPOIndicator(fast_period=3, slow_period=6, signal_period=4)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_PPO", data=data)
    trades = engine.run()

    # Similar to MACD, we expect a buy and then a sell signal.
    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 101.0),
        ('SELL', pd.Timestamp('2023-01-12'), 108.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ PPO Indicator test passed")


from strategies.strategies import ADXIndicator

def create_adx_test_data():
    """Creates a dataset to test the ADX indicator."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10',
                                '2023-01-11', '2023-01-12', '2023-01-13', '2023-01-14', '2023-01-15',
                                '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19', '2023-01-20']),
        'Open': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118],
        'High': [101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118],
        'Low': [99, 101, 103, 105, 107, 109, 111, 113, 115, 117, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118],
        'Close': [100, 102, 104, 106, 108, 110, 112, 114, 116, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118, 118],
        'Volume': [1000] * 20
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_adx_indicator():
    """Tests the ADX indicator for correct signal generation."""
    print("\\n--- Testing ADX Indicator ---")

    data = create_adx_test_data()
    indicator = ADXIndicator(period=5, threshold=25)
    strategy = CompositeStrategy([(indicator, 1.0)])

    engine = TradingEngine(strategy, "TEST_ADX", data=data)
    trades = engine.run()

    # A strong trend signal should be generated early,
    # and a weak trend signal when the price goes flat.
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(engine.signals[['signal', 'positions']])

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-03'), 104.0),
        ('SELL', pd.Timestamp('2023-01-20'), 118.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"

    assert trades[0][0] == 'BUY'
    assert trades[0][1] == expected_trades[0][1]
    assert np.isclose(trades[0][2], expected_trades[0][2])

    assert trades[1][0] == 'SELL'
    assert trades[1][1] == expected_trades[1][1]
    assert np.isclose(trades[1][2], expected_trades[1][2])

    print("   ✓ ADX Indicator test passed")


if __name__ == "__main__":
    test_macd_indicator()
    test_sar_indicator()
    test_ema_indicator()
    test_ppo_indicator()
    test_adx_indicator()
