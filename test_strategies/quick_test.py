#!/usr/bin/env python3
"""Quick test to verify all 7 indicators are working."""

import sys
import os
# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

def quick_test():
    """Quick test of all indicators."""
    print("Quick Test: All 7 Indicators\n")
    
    # Define all indicators with their basic parameters
    indicators_config = {
        'ma': {'short_window': 20, 'long_window': 50},
        'rsi': {'period': 14},
        'bollinger': {'window': 20, 'num_std': 2},
        'mean_reversion': {'window': 20},
        'mfi': {'period': 14},
        'sar': {'acceleration': 0.02, 'maximum': 0.2},
        'cmo': {'period': 14}
    }
    
    results = {}
    
    # Test each indicator
    for indicator, params in indicators_config.items():
        print(f"Testing {indicator.upper()}...")
        try:
            strategy = StrategyBuilder.create_single_indicator_strategy(indicator, **params)
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            summary = engine.get_trade_summary()
            results[indicator] = summary['total_trades']
            print(f"  ✓ {indicator.upper()}: {summary['total_trades']} trades")
        except Exception as e:
            results[indicator] = f"ERROR: {e}"
            print(f"  ✗ {indicator.upper()}: {e}")
    
    # Summary
    print(f"\n=== Summary ===")
    for indicator, result in results.items():
        status = "✓" if isinstance(result, int) else "✗"
        print(f"{status} {indicator.upper()}: {result}")
    
    # Test a combination
    print(f"\n=== Testing Combination ===")
    try:
        combo_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'sar', 'cmo',
            weight1=0.5, weight2=0.5,
            ind1_acceleration=0.02, ind1_maximum=0.2,
            ind2_period=14
        )
        engine = TradingEngine(combo_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"✓ SAR + CMO combination: {summary['total_trades']} trades")
    except Exception as e:
        print(f"✗ SAR + CMO combination failed: {e}")
    
    print(f"\n=== Test Complete ===")
    working_count = sum(1 for result in results.values() if isinstance(result, int))
    print(f"Working indicators: {working_count}/7")

if __name__ == "__main__":
    quick_test() 