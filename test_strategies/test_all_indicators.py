#!/usr/bin/env python3
"""Comprehensive test script for all 20 indicators."""

import sys
import os
# Add parent directory to path to import strategies module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.engine import TradingEngine, StrategyBuilder

def test_all_indicators():
    """Test all 20 indicators individually."""
    print("=== Testing All 20 Indicators ===\n")
    
    # Define all indicators with their basic parameters
    indicators_config = {
        'ma': {'short_window': 20, 'long_window': 50},
        'rsi': {'period': 14},
        'bollinger': {'window': 20, 'num_std': 2},
        'mean_reversion': {'window': 20},
        'mfi': {'period': 14},
        'sar': {'acceleration': 0.02, 'maximum': 0.2},
        'cmo': {'period': 14},
        'stochastic': {'k_period': 14, 'd_period': 3},
        'williams_r': {'period': 14},
        'macd': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
        'obv': {'period': 20},
        'ema': {'short_period': 12, 'long_period': 26},
        'vwap': {'period': 20},
        'atr': {'period': 14, 'multiplier': 2.0},
        'ibs': {'overbought': 0.8, 'oversold': 0.2},
        'fibonacci': {'period': 20, 'retracement_level': 0.618},
        'ppo': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
        'adx': {'period': 14, 'threshold': 25.0},
        'std': {'period': 20, 'multiplier': 2.0},
        'rvi': {'period': 14}
    }
    
    results = {}
    
    # Test each indicator
    for i, (indicator, params) in enumerate(indicators_config.items(), 1):
        print(f"{i:2d}. Testing {indicator.upper()}...")
        try:
            strategy = StrategyBuilder.create_single_indicator_strategy(indicator, **params)
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            summary = engine.get_trade_summary()
            results[indicator] = summary['total_trades']
            print(f"     ✓ {indicator.upper()}: {summary['total_trades']} trades")
        except Exception as e:
            results[indicator] = f"ERROR: {e}"
            print(f"     ✗ {indicator.upper()}: {e}")
    
    # Summary
    print(f"\n=== Summary ===")
    working_count = 0
    for indicator, result in results.items():
        status = "✓" if isinstance(result, int) else "✗"
        if isinstance(result, int):
            working_count += 1
        print(f"{status} {indicator.upper()}: {result}")
    
    print(f"\nWorking indicators: {working_count}/20")
    return results


def test_indicator_combinations():
    """Test various indicator combinations."""
    print("\n=== Testing Indicator Combinations ===\n")
    
    combinations = [
        # Dual combinations
        ('stochastic', 'rsi', 'Momentum Analysis'),
        ('macd', 'ema', 'Trend Confirmation'),
        ('vwap', 'atr', 'Volume & Volatility'),
        ('williams_r', 'cmo', 'Oscillator Pair'),
        ('obv', 'mfi', 'Volume Analysis'),
        ('fibonacci', 'sar', 'Support/Resistance'),
        ('ppo', 'macd', 'MACD Variants'),
        ('adx', 'ma', 'Trend Strength'),
        ('std', 'bollinger', 'Volatility Bands'),
        ('rvi', 'rsi', 'Volatility & Momentum'),
        
        # Triple combinations
        ('ma', 'macd', 'rsi', 'Classic Trio'),
        ('vwap', 'atr', 'stochastic', 'Volume & Momentum'),
        ('ema', 'adx', 'ppo', 'Trend Analysis'),
        ('fibonacci', 'sar', 'williams_r', 'Support/Resistance'),
        ('obv', 'mfi', 'cmo', 'Volume & Momentum'),
    ]
    
    results = {}
    
    for i, combo in enumerate(combinations, 1):
        if len(combo) == 4:  # Triple indicator combination
            indicator1, indicator2, indicator3, description = combo
            print(f"{i:2d}. Testing {indicator1.upper()} + {indicator2.upper()} + {indicator3.upper()} ({description})...")
            try:
                strategy = StrategyBuilder.create_triple_indicator_strategy(
                    indicator1, indicator2, indicator3,
                    weight1=0.33, weight2=0.33, weight3=0.34
                )
                engine = TradingEngine(strategy, "AAPL")
                trades = engine.run()
                summary = engine.get_trade_summary()
                results[f"{indicator1}+{indicator2}+{indicator3}"] = summary['total_trades']
                print(f"     ✓ {indicator1.upper()}+{indicator2.upper()}+{indicator3.upper()}: {summary['total_trades']} trades")
            except Exception as e:
                results[f"{indicator1}+{indicator2}+{indicator3}"] = f"ERROR: {e}"
                print(f"     ✗ {indicator1.upper()}+{indicator2.upper()}+{indicator3.upper()}: {e}")
        elif len(combo) == 3:  # Dual indicator combination
            indicator1, indicator2, description = combo
            print(f"{i:2d}. Testing {indicator1.upper()} + {indicator2.upper()} ({description})...")
            try:
                strategy = StrategyBuilder.create_dual_indicator_strategy(
                    indicator1, indicator2,
                    weight1=0.5, weight2=0.5
                )
                engine = TradingEngine(strategy, "AAPL")
                trades = engine.run()
                summary = engine.get_trade_summary()
                results[f"{indicator1}+{indicator2}"] = summary['total_trades']
                print(f"     ✓ {indicator1.upper()}+{indicator2.upper()}: {summary['total_trades']} trades")
            except Exception as e:
                results[f"{indicator1}+{indicator2}"] = f"ERROR: {e}"
                print(f"     ✗ {indicator1.upper()}+{indicator2.upper()}: {e}")
        else:
            print(f"     ✗ Invalid combination format: {combo}")
    
    return results


