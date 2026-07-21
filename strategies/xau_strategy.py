"""
==========================================
Sultan Quant Lab
XAUUSD Strategy
Version : 2.1
Feature : Dynamic ADX Filter Testing
==========================================
"""

import pandas as pd

from config.settings import (
    RSI_OVERSOLD,
    RSI_OVERBOUGHT,
    STOCH_OVERSOLD,
    STOCH_OVERBOUGHT,
    ADX_MIN,
    USE_EMA200_FILTER,
    USE_ADX_FILTER,
    USE_RSI_FILTER,
    USE_STOCH_FILTER,
)


def generate_signal(
    df: pd.DataFrame,
    rsi_oversold=None,
    rsi_overbought=None,
    adx_min=None,
):

    if rsi_oversold is None:
        rsi_oversold = RSI_OVERSOLD

    if rsi_overbought is None:
        rsi_overbought = RSI_OVERBOUGHT

    if adx_min is None:
        adx_min = ADX_MIN


    # ===============================
    # STOCHASTIC CROSS
    # ===============================

    cross_up = (
        (df["%K"].shift(1) <= df["%D"].shift(1))
        &
        (df["%K"] > df["%D"])
    )


    cross_down = (
        (df["%K"].shift(1) >= df["%D"].shift(1))
        &
        (df["%K"] < df["%D"])
    )


    # ===============================
    # EMA TREND FILTER
    # ===============================

    ema_buy = (
        (df["EMA20"] > df["EMA50"])
        &
        (
            (df["EMA50"] > df["EMA200"])
            if USE_EMA200_FILTER
            else True
        )
    )


    ema_sell = (
        (df["EMA20"] < df["EMA50"])
        &
        (
            (df["EMA50"] < df["EMA200"])
            if USE_EMA200_FILTER
            else True
        )
    )


    # ===============================
    # ADX MARKET REGIME FILTER
    # ===============================

    adx_filter = (
        (df["ADX"] > adx_min)
        if USE_ADX_FILTER
        else True
    )


    # ===============================
    # RSI FILTER
    # ===============================

    rsi_buy = (
        (df["RSI"] < rsi_oversold)
        if USE_RSI_FILTER
        else True
    )


    rsi_sell = (
        (df["RSI"] > rsi_overbought)
        if USE_RSI_FILTER
        else True
    )


    # ===============================
    # STOCH FILTER
    # ===============================

    stoch_buy = (
        (df["%K"] < STOCH_OVERSOLD)
        if USE_STOCH_FILTER
        else True
    )


    stoch_sell = (
        (df["%K"] > STOCH_OVERBOUGHT)
        if USE_STOCH_FILTER
        else True
    )


    # ===============================
    # FINAL SIGNAL
    # ===============================

    df["BUY"] = (
        ema_buy
        &
        adx_filter
        &
        rsi_buy
        &
        stoch_buy
        &
        cross_up
    )


    df["SELL"] = (
        ema_sell
        &
        adx_filter
        &
        rsi_sell
        &
        stoch_sell
        &
        cross_down
    )


    return df