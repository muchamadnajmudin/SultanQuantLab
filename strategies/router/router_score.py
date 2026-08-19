"""
==========================================
SULTAN QUANT OS

Router Score Engine

Version : 1.0.0
==========================================

Responsibilities:

- Score market condition
- Rank strategy suitability

"""


# ==================================================
# TREND SCORE
# ==================================================

def trend_score(row):

    score = 0

    ema20 = row.get(
        "EMA20",
        0
    )

    ema50 = row.get(
        "EMA50",
        0
    )

    ema200 = row.get(
        "EMA200",
        0
    )

    adx = row.get(
        "ADX",
        0
    )


    if ema20 > ema50 > ema200:

        score += 50


    if ema20 < ema50 < ema200:

        score += 50


    if adx >= 25:

        score += 30


    return score



# ==================================================
# RANGE SCORE
# ==================================================

def range_score(row):

    score = 0


    adx = row.get(
        "ADX",
        0
    )


    if adx < 20:

        score += 50


    return score



# ==================================================
# VOLATILITY SCORE
# ==================================================

def volatility_score(row):

    score = 0


    atr = row.get(
        "ATR",
        0
    )

    close = row.get(
        "close",
        0
    )


    if close:

        volatility = atr / close


        if volatility > 0.002:

            score += 50


    return score



# ==================================================
# TOTAL SCORE
# ==================================================

def router_scores(row):

    return {

        "TRENDING":

            trend_score(row),


        "RANGING":

            range_score(row),


        "VOLATILE":

            volatility_score(row),

    }