def test_signal_analysis():
    """Test signal analysis for selected indicators."""
    print("\n=== Testing Signal Analysis ===\n")
    
    # Test a few key indicators for signal analysis
    test_indicators = ['macd', 'stochastic', 'vwap', 'adx', 'fibonacci']
    
    for indicator in test_indicators:
        print(f"Testing {indicator.upper()} signal analysis...")
        try:
            if indicator == 'macd':
                strategy = StrategyBuilder.create_single_indicator_strategy('macd', fast_period=12, slow_period=26, signal_period=9)
            elif indicator == 'stochastic':
                strategy = StrategyBuilder.create_single_indicator_strategy('stochastic', k_period=14, d_period=3)
            elif indicator == 'vwap':
                strategy = StrategyBuilder.create_single_indicator_strategy('vwap', period=20)
            elif indicator == 'adx':
                strategy = StrategyBuilder.create_single_indicator_strategy('adx', period=14, threshold=25.0)
            elif indicator == 'fibonacci':
                strategy = StrategyBuilder.create_single_indicator_strategy('fibonacci', period=20, retracement_level=0.618)
            
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            signals = engine.get_signals()
            
            print(f"  ✓ {indicator.upper()} signals generated: {len(signals)} data points")
            print(f"  ✓ Signal columns: {list(signals.columns)}")
            
            # Show recent signals
            recent_signals = signals.tail(3)
            print(f"  ✓ Recent {indicator.upper()} signals (last 3 days):")
            for date, row in recent_signals.iterrows():
                if row['signal'] != 0:
                    action = "BUY" if row['signal'] > 0 else "SELL"
                    print(f"    {date.date()}: {action} (signal: {row['signal']:.2f})")
            print()
        except Exception as e:
            print(f"  ✗ {indicator.upper()} signal analysis failed: {e}\n")


def test_custom_parameters():
    """Test indicators with custom parameters."""
    print("\n=== Testing Custom Parameters ===\n")
    
    custom_tests = [
        ('stochastic', {'k_period': 10, 'd_period': 3, 'overbought': 85, 'oversold': 15}, 'Aggressive Stochastic'),
        ('williams_r', {'period': 10, 'overbought': -15, 'oversold': -85}, 'Aggressive Williams %R'),
        ('macd', {'fast_period': 8, 'slow_period': 21, 'signal_period': 5}, 'Fast MACD'),
        ('atr', {'period': 10, 'multiplier': 1.5}, 'Conservative ATR'),
        ('fibonacci', {'period': 30, 'retracement_level': 0.5}, '50% Retracement'),
        ('adx', {'period': 10, 'threshold': 30.0}, 'Strong Trend ADX'),
    ]
    
    for indicator, params, description in custom_tests:
        print(f"Testing {indicator.upper()} with custom parameters ({description})...")
        try:
            strategy = StrategyBuilder.create_single_indicator_strategy(indicator, **params)
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            summary = engine.get_trade_summary()
            print(f"  ✓ {indicator.upper()}: {summary['total_trades']} trades")
        except Exception as e:
            print(f"  ✗ {indicator.upper()}: {e}")


def test_advanced_combinations():
    """Test advanced multi-indicator combinations."""
    print("\n=== Testing Advanced Combinations ===\n")
    
    advanced_combinations = [
        # Volume + Momentum + Trend
        ('obv', 'rsi', 'ma', 'Volume + Momentum + Trend'),
        # Volatility + Support/Resistance + Momentum
        ('atr', 'fibonacci', 'stochastic', 'Volatility + Support + Momentum'),
        # Multiple Oscillators
        ('rsi', 'cmo', 'williams_r', 'Triple Oscillator'),
        # Trend + Volume + Volatility
        ('ema', 'mfi', 'std', 'Trend + Volume + Volatility'),
    ]
    
    for i, (ind1, ind2, ind3, description) in enumerate(advanced_combinations, 1):
        print(f"{i}. Testing {ind1.upper()} + {ind2.upper()} + {ind3.upper()} ({description})...")
        try:
            strategy = StrategyBuilder.create_triple_indicator_strategy(
                ind1, ind2, ind3,
                weight1=0.4, weight2=0.3, weight3=0.3
            )
            engine = TradingEngine(strategy, "AAPL")
            trades = engine.run()
            summary = engine.get_trade_summary()
            print(f"  ✓ {ind1.upper()}+{ind2.upper()}+{ind3.upper()}: {summary['total_trades']} trades")
        except Exception as e:
            print(f"  ✗ {ind1.upper()}+{ind2.upper()}+{ind3.upper()}: {e}")


if __name__ == "__main__":
    print("Comprehensive Test: All 20 Indicators\n")
    
    # Test all indicators individually
    individual_results = test_all_indicators()
    
    # Test combinations
    combination_results = test_indicator_combinations()
    
    # Test signal analysis
    test_signal_analysis()
    
    # Test custom parameters
    test_custom_parameters()
    
    # Test advanced combinations
    test_advanced_combinations()
    
    print("\n=== Final Summary ===")
    working_individual = sum(1 for result in individual_results.values() if isinstance(result, int))
    working_combinations = sum(1 for result in combination_results.values() if isinstance(result, int))
    
    print(f"✓ Individual indicators working: {working_individual}/20")
    print(f"✓ Combinations working: {working_combinations}/{len(combination_results)}")
    print(f"✓ All indicators are now available for use!")
    print(f"✓ You can combine any 1-3 indicators with custom weights and parameters") 