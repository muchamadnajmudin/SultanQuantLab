"""
==========================================
Sultan Quant Lab
Module : Statistics Engine
Version : 2.3.2
==========================================
"""

import math
import config.settings as settings


ROUND_DIGITS = 2



# =====================================================
# EMPTY STATISTICS
# =====================================================

def empty_statistics():

    return {

        "total_trade": 0,

        "winner": 0,
        "loser": 0,

        "win_rate": 0,

        "gross_profit": 0,
        "gross_loss": 0,
        "net_profit": 0,

        "profit_factor": 0,

        "average_win": 0,
        "average_loss": 0,

        "expectancy": 0,
        "average_trade": 0,

        "max_win": 0,
        "max_loss": 0,

        "average_rr": 0,

        "max_drawdown": 0,
        "max_drawdown_percent": 0,

        "max_win_streak": 0,
        "max_loss_streak": 0,

        "recovery_factor": 0,

        "sharpe_ratio": 0,

        "equity_curve": [
            settings.INITIAL_BALANCE
        ],

        "drawdown_curve": []

    }



# =====================================================
# STREAK
# =====================================================

def calculate_streaks(trades):

    win_streak = 0
    loss_streak = 0

    max_win_streak = 0
    max_loss_streak = 0



    for trade in trades:


        if trade.profit > 0:

            win_streak += 1
            loss_streak = 0


        elif trade.profit < 0:

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



    return (
        max_win_streak,
        max_loss_streak
    )



# =====================================================
# SHARPE
# =====================================================

def calculate_sharpe(trades):


    returns = [

        float(trade.profit)

        for trade in trades

    ]



    if len(returns) < 2:

        return 0



    avg = sum(returns) / len(returns)



    variance = sum(

        (x - avg) ** 2

        for x in returns

    ) / (len(returns) - 1)



    std = math.sqrt(
        variance
    )



    if std == 0:

        return 0



    return avg / std



# =====================================================
# MAIN
# =====================================================

def calculate_statistics(trades):


    total_trade = len(trades)



    if total_trade == 0:

        return empty_statistics()



    winners = [

        float(t.profit)

        for t in trades

        if t.profit > 0

    ]



    losers = [

        float(t.profit)

        for t in trades

        if t.profit < 0

    ]



    winner_count = len(winners)

    loser_count = len(losers)



    gross_profit = sum(winners)


    gross_loss = abs(
        sum(losers)
    )


    net_profit = (

        gross_profit -
        gross_loss

    )



    win_rate = (

        winner_count /
        total_trade *
        100

    )



    profit_factor = (

        gross_profit /
        gross_loss

        if gross_loss > 0

        else 0

    )



    average_win = (

        gross_profit /
        winner_count

        if winner_count

        else 0

    )



    average_loss = (

        gross_loss /
        loser_count

        if loser_count

        else 0

    )



    average_trade = (

        net_profit /
        total_trade

    )


    expectancy = average_trade



    # =================================================
    # RISK REWARD
    # =================================================

    rr_values = [

        float(trade.risk_reward)

        for trade in trades

        if trade.risk_reward > 0

    ]



    average_rr = (

        sum(rr_values) /
        len(rr_values)

        if rr_values

        else 0

    )



    max_win = (

        max(winners)

        if winners

        else 0

    )



    max_loss = (

        min(

            [

                float(t.profit)

                for t in trades

            ]

        )

        if trades

        else 0

    )



    # =================================================
    # EQUITY CURVE
    # =================================================

    equity = settings.INITIAL_BALANCE


    equity_curve = [

        float(equity)

    ]


    peak = equity


    drawdown_curve = []


    max_drawdown = 0



    for trade in trades:


        equity += float(
            trade.profit
        )


        equity_curve.append(
            float(equity)
        )



        if equity > peak:

            peak = equity



        drawdown = peak - equity



        drawdown_curve.append(

            float(drawdown)

        )



        max_drawdown = max(

            max_drawdown,

            drawdown

        )



    # mengikuti baseline lama

    max_drawdown_percent = (

        max_drawdown /
        net_profit *
        100

        if net_profit != 0

        else 0

    )



    max_win_streak, max_loss_streak = calculate_streaks(
        trades
    )



    recovery_factor = (

        net_profit /
        max_drawdown

        if max_drawdown

        else 0

    )



    sharpe_ratio = calculate_sharpe(
        trades
    )



    return {


        "total_trade": total_trade,


        "winner": winner_count,


        "loser": loser_count,


        "win_rate": round(
            win_rate,
            ROUND_DIGITS
        ),



        "gross_profit": round(
            gross_profit,
            ROUND_DIGITS
        ),


        "gross_loss": round(
            gross_loss,
            ROUND_DIGITS
        ),


        "net_profit": round(
            net_profit,
            ROUND_DIGITS
        ),



        "profit_factor": round(
            profit_factor,
            ROUND_DIGITS
        ),



        "average_win": round(
            average_win,
            ROUND_DIGITS
        ),



        "average_loss": round(
            average_loss,
            ROUND_DIGITS
        ),



        "expectancy": round(
            expectancy,
            ROUND_DIGITS
        ),



        "average_trade": round(
            average_trade,
            ROUND_DIGITS
        ),



        "max_win": round(
            max_win,
            ROUND_DIGITS
        ),



        "max_loss": round(
            max_loss,
            ROUND_DIGITS
        ),



        "average_rr": round(
            average_rr,
            ROUND_DIGITS
        ),



        "max_drawdown": round(
            max_drawdown,
            ROUND_DIGITS
        ),



        "max_drawdown_percent": round(
            max_drawdown_percent,
            ROUND_DIGITS
        ),



        "max_win_streak": max_win_streak,


        "max_loss_streak": max_loss_streak,



        "recovery_factor": round(
            recovery_factor,
            ROUND_DIGITS
        ),



        "sharpe_ratio": round(
            sharpe_ratio,
            ROUND_DIGITS
        ),



        "equity_curve": equity_curve,



        "drawdown_curve": [

            round(
                x,
                ROUND_DIGITS
            )

            for x in drawdown_curve

        ]

    }