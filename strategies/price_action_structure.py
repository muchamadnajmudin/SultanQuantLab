"""
==========================================
SULTAN QUANT OS
Market Structure Engine
Version : 2.0.0
==========================================

Responsibilities

- Break Of Structure (BOS)
- Change Of Character (CHoCH)
- Market Structure Shift (MSS)

"""

import pandas as pd


# ==================================================
# COLUMN ADAPTER
# ==================================================

def _col(df, upper_name, lower_name):

    if upper_name in df.columns:
        return upper_name

    return lower_name


# ==================================================
# DETECT MARKET STRUCTURE
# ==================================================

def detect_structure(df: pd.DataFrame):

    df = df.copy()

    high_col = _col(df, "High", "high")
    low_col = _col(df, "Low", "low")
    close_col = _col(df, "Close", "close")

    columns = [

        "BULLISH_BOS",
        "BEARISH_BOS",
        "BULLISH_CHOCH",
        "BEARISH_CHOCH",
        "MSS",

    ]

    for col in columns:

        if col not in df.columns:

            df[col] = False

    last_swing_high = None
    last_swing_low = None

    trend = None

    for i in range(len(df)):

        row = df.iloc[i]

        # ------------------------------------------
        # Update Swing
        # ------------------------------------------

        if row.get("SWING_HIGH", False):

            last_swing_high = row[high_col]

        if row.get("SWING_LOW", False):

            last_swing_low = row[low_col]

        close = row[close_col]

        # ------------------------------------------
        # Bullish BOS
        # ------------------------------------------

        if (

            last_swing_high is not None

            and close > last_swing_high

        ):

            df.at[df.index[i], "BULLISH_BOS"] = True

            if trend == "DOWN":

                df.at[df.index[i], "BULLISH_CHOCH"] = True

                df.at[df.index[i], "MSS"] = True

            trend = "UP"

        # ------------------------------------------
        # Bearish BOS
        # ------------------------------------------

        if (

            last_swing_low is not None

            and close < last_swing_low

        ):

            df.at[df.index[i], "BEARISH_BOS"] = True

            if trend == "UP":

                df.at[df.index[i], "BEARISH_CHOCH"] = True

                df.at[df.index[i], "MSS"] = True

            trend = "DOWN"

    return df


# ==================================================
# LAST TREND
# ==================================================

def get_market_trend(df):

    if len(df) == 0:

        return "UNKNOWN"

    last = df.iloc[-1]

    if last.get("BULLISH_BOS", False):

        return "UP"

    if last.get("BEARISH_BOS", False):

        return "DOWN"

    return "RANGE"