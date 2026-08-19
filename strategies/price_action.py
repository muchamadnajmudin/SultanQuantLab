"""
==========================================
SULTAN QUANT OS
Price Action Strategy
Version : 2.0.1
==========================================

Responsibilities

- Generate Price Action Signal
- Detect Candlestick Pattern
- Detect Market Structure
- Confirm Trend
- Build Trade

"""

from strategies.base_strategy import prepare_dataframe

from strategies.price_action_patterns import detect_patterns
from strategies.price_action_swings import detect_swings
from strategies.price_action_structure import detect_structure

from strategies.price_action_confirmation import (
    confirmation_score,
)

from strategies.price_action_trade import (
    execute_buy,
    execute_sell,
)


# ==================================================
# COLUMN ADAPTER
# ==================================================

def _col(df, upper_name, lower_name):

    if upper_name in df.columns:
        return upper_name

    return lower_name


# ==================================================
# GENERATE SIGNAL
# ==================================================

def generate_signal(df):

    df = prepare_dataframe(df)

    # ------------------------------------------
    # Price Action Library
    # ------------------------------------------

    df = detect_patterns(df)

    df = detect_swings(df)

    df = detect_structure(df)

    close_col = _col(df, "Close", "close")

    # ------------------------------------------
    # Trading Loop
    # ------------------------------------------

    for i in range(len(df)):

        row = df.iloc[i]

        score = confirmation_score(row)

        atr = row["ATR"] if "ATR" in row else 1

        entry = row[close_col]

        # --------------------------------------
        # BUY
        # --------------------------------------

        if (

            row.get("BULLISH_ENGULFING", False)

            and row.get("BULLISH_BOS", False)

        ):

            df = execute_buy(

                df=df,

                index=i,

                entry=entry,

                atr=atr,

                confirmation_score=score,

                pattern_score=30,

                structure_score=30,

            )

        # --------------------------------------
        # SELL
        # --------------------------------------

        elif (

            row.get("BEARISH_ENGULFING", False)

            and row.get("BEARISH_BOS", False)

        ):

            df = execute_sell(

                df=df,

                index=i,

                entry=entry,

                atr=atr,

                confirmation_score=score,

                pattern_score=30,

                structure_score=30,

            )

    return df