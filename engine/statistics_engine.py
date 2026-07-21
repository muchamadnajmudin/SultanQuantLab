"""
==========================================
Sultan Quant Lab
Module : Statistics Engine
Version : 2.2
==========================================
"""

from engine.trade import Trade
import math


def calculate_statistics(trades: list[Trade]):

    total_trade = len(trades)

    if total_trade == 0:
        return {
            "total_trade": 0,
            "winner": 0,
            "loser": 0,
            "win_rate": 0.0,
            "gross_profit": 0.0,
            "gross_loss": 0.0,
            "net_profit": 0.0,
            "profit_factor": 0.0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "expectancy": 0.0,
            "average_trade": 0.0,
            "max_win": 0.0,
            "max_loss": 0.0,
            "average_rr": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_percent": 0.0,
            "max_win_streak": 0,
            "max_loss_streak": 0,
            "recovery_factor": 0.0,
            "sharpe_ratio": 0.0,
        }


    winners = [
        t for t in trades
        if t.profit > 0
    ]

    losers = [
        t for t in trades
        if t.profit <= 0
    ]


    gross_profit = sum(
        t.profit for t in winners
    )

    gross_loss = abs(
        sum(t.profit for t in losers)
    )


    net_profit = (
        gross_profit -
        gross_loss
    )


    win_rate = (
        len(winners)
        /
        total_trade
    ) * 100


    average_win = (
        gross_profit / len(winners)
        if winners
        else 0
    )


    average_loss = (
        gross_loss / len(losers)
        if losers
        else 0
    )


    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf")
    )


    expectancy = (
        net_profit /
        total_trade
    )


    max_win = max(
        (t.profit for t in winners),
        default=0
    )


    max_loss = min(
        (t.profit for t in losers),
        default=0
    )


    average_rr = (
        average_win / average_loss
        if average_loss > 0
        else float("inf")
    )


    # ===============================
    # EQUITY & DRAWDOWN
    # ===============================

    equity = 0
    peak = 0

    max_drawdown = 0

    equity_curve = []


    for trade in trades:

        equity += trade.profit

        equity_curve.append(equity)

        if equity > peak:
            peak = equity

        drawdown = (
            peak - equity
        )

        if drawdown > max_drawdown:
            max_drawdown = drawdown



    max_drawdown_percent = (
        (max_drawdown / peak) * 100
        if peak > 0
        else 0
    )


    # ===============================
    # WIN / LOSS STREAK
    # ===============================

    win_streak = 0
    loss_streak = 0

    max_win_streak = 0
    max_loss_streak = 0


    for trade in trades:

        if trade.profit > 0:

            win_streak += 1
            loss_streak = 0

        else:

            loss_streak += 1
            win_streak = 0


        max_win_streak = max(
            max_win_streak,
            win_streak
        )

        max_loss_streak = max(
            max_loss_streak,
            loss_streak
        )



    # ===============================
    # RECOVERY FACTOR
    # ===============================

    recovery_factor = (
        net_profit / max_drawdown
        if max_drawdown > 0
        else 0
    )



    # ===============================
    # SHARPE RATIO
    # ===============================

    returns = [
        t.profit
        for t in trades
    ]


    avg_return = (
        sum(returns)
        /
        len(returns)
    )


    variance = sum(
        (x - avg_return) ** 2
        for x in returns
    ) / len(returns)


    std_dev = math.sqrt(
        variance
    )


    sharpe_ratio = (
        avg_return / std_dev
        if std_dev > 0
        else 0
    )



    return {

        "total_trade": total_trade,

        "winner": len(winners),

        "loser": len(losers),

        "win_rate": round(
            win_rate, 2
        ),

        "gross_profit": round(
            gross_profit, 2
        ),

        "gross_loss": round(
            gross_loss, 2
        ),

        "net_profit": round(
            net_profit, 2
        ),

        "profit_factor":
            round(profit_factor, 2)
            if profit_factor != float("inf")
            else float("inf"),


        "average_win": round(
            average_win, 2
        ),

        "average_loss": round(
            average_loss, 2
        ),

        "expectancy": round(
            expectancy, 2
        ),

        "average_trade": round(
            expectancy, 2
        ),

        "max_win": round(
            max_win, 2
        ),

        "max_loss": round(
            max_loss, 2
        ),

        "average_rr":
            round(average_rr, 2)
            if average_rr != float("inf")
            else float("inf"),


        "max_drawdown": round(
            max_drawdown, 2
        ),

        "max_drawdown_percent": round(
            max_drawdown_percent, 2
        ),


        "max_win_streak":
            max_win_streak,


        "max_loss_streak":
            max_loss_streak,


        "recovery_factor": round(
            recovery_factor, 2
        ),


        "sharpe_ratio": round(
            sharpe_ratio, 2
        ),


        "equity_curve":
            equity_curve,
    }