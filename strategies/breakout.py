"""
==========================================
SULTAN QUANT OS
Breakout Strategy
Version : 2.0.0
==========================================

Responsibilities:

- Detect breakout
- Generate BUY / SELL
- Build SL / TP

"""

from strategies.base_strategy import prepare_dataframe
from strategies.risk_builder import build_risk


# ==================================================
# SETTINGS
# ==================================================

LOOKBACK = 20


# ==================================================
# GENERATE SIGNAL
# ==================================================

def generate_signal(df):

    df = prepare_dataframe(df)

    highest = df["high"].rolling(LOOKBACK).max().shift(1)
    lowest = df["low"].rolling(LOOKBACK).min().shift(1)

    for i in range(LOOKBACK, len(df)):

        close = df.iloc[i]["close"]

        # ==========================
        # BUY BREAKOUT
        # ==========================

        if close > highest.iloc[i]:

            df.at[df.index[i], "BUY"] = True

            sl, tp = build_risk(

                entry=close,

                atr=df.iloc[i]["ATR"],

                side="BUY",

            )

            df.at[df.index[i], "SL"] = sl
            df.at[df.index[i], "TP"] = tp

        # ==========================
        # SELL BREAKOUT
        # ==========================

        elif close < lowest.iloc[i]:

            df.at[df.index[i], "SELL"] = True

            sl, tp = build_risk(

                entry=close,

                atr=df.iloc[i]["ATR"],

                side="SELL",

            )

            df.at[df.index[i], "SL"] = sl
            df.at[df.index[i], "TP"] = tp

    return df