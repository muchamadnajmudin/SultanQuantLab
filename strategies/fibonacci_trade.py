"""
==========================================
SULTAN QUANT OS
Fibonacci Trade Engine
Version : 1.0.0
==========================================

Responsibilities

- Execute BUY
- Execute SELL
- Build Stop Loss
- Build Take Profit
- Shared Fibonacci Trade Builder

"""

from strategies.risk_builder import build_risk


# ==================================================
# EXECUTE BUY
# ==================================================

def execute_buy(

    df,
    index,
    entry,
    atr,
    confirmation_score=0,
    pattern_score=0,
    structure_score=0,
    sl_multiplier=1.0,
    rr=2.0,

):

    sl, tp = build_risk(

        entry=entry,
        atr=atr,
        side="BUY",
        sl_multiplier=sl_multiplier,
        rr=rr,

    )

    df.at[df.index[index], "BUY"] = True
    df.at[df.index[index], "SELL"] = False

    df.at[df.index[index], "SL"] = sl
    df.at[df.index[index], "TP"] = tp

    if "CONFIRMATION_SCORE" not in df.columns:
        df["CONFIRMATION_SCORE"] = 0

    if "PATTERN_SCORE" not in df.columns:
        df["PATTERN_SCORE"] = 0

    if "STRUCTURE_SCORE" not in df.columns:
        df["STRUCTURE_SCORE"] = 0

    if "TOTAL_SCORE" not in df.columns:
        df["TOTAL_SCORE"] = 0

    df.at[df.index[index], "CONFIRMATION_SCORE"] = confirmation_score
    df.at[df.index[index], "PATTERN_SCORE"] = pattern_score
    df.at[df.index[index], "STRUCTURE_SCORE"] = structure_score

    df.at[df.index[index], "TOTAL_SCORE"] = (

        confirmation_score
        + pattern_score
        + structure_score

    )

    return df


# ==================================================
# EXECUTE SELL
# ==================================================

def execute_sell(

    df,
    index,
    entry,
    atr,
    confirmation_score=0,
    pattern_score=0,
    structure_score=0,
    sl_multiplier=1.0,
    rr=2.0,

):

    sl, tp = build_risk(

        entry=entry,
        atr=atr,
        side="SELL",
        sl_multiplier=sl_multiplier,
        rr=rr,

    )

    df.at[df.index[index], "BUY"] = False
    df.at[df.index[index], "SELL"] = True

    df.at[df.index[index], "SL"] = sl
    df.at[df.index[index], "TP"] = tp

    if "CONFIRMATION_SCORE" not in df.columns:
        df["CONFIRMATION_SCORE"] = 0

    if "PATTERN_SCORE" not in df.columns:
        df["PATTERN_SCORE"] = 0

    if "STRUCTURE_SCORE" not in df.columns:
        df["STRUCTURE_SCORE"] = 0

    if "TOTAL_SCORE" not in df.columns:
        df["TOTAL_SCORE"] = 0

    df.at[df.index[index], "CONFIRMATION_SCORE"] = confirmation_score
    df.at[df.index[index], "PATTERN_SCORE"] = pattern_score
    df.at[df.index[index], "STRUCTURE_SCORE"] = structure_score

    df.at[df.index[index], "TOTAL_SCORE"] = (

        confirmation_score
        + pattern_score
        + structure_score

    )

    return df