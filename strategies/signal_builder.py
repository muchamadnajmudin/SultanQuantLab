"""
==========================================
SULTAN QUANT OS
Signal Builder
Version : 1.0.0
==========================================

Responsibilities:

- Reset signals
- Mark BUY / SELL
- Build SL / TP

"""

import pandas as pd


# ==================================================
# RESET
# ==================================================

def reset_signals(df):

    df = df.copy()

    df["BUY"] = False
    df["SELL"] = False

    df["SL"] = 0.0
    df["TP"] = 0.0

    return df


# ==================================================
# BUY
# ==================================================

def set_buy(

    df,

    index,

    sl,

    tp,

):

    df.at[index, "BUY"] = True

    df.at[index, "SL"] = sl

    df.at[index, "TP"] = tp


# ==================================================
# SELL
# ==================================================

def set_sell(

    df,

    index,

    sl,

    tp,

):

    df.at[index, "SELL"] = True

    df.at[index, "SL"] = sl

    df.at[index, "TP"] = tp


# ==================================================
# FINISH
# ==================================================

def finish(df):

    return df