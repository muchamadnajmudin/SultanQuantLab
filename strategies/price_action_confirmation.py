"""
==========================================
SULTAN QUANT OS
Price Action Confirmation
Version : 1.0.0
==========================================

Responsibilities

- EMA Trend Filter
- ATR Volatility Filter
- ADX Trend Strength
- Volume Filter
- Confirmation Score

"""

import pandas as pd


# ==================================================
# EMA FILTER
# ==================================================

def ema_filter(row):

    if "EMA_FAST" not in row:
        return False

    if "EMA_SLOW" not in row:
        return False

    return row["EMA_FAST"] > row["EMA_SLOW"]


# ==================================================
# EMA SELL FILTER
# ==================================================

def ema_sell_filter(row):

    if "EMA_FAST" not in row:
        return False

    if "EMA_SLOW" not in row:
        return False

    return row["EMA_FAST"] < row["EMA_SLOW"]


# ==================================================
# ATR FILTER
# ==================================================

def atr_filter(

    row,
    minimum_atr=0.0,

):

    if "ATR" not in row:

        return False

    return row["ATR"] >= minimum_atr


# ==================================================
# ADX FILTER
# ==================================================

def adx_filter(

    row,
    minimum_adx=25,

):

    if "ADX" not in row:

        return False

    return row["ADX"] >= minimum_adx


# ==================================================
# VOLUME FILTER
# ==================================================

def volume_filter(

    row,
    minimum_volume=0,

):

    if "Volume" not in row:

        return True

    return row["Volume"] >= minimum_volume


# ==================================================
# CONFIRM BUY
# ==================================================

def confirm_buy(

    row,
    minimum_adx=25,
    minimum_atr=0,

):

    return (

        ema_filter(row)

        and atr_filter(

            row,

            minimum_atr,

        )

        and adx_filter(

            row,

            minimum_adx,

        )

        and volume_filter(row)

    )


# ==================================================
# CONFIRM SELL
# ==================================================

def confirm_sell(

    row,
    minimum_adx=25,
    minimum_atr=0,

):

    return (

        ema_sell_filter(row)

        and atr_filter(

            row,

            minimum_atr,

        )

        and adx_filter(

            row,

            minimum_adx,

        )

        and volume_filter(row)

    )


# ==================================================
# CONFIRMATION SCORE
# ==================================================

def confirmation_score(row):

    score = 0

    if ema_filter(row):
        score += 30

    if atr_filter(row):
        score += 20

    if adx_filter(row):
        score += 30

    if volume_filter(row):
        score += 20

    return score