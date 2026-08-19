"""
==========================================
SULTAN QUANT OS
Price Action Trade Builder
Version : 2.0.0
==========================================

Responsibilities

- Execute Buy
- Execute Sell
- Build Trade Levels
- Attach Risk Management

"""


from strategies.risk_builder import build_risk



# ==================================================
# NORMALIZE BOOLEAN
# ==================================================

def normalize_boolean_columns(df):

    """
    Keep BUY / SELL as native Python bool
    """

    if "BUY" in df.columns:

        df["BUY"] = df["BUY"].astype(object)


    if "SELL" in df.columns:

        df["SELL"] = df["SELL"].astype(object)


    return df



# ==================================================
# EXECUTE BUY
# ==================================================

def execute_buy(

    df,

    index,

    entry,

    atr,

    confirmation_score,

    pattern_score,

    structure_score,

):


    sl, tp = build_risk(

        entry=entry,

        atr=atr,

        side="BUY",

    )


    df.at[index, "BUY"] = True

    df.at[index, "SELL"] = False


    df.at[index, "SL"] = sl

    df.at[index, "TP"] = tp


    df = normalize_boolean_columns(df)


    return df




# ==================================================
# EXECUTE SELL
# ==================================================

def execute_sell(

    df,

    index,

    entry,

    atr,

    confirmation_score,

    pattern_score,

    structure_score,

):


    sl, tp = build_risk(

        entry=entry,

        atr=atr,

        side="SELL",

    )


    df.at[index, "BUY"] = False

    df.at[index, "SELL"] = True


    df.at[index, "SL"] = sl

    df.at[index, "TP"] = tp


    df = normalize_boolean_columns(df)


    return df