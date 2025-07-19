# backend/core/backtester.py
def run_backtest(trades: list, initial_capital: float = 10000.0):
    """Calculates performance metrics from a list of trades."""
    if not trades:
        return {
            "pnl": 0,
            "final_capital": initial_capital,
            "total_return_pct": 0,
            "total_trades": 0,
        }

    capital = initial_capital
    position = 0
    pnl = 0

    for trade_type, trade_time, trade_price in trades:
        if trade_type == "BUY" and position == 0:
            position = capital / trade_price  # Invest all capital
            capital = 0
        elif trade_type == "SELL" and position > 0:
            capital = position * trade_price
            pnl += capital - initial_capital
            position = 0

    # If still holding a position, calculate final value based on last price
    if position > 0:
        final_capital = position * trades[-1][2]
    else:
        final_capital = capital

    total_return_pct = ((final_capital - initial_capital) / initial_capital) * 100

    return {
        "pnl": final_capital - initial_capital,
        "final_capital": final_capital,
        "total_return_pct": round(total_return_pct, 2),
        "total_trades": len(trades),
    }
