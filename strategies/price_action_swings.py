"""
==========================================
SULTAN QUANT OS
Price Action Swings
Version : 2.0.0
==========================================

Responsibilities

- Detect Swing High
- Detect Swing Low
- Detect Higher High
- Detect Higher Low
- Detect Lower High
- Detect Lower Low

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
# DETECT SWINGS
# ==================================================

def detect_swings(df: pd.DataFrame, lookback: int = 2):

    df = df.copy()

    high_col = _col(df, "High", "high")
    low_col = _col(df, "Low", "low")

    columns = [
        "SWING_HIGH",
        "SWING_LOW",
        "HH",
        "HL",
        "LH",
        "LL",
    ]

    for col in columns:
        if col not in df.columns:
            df[col] = False

    swing_highs = []
    swing_lows = []

    for i in range(lookback, len(df) - lookback):

        high = df.iloc[i][high_col]
        low = df.iloc[i][low_col]

        previous_highs = df.iloc[i - lookback:i][high_col]
        next_highs = df.iloc[i + 1:i + lookback + 1][high_col]

        previous_lows = df.iloc[i - lookback:i][low_col]
        next_lows = df.iloc[i + 1:i + lookback + 1][low_col]

        if (
            high > previous_highs.max()
            and high > next_highs.max()
        ):
            df.at[df.index[i], "SWING_HIGH"] = True
            swing_highs.append((i, high))

        if (
            low < previous_lows.min()
            and low < next_lows.min()
        ):
            df.at[df.index[i], "SWING_LOW"] = True
            swing_lows.append((i, low))

    for j in range(1, len(swing_highs)):

        previous = swing_highs[j - 1]
        current = swing_highs[j]

        if current[1] > previous[1]:
            df.at[df.index[current[0]], "HH"] = True
        else:
            df.at[df.index[current[0]], "LH"] = True

    for j in range(1, len(swing_lows)):

        previous = swing_lows[j - 1]
        current = swing_lows[j]

        if current[1] > previous[1]:
            df.at[df.index[current[0]], "HL"] = True
        else:
            df.at[df.index[current[0]], "LL"] = True

    return df


# ==================================================
# GET LAST SWING HIGH
# ==================================================

def get_last_swing_high(df):

    swings = df[df["SWING_HIGH"]]

    if swings.empty:
        return None

    high_col = _col(df, "High", "high")

    return swings.iloc[-1][high_col]


# ==================================================
# GET LAST SWING LOW
# ==================================================

def get_last_swing_low(df):

    swings = df[df["SWING_LOW"]]

    if swings.empty:
        return None

    low_col = _col(df, "Low", "low")

    return swings.iloc[-1][low_col]