#!/usr/bin/env python3
"""Simple test of the Algonex strategy system."""

import sys
import os
# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

def test_basic_functionality():
    """Test basic strategy functionality."""
    print("Testing Algonex Strategy System...")
    
    # Test 1: Default strategy
    print("\n1. Testing Default Strategy")
    try:
        default_strategy = StrategyBuilder.create_default_strategy()
        engine = TradingEngine(default_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Default strategy works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Default strategy failed: {e}")
    
    # Test 2: Single RSI strategy
    print("\n2. Testing Single RSI Strategy")
    try:
        rsi_strategy = StrategyBuilder.create_single_indicator_strategy('rsi', period=14)
        engine = TradingEngine(rsi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ RSI strategy works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ RSI strategy failed: {e}")
    
    # Test 3: Dual indicator strategy
    print("\n3. Testing Dual Indicator Strategy")
    try:
        dual_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'ma', 'rsi',
            weight1=0.6, weight2=0.4,
            ind1_short_window=20, ind1_long_window=50,
            ind2_period=14
        )
        engine = TradingEngine(dual_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Dual strategy works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Dual strategy failed: {e}")
    
    # Test 4: Triple indicator strategy
    print("\n4. Testing Triple Indicator Strategy")
    try:
        triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
            'ma', 'rsi', 'bollinger',
            weight1=0.4, weight2=0.3, weight3=0.3,
            ind1_short_window=20, ind1_long_window=50,
            ind2_period=14,
            ind3_window=20, ind3_num_std=2
        )
        engine = TradingEngine(triple_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Triple strategy works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Triple strategy failed: {e}")
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    test_basic_functionality() 