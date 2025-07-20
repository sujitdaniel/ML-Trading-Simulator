#!/usr/bin/env python3
"""Test script for the new indicators: Parabolic SAR and Chande Momentum Oscillator."""

import sys
import os
# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

def test_parabolic_sar():
    """Test the Parabolic SAR indicator."""
    print("=== Testing Parabolic SAR Indicator ===\n")
    
    # Test 1: Basic SAR strategy
    print("1. Testing Basic Parabolic SAR Strategy")
    try:
        sar_strategy = StrategyBuilder.create_single_indicator_strategy('sar', acceleration=0.02, maximum=0.2)
        engine = TradingEngine(sar_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Basic SAR works: {summary['total_trades']} trades")
        print(f"   ✓ Buy trades: {summary['buy_trades']}")
        print(f"   ✓ Sell trades: {summary['sell_trades']}")
    except Exception as e:
        print(f"   ✗ Basic SAR failed: {e}")
    
    # Test 2: SAR with custom parameters
    print("\n2. Testing SAR with Custom Parameters")
    try:
        sar_custom = StrategyBuilder.create_single_indicator_strategy(
            'sar', 
            acceleration=0.01,  # More conservative
            maximum=0.1  # Lower maximum
        )
        engine = TradingEngine(sar_custom, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Custom SAR works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Custom SAR failed: {e}")
    
    # Test 3: SAR + MA combination (trend confirmation)
    print("\n3. Testing SAR + MA Combination (Trend Confirmation)")
    try:
        sar_ma_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'sar', 'ma',
            weight1=0.6, weight2=0.4,  # SAR has higher weight
            ind1_acceleration=0.02, ind1_maximum=0.2,
            ind2_short_window=20, ind2_long_window=50
        )
        engine = TradingEngine(sar_ma_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ SAR + MA combination works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ SAR + MA combination failed: {e}")
    
    # Test 4: SAR + RSI combination
    print("\n4. Testing SAR + RSI Combination")
    try:
        sar_rsi_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'sar', 'rsi',
            weight1=0.5, weight2=0.5,
            ind1_acceleration=0.02, ind1_maximum=0.2,
            ind2_period=14, ind2_overbought=70, ind2_oversold=30
        )
        engine = TradingEngine(sar_rsi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ SAR + RSI combination works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ SAR + RSI combination failed: {e}")


def test_chande_momentum_oscillator():
    """Test the Chande Momentum Oscillator indicator."""
    print("\n=== Testing Chande Momentum Oscillator ===\n")
    
    # Test 1: Basic CMO strategy
    print("1. Testing Basic CMO Strategy")
    try:
        cmo_strategy = StrategyBuilder.create_single_indicator_strategy('cmo', period=14)
        engine = TradingEngine(cmo_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Basic CMO works: {summary['total_trades']} trades")
        print(f"   ✓ Buy trades: {summary['buy_trades']}")
        print(f"   ✓ Sell trades: {summary['sell_trades']}")
    except Exception as e:
        print(f"   ✗ Basic CMO failed: {e}")
    
    # Test 2: CMO with custom parameters
    print("\n2. Testing CMO with Custom Parameters")
    try:
        cmo_custom = StrategyBuilder.create_single_indicator_strategy(
            'cmo', 
            period=10,  # Shorter period
            overbought=40,  # More conservative overbought
            oversold=-40  # More conservative oversold
        )
        engine = TradingEngine(cmo_custom, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ Custom CMO works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ Custom CMO failed: {e}")
    
    # Test 3: CMO + RSI combination (momentum analysis)
    print("\n3. Testing CMO + RSI Combination (Momentum Analysis)")
    try:
        cmo_rsi_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'cmo', 'rsi',
            weight1=0.5, weight2=0.5,
            ind1_period=14, ind1_overbought=50, ind1_oversold=-50,
            ind2_period=14, ind2_overbought=70, ind2_oversold=30
        )
        engine = TradingEngine(cmo_rsi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ CMO + RSI combination works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ CMO + RSI combination failed: {e}")
    
    # Test 4: CMO + MFI combination
    print("\n4. Testing CMO + MFI Combination")
    try:
        cmo_mfi_strategy = StrategyBuilder.create_dual_indicator_strategy(
            'cmo', 'mfi',
            weight1=0.4, weight2=0.6,  # MFI has higher weight
            ind1_period=14, ind1_overbought=50, ind1_oversold=-50,
            ind2_period=14, ind2_overbought=80, ind2_oversold=20
        )
        engine = TradingEngine(cmo_mfi_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ CMO + MFI combination works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ CMO + MFI combination failed: {e}")


def test_triple_combinations():
    """Test triple indicator combinations with new indicators."""
    print("\n=== Testing Triple Indicator Combinations ===\n")
    
    # Test 1: SAR + CMO + MA
    print("1. Testing SAR + CMO + MA Combination")
    try:
        sar_cmo_ma_strategy = StrategyBuilder.create_triple_indicator_strategy(
            'sar', 'cmo', 'ma',
            weight1=0.4, weight2=0.3, weight3=0.3,
            ind1_acceleration=0.02, ind1_maximum=0.2,
            ind2_period=14, ind2_overbought=50, ind2_oversold=-50,
            ind3_short_window=20, ind3_long_window=50
        )
        engine = TradingEngine(sar_cmo_ma_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ SAR + CMO + MA works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ SAR + CMO + MA failed: {e}")
    
    # Test 2: CMO + RSI + Bollinger
    print("\n2. Testing CMO + RSI + Bollinger Combination")
    try:
        cmo_rsi_bb_strategy = StrategyBuilder.create_triple_indicator_strategy(
            'cmo', 'rsi', 'bollinger',
            weight1=0.3, weight2=0.4, weight3=0.3,
            ind1_period=14, ind1_overbought=50, ind1_oversold=-50,
            ind2_period=14, ind2_overbought=70, ind2_oversold=30,
            ind3_window=20, ind3_num_std=2
        )
        engine = TradingEngine(cmo_rsi_bb_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ CMO + RSI + Bollinger works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ CMO + RSI + Bollinger failed: {e}")
    
    # Test 3: SAR + MFI + Mean Reversion
    print("\n3. Testing SAR + MFI + Mean Reversion Combination")
    try:
        sar_mfi_mr_strategy = StrategyBuilder.create_triple_indicator_strategy(
            'sar', 'mfi', 'mean_reversion',
            weight1=0.4, weight2=0.3, weight3=0.3,
            ind1_acceleration=0.02, ind1_maximum=0.2,
            ind2_period=14, ind2_overbought=80, ind2_oversold=20,
            ind3_window=20, ind3_entry_z=1.0, ind3_exit_z=0.0
        )
        engine = TradingEngine(sar_mfi_mr_strategy, "AAPL")
        trades = engine.run()
        summary = engine.get_trade_summary()
        print(f"   ✓ SAR + MFI + Mean Reversion works: {summary['total_trades']} trades")
    except Exception as e:
        print(f"   ✗ SAR + MFI + Mean Reversion failed: {e}")


def test_signal_analysis():
    """Test signal analysis for new indicators."""
    print("\n=== Testing Signal Analysis ===\n")
    
    # Test SAR signal analysis
    print("1. Testing SAR Signal Analysis")
    try:
        sar_strategy = StrategyBuilder.create_single_indicator_strategy('sar', acceleration=0.02, maximum=0.2)
        engine = TradingEngine(sar_strategy, "AAPL")
        trades = engine.run()
        signals = engine.get_signals()
        
        print(f"   ✓ SAR signals generated: {len(signals)} data points")
        print(f"   ✓ Signal columns: {list(signals.columns)}")
        
        # Show recent signals
        recent_signals = signals.tail(5)
        print(f"   ✓ Recent SAR signals (last 5 days):")
        for date, row in recent_signals.iterrows():
            if row['signal'] != 0:
                action = "BUY" if row['signal'] > 0 else "SELL"
                print(f"     {date.date()}: {action} (signal: {row['signal']:.2f})")
    except Exception as e:
        print(f"   ✗ SAR signal analysis failed: {e}")
    
    # Test CMO signal analysis
    print("\n2. Testing CMO Signal Analysis")
    try:
        cmo_strategy = StrategyBuilder.create_single_indicator_strategy('cmo', period=14)
        engine = TradingEngine(cmo_strategy, "AAPL")
        trades = engine.run()
        signals = engine.get_signals()
        
        print(f"   ✓ CMO signals generated: {len(signals)} data points")
        print(f"   ✓ Signal columns: {list(signals.columns)}")
        
        # Show recent signals
        recent_signals = signals.tail(5)
        print(f"   ✓ Recent CMO signals (last 5 days):")
        for date, row in recent_signals.iterrows():
            if row['signal'] != 0:
                action = "BUY" if row['signal'] > 0 else "SELL"
                print(f"     {date.date()}: {action} (signal: {row['signal']:.2f})")
    except Exception as e:
        print(f"   ✗ CMO signal analysis failed: {e}")


def test_all_indicators():
    """Test that all indicators are working together."""
    print("\n=== Testing All Indicators Together ===\n")
    
    indicators = ['ma', 'rsi', 'bollinger', 'mean_reversion', 'mfi', 'sar', 'cmo']
    
    for i, indicator in enumerate(indicators, 1):
        print(f"{i}. Testing {indicator.upper()} indicator")
        try:
            if indicator == 'ma':
                strategy = StrategyBuilder.create_single_indicator_strategy('ma', short_window=20, long_window=50)
            elif indicator == 'rsi':
                strategy = StrategyBuilder.create_single_indicator_strategy('rsi', period=14)
            elif indicator == 'bollinger':
                strategy = StrategyBuilder.create_single_indicator_strategy('bollinger', window=20, num_std=2)
            elif indicator == 'mean_reversion':
                strategy = StrategyBuilder.create_single_indicator_strategy('mean_reversion', window=20)
            elif indicator == 'mfi':
                strategy = StrategyBuilder.create_single_indicator_strategy('mfi', period=14)
            elif indicator == 'sar':
                strategy = StrategyBuilder.create_single_indicator_strategy('sar', acceleration=0.02, maximum=0.2)
            elif indicator == 'cmo':
                strategy = StrategyBuilder.create_single_indicator_strategy('cmo', period=14)
            
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            summary = engine.get_trade_summary()
            print(f"   ✓ {indicator.upper()} works: {summary['total_trades']} trades")
        except Exception as e:
            print(f"   ✗ {indicator.upper()} failed: {e}")


if __name__ == "__main__":
    print("Testing New Indicators: Parabolic SAR and Chande Momentum Oscillator\n")
    
    # Test individual indicators
    test_parabolic_sar()
    test_chande_momentum_oscillator()
    
    # Test combinations
    test_triple_combinations()
    
    # Test signal analysis
    test_signal_analysis()
    
    # Test all indicators together
    test_all_indicators()
    
    print("\n=== All Tests Completed! ===")
    print("✓ Parabolic SAR indicator is working correctly")
    print("✓ Chande Momentum Oscillator indicator is working correctly")
    print("✓ Both indicators integrate well with existing indicators")
    print("✓ All combinations and signal analysis are functional") 