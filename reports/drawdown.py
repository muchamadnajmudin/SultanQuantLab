"""
==========================================
SULTAN QUANT OS
Drawdown Analytics Engine
Version : 4.2.0
==========================================

Responsibilities:

- Calculate drawdown
- Calculate maximum drawdown
- Measure drawdown percentage

"""


# ==================================================
# CALCULATE DRAWDOWN SERIES
# ==================================================

def calculate_drawdown(
    equity: list[float],
):

    if not equity:

        return []


    peak = equity[0]

    drawdowns = []


    for value in equity:


        if value > peak:

            peak = value


        drawdown = peak - value


        drawdowns.append(
            drawdown
        )


    return drawdowns



# ==================================================
# MAX DRAWDOWN
# ==================================================

def max_drawdown(
    equity: list[float],
):


    drawdowns = calculate_drawdown(
        equity
    )


    if not drawdowns:

        return 0


    return max(
        drawdowns
    )



# ==================================================
# MAX DRAWDOWN PERCENT
# ==================================================

def max_drawdown_percent(
    equity: list[float],
):


    if not equity:

        return 0


    peak = max(
        equity
    )


    if peak == 0:

        return 0


    return (

        max_drawdown(equity)

        /

        peak

        *

        100

    )