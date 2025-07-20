#!/usr/bin/env python3
"""
Example usage of the Algonex trading strategy system.

This script demonstrates how to:
1. Use the default strategy
2. Create single indicator strategies
3. Combine multiple indicators with custom weights
4. Analyze trading performance
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from strategies.engine import TradingEngine, StrategyBuilder
import pandas as pd


def run_strategy_analysis(ticker: str = "AAPL"):
    """Run analysis with different strategy combinations."""
    
    print(f"=== Algonex Strategy Analysis for {ticker} ===\n")
    
    # Example 1: Default Strategy
    print("1. Default Strategy (Moving Average Crossover)")
    default_strategy = StrategyBuilder.create_default_strategy()
    engine = TradingEngine(default_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 2: Single RSI Strategy
    print("2. Single RSI Strategy")
    rsi_strategy = StrategyBuilder.create_single_indicator_strategy('rsi', period=14)
    engine = TradingEngine(rsi_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 3: Dual Indicator Strategy (MA + RSI)
    print("3. Dual Indicator Strategy (Moving Average + RSI)")
    dual_strategy = StrategyBuilder.create_dual_indicator_strategy(
        'ma', 'rsi',
        weight1=0.6, weight2=0.4,  # MA has higher weight
        ind1_short_window=20, ind1_long_window=50,
        ind2_period=14
    )
    engine = TradingEngine(dual_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 4: Triple Indicator Strategy
    print("4. Triple Indicator Strategy (MA + RSI + Bollinger Bands)")
    triple_strategy = StrategyBuilder.create_triple_indicator_strategy(
        'ma', 'rsi', 'bollinger',
        weight1=0.4, weight2=0.3, weight3=0.3,
        ind1_short_window=20, ind1_long_window=50,
        ind2_period=14,
        ind3_window=20, ind3_num_std=2
    )
    engine = TradingEngine(triple_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 5: Mean Reversion Strategy
    print("5. Mean Reversion Strategy")
    mean_rev_strategy = StrategyBuilder.create_single_indicator_strategy(
        'mean_reversion', 
        window=20, entry_z=1.5, exit_z=0.5
    )
    engine = TradingEngine(mean_rev_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 6: Money Flow Index Strategy
    print("6. Money Flow Index Strategy")
    mfi_strategy = StrategyBuilder.create_single_indicator_strategy(
        'mfi', 
        period=14, overbought=80, oversold=20
    )
    engine = TradingEngine(mfi_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 7: Parabolic SAR Strategy
    print("7. Parabolic SAR Strategy")
    sar_strategy = StrategyBuilder.create_single_indicator_strategy(
        'sar', 
        acceleration=0.02, maximum=0.2
    )
    engine = TradingEngine(sar_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")
    
    # Example 8: Chande Momentum Oscillator Strategy
    print("8. Chande Momentum Oscillator Strategy")
    cmo_strategy = StrategyBuilder.create_single_indicator_strategy(
        'cmo', 
        period=14, overbought=50, oversold=-50
    )
    engine = TradingEngine(cmo_strategy, ticker)
    trades = engine.run()
    summary = engine.get_trade_summary()
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}\n")


def demonstrate_custom_strategy():
    """Demonstrate how to create a custom strategy with specific parameters."""
    
    print("=== Custom Strategy Example ===\n")
    
    # Create a custom strategy: RSI + Bollinger Bands with custom weights
    print("Custom Strategy: RSI (70%) + Bollinger Bands (30%)")
    
    custom_strategy = StrategyBuilder.create_dual_indicator_strategy(
        'rsi', 'bollinger',
        weight1=0.7, weight2=0.3,  # RSI has higher weight
        ind1_period=10,  # Shorter RSI period for more sensitivity
        ind2_window=15, ind2_num_std=1.5  # Tighter Bollinger Bands
    )
    
    engine = TradingEngine(custom_strategy, "AAPL")
    trades = engine.run()
    summary = engine.get_trade_summary()
    
    print(f"   Total trades: {summary['total_trades']}")
    print(f"   Buy trades: {summary['buy_trades']}")
    print(f"   Sell trades: {summary['sell_trades']}")
    
    # Show some signal details
    signals = engine.get_signals()
    print(f"\n   Signal columns available: {list(signals.columns)}")
    print(f"   Data points: {len(signals)}")
    
    # Show recent signals
    recent_signals = signals.tail(5)
    print(f"\n   Recent signals (last 5 days):")
    for date, row in recent_signals.iterrows():
        if row['signal'] != 0:
            action = "BUY" if row['signal'] > 0 else "SELL"
            print(f"     {date.date()}: {action} (signal: {row['signal']:.2f})")


def show_available_indicators():
    """Show information about available indicators."""
    
    print("=== Available Indicators ===\n")
    
    indicators = {
        'ma': {
            'name': 'Moving Average Crossover',
            'params': ['short_window', 'long_window'],
            'description': 'Generates signals when short MA crosses above/below long MA'
        },
        'rsi': {
            'name': 'Relative Strength Index',
            'params': ['period', 'overbought', 'oversold'],
            'description': 'Generates buy signals when oversold, sell signals when overbought'
        },
        'bollinger': {
            'name': 'Bollinger Bands',
            'params': ['window', 'num_std'],
            'description': 'Generates signals based on price position within bands'
        },
        'mean_reversion': {
            'name': 'Mean Reversion (Z-Score)',
            'params': ['window', 'entry_z', 'exit_z'],
            'description': 'Generates signals based on price deviation from mean'
        },
        'mfi': {
            'name': 'Money Flow Index',
            'params': ['period', 'overbought', 'oversold'],
            'description': 'Combines price and volume to identify overbought/oversold conditions'
        },
        'sar': {
            'name': 'Parabolic SAR',
            'params': ['acceleration', 'maximum'],
            'description': 'Trend following indicator that provides stop and reverse signals'
        },
        'cmo': {
            'name': 'Chande Momentum Oscillator',
            'params': ['period', 'overbought', 'oversold'],
            'description': 'Momentum oscillator that measures the rate of price changes'
        }
    }
    
    for key, info in indicators.items():
        print(f"{key.upper()}: {info['name']}")
        print(f"  Parameters: {', '.join(info['params'])}")
        print(f"  Description: {info['description']}")
        print()


if __name__ == "__main__":
    print("Algonex Trading Strategy System - Example Usage\n")
    
    # Show available indicators
    show_available_indicators()
    
    # Run strategy analysis
    run_strategy_analysis("AAPL")
    
    # Demonstrate custom strategy
    demonstrate_custom_strategy()
    
    print("\n=== Usage Tips ===")
    print("1. Start with the default strategy for basic analysis")
    print("2. Use single indicators to understand their behavior")
    print("3. Combine 2-3 indicators with custom weights for better results")
    print("4. Adjust indicator parameters based on your trading style")
    print("5. Use require_confirmation=True for more conservative signals")
    print("6. Monitor the 'composite_signal' column for signal strength") 