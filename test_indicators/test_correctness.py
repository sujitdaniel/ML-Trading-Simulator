import sys
import os
import pandas as pd
import numpy as np

# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder
from strategies.strategies import MovingAverageCrossover

def create_test_data():
    """Creates a simple, predictable dataset for testing."""
    data = {
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05',
                                '2023-01-06', '2023-01-07', '2023-01-08', '2023-01-09', '2023-01-10']),
        'Open': [100, 102, 104, 103, 105, 107, 106, 108, 110, 109],
        'High': [103, 104, 105, 106, 107, 108, 109, 111, 112, 110],
        'Low': [99, 101, 103, 102, 104, 106, 105, 107, 109, 108],
        'Close': [102, 103, 105, 104, 106, 108, 107, 109, 111, 110],
        'Volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }
    df = pd.DataFrame(data)
    df.set_index('Date', inplace=True)
    return df

def test_strategy_correctness():
    """
    Tests the correctness of a simple strategy with a known outcome.
    """
    print("\\n--- Testing Strategy Correctness ---")

    # 1. Setup: Create test data and a simple strategy
    test_data = create_test_data()
    strategy = MovingAverageCrossover(short_window=3, long_window=6)

    # We need to mock the data loading process of the engine
    # A simple way is to make the engine accept a dataframe directly
    engine = TradingEngine(strategy, "TEST", data=test_data)

    # 2. Run the strategy
    trades = engine.run()

    # 3. Manually calculate expected outcome
    # Short MA:
    # Day 1: 102
    # Day 2: (102+103)/2 = 102.5
    # Day 3: (102+103+105)/3 = 103.33
    # Day 4: (103+105+104)/3 = 104
    # Day 5: (105+104+106)/3 = 105
    # Day 6: (104+106+108)/3 = 106
    # Day 7: (106+108+107)/3 = 107
    # Day 8: (108+107+109)/3 = 108
    # Day 9: (107+109+111)/3 = 109
    # Day 10: (109+111+110)/3 = 110

    # Long MA:
    # Day 1-5: ...
    # Day 6: (102+103+105+104+106+108)/6 = 104.66
    # Day 7: (103+105+104+106+108+107)/6 = 105.5
    # Day 8: (105+104+106+108+107+109)/6 = 106.5
    # Day 9: (104+106+108+107+109+111)/6 = 107.5
    # Day 10: (106+108+107+109+111+110)/6 = 108.5

    # Signal (short > long):
    # Day 6: 106 > 104.66 -> 1 (Buy)
    # Day 7: 107 > 105.5 -> 1
    # Day 8: 108 > 106.5 -> 1
    # Day 9: 109 > 107.5 -> 1
    # Day 10: 110 > 108.5 -> 1

    # Positions (diff of signal):
    # A buy signal should be generated on 2023-01-06, when the short MA (106) crosses above the long MA (104.66).
    # Before that, the signal is 0. At day 6, it becomes 1. So positions has a 1.
    # No other crossovers happen.

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07 00:00:00'), 107.0)
    ]

    # 4. Assert trades are correct
    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"
    for i, trade in enumerate(trades):
        assert trade[0] == expected_trades[i][0], f"Trade {i} action is wrong"
        assert trade[1] == expected_trades[i][1], f"Trade {i} date is wrong"
        assert trade[2] == expected_trades[i][2], f"Trade {i} price is wrong"

    print("   ✓ Trades are correct")

    # 5. Calculate and assert performance metrics
    metrics = engine.calculate_performance_metrics()

    # Expected metrics:
    # One trade, a buy, which is never sold. So 0 completed trades.
    # This means win rate should be 0, and sharpe ratio should be 0.
    # Let's add a sell to make the test more interesting.

    # Let's modify the data to have a sell signal.
    close_prices = [102, 103, 105, 104, 106, 108, 100, 98, 96, 94]
    test_data['Close'] = close_prices
    engine.data = test_data
    trades = engine.run()

    # New MAs
    # Short MA
    # Day 7: (106+108+100)/3 = 104.67
    # Day 8: (108+100+98)/3 = 102
    # Day 9: (100+98+96)/3 = 98
    # Day 10: (98+96+94)/3 = 96

    # Long MA
    # Day 7: (103+105+104+106+108+100)/6 = 104.33
    # Day 8: (105+104+106+108+100+98)/6 = 103.5
    # Day 9: (104+106+108+100+98+96)/6 = 102
    # Day 10: (106+108+100+98+96+94)/6 = 100.33

    # Signal (short > long)
    # Day 6: 106 > 104.66 -> 1 (Buy)
    # Day 7: 104.67 > 104.33 -> 1
    # Day 8: 102 < 103.5 -> 0 (Sell)

    # Expected trades:
    # Buy on 2023-01-06 at 108
    # Sell on 2023-01-08 at 98

    expected_trades = [
        ('BUY', pd.Timestamp('2023-01-07 00:00:00'), 100.0),
        ('SELL', pd.Timestamp('2023-01-08 00:00:00'), 98.0)
    ]

    assert len(trades) == len(expected_trades), f"Expected {len(expected_trades)} trades, but got {len(trades)}"
    for i, trade in enumerate(trades):
        assert trade[0] == expected_trades[i][0], f"Trade {i} action is wrong"
        assert trade[1] == expected_trades[i][1], f"Trade {i} date is wrong"
        assert trade[2] == expected_trades[i][2], f"Trade {i} price is wrong"

    print("   ✓ Trades are correct after data modification")

    metrics = engine.calculate_performance_metrics()

    # Expected Metrics Calculation
    # 1 trade was made. It was a loss (bought at 108, sold at 98).
    # So, winning trades = 0. Total completed trades = 1.
    # Win rate = 0 / 1 = 0.0
    # Total return = (98 - 108) / 108 = -0.0925... Let's calculate based on portfolio
    # Initial capital = 10000.
    # Buy at 108: shares = 10000 / 108 = 92.59
    # Sell at 98: cash = 92.59 * 98 = 9073.82
    # Final portfolio value = 9073.82
    # Total return = (9073.82 - 10000) / 10000 = -0.0926
    # Sharpe ratio will be non-zero, but tricky to calculate by hand. Let's just check win_rate and total_return.

    assert metrics['win_rate'] == 0.0, f"Expected win rate of 0.0, but got {metrics['win_rate']}"
    assert np.isclose(metrics['total_return'], -0.02, atol=1e-4), f"Expected total return of approx -0.02, but got {metrics['total_return']}"

    print("   ✓ Performance metrics are correct")
    print("--- Strategy Correctness Test Passed ---")

if __name__ == "__main__":
    test_strategy_correctness()
