"""
==========================================
SULTAN QUANT OS
Trend Following Strategy
Version : 2.0.0
==========================================

Logic

BUY
EMA20 > EMA50 > EMA200
ADX > 25
Close > EMA20

SELL
EMA20 < EMA50 < EMA200
ADX > 25
Close < EMA20
"""

from strategies.base_strategy import prepare_dataframe
from strategies.risk_builder import build_risk


# ==================================================
# GENERATE SIGNAL
# ==================================================

def generate_signal(df):

    df = prepare_dataframe(df)

    required = [
        "close",
        "EMA20",
        "EMA50",
        "EMA200",
        "ADX",
        "ATR",
    ]

    for col in required:

        if col not in df.columns:
            return df

    for i in range(len(df)):

        close = df.at[i, "close"]

        ema20 = df.at[i, "EMA20"]
        ema50 = df.at[i, "EMA50"]
        ema200 = df.at[i, "EMA200"]

        adx = df.at[i, "ADX"]
        atr = df.at[i, "ATR"]

        if (
            ema20 > ema50
            and ema50 > ema200
            and close > ema20
            and adx >= 25
        ):

            df.at[i, "BUY"] = True

            sl, tp = build_risk(

                entry=close,
                atr=atr,
                side="BUY",

            )

            df.at[i, "SL"] = sl
            df.at[i, "TP"] = tp

        elif (
            ema20 < ema50
            and ema50 < ema200
            and close < ema20
            and adx >= 25
        ):

            df.at[i, "SELL"] = True

            sl, tp = build_risk(

                entry=close,
                atr=atr,
                side="SELL",

            )

            df.at[i, "SL"] = sl
            df.at[i, "TP"] = tp

    return df