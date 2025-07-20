#!/usr/bin/env python3
"""Test script for the Money Flow Index indicator."""

import sys
import os
# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

def test_mfi_indicator():
    """Test the Money Flow Index indicator."""
    print("Testing Money Flow Index Indicator...")
    
    # Test 1: Single MFI strategy
    print("\n1. Testing Single MFI Strategy")
    try:
        mfi_strategy = StrategyBuilder.create_single_indicator_strategy('mfi', period=14)
        engine = TradingEngine(mfi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ MFI strategy works: {summary['total_trades']} trades")
        print(f"   ✓ Buy trades: {summary['buy_trades']}")
        print(f"   ✓ Sell trades: {summary['sell_trades']}")
    except Exception as e:
        print(f"   ✗ MFI strategy failed: {e}")
    
    # Test 2: MFI with custom parameters
    print("\n2. Testing MFI with Custom Parameters")
    try:
        mfi_custom = StrategyBuilder.create_single_indicator_strategy(
            'mfi', 
            period=10, 
            overbought=75, 
            oversold=25
        )
        engine = TradingEngine(mfi_custom, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Custom MFI works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Custom MFI failed: {e}")
    
    # Test 3: MFI + RSI combination
    print("\n3. Testing MFI + RSI Combination")
    try:
        mfi_rsi_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'mfi', 'rsi',
            weight1=0.5, weight2=0.5,
            ind1_period=14, ind1_overbought=80, ind1_oversold=20,
            ind2_period=14, ind2_overbought=70, ind2_oversold=30
        )
        engine = TradingEngine(mfi_rsi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ MFI + RSI combination works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ MFI + RSI combination failed: {e}")
    
    # Test 4: Triple indicator with MFI
    print("\n4. Testing Triple Indicator with MFI")
    try:
        triple_mfi_strategy = StrategyBuilder.create_triple_indicator_strategy(
            'ma', 'mfi', 'bollinger',
            weight1=0.4, weight2=0.3, weight3=0.3,
            ind1_short_window=20, ind1_long_window=50,
            ind2_period=14, ind2_overbought=80, ind2_oversold=20,
            ind3_window=20, ind3_num_std=2
        )
        engine = TradingEngine(triple_mfi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Triple indicator with MFI works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Triple indicator with MFI failed: {e}")
    
    print("\n✓ All MFI tests completed!")

if __name__ == "__main__":
    test_mfi_indicator() 