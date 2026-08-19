"""
==========================================
SULTAN QUANT OS
Market Regime Engine
Version : 1.1.0
==========================================

Responsibilities:

- Detect Trend Regime
- Detect Range Regime
- Detect Volatility Regime
- Detect Market Environment
- Institutional Strategy Routing

Design:

Trend structure has priority.

Volatility is treated as filter,
not as primary regime switch.

"""



# ==================================================
# TREND REGIME
# ==================================================

def trend_regime(row):

    """
    Detect EMA market direction

    Returns:

    BULLISH
    BEARISH
    NEUTRAL

    """


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


    if ema20 > ema50 > ema200:

        return "BULLISH"



    if ema20 < ema50 < ema200:

        return "BEARISH"



    return "NEUTRAL"




# ==================================================
# VOLATILITY REGIME
# ==================================================

def volatility_regime(row):

    """
    Detect ATR volatility

    Returns:

    HIGH_VOLATILITY
    NORMAL
    LOW_VOLATILITY

    """


    atr = row.get(
        "ATR",
        0
    )


    close = row.get(
        "close",
        row.get(
            "Close",
            0
        )
    )


    if close == 0:

        return "UNKNOWN"



    ratio = atr / close



    if ratio >= 0.002:

        return "HIGH_VOLATILITY"



    if ratio <= 0.0005:

        return "LOW_VOLATILITY"



    return "NORMAL"




# ==================================================
# MARKET STRENGTH
# ==================================================

def strength_regime(row):

    """
    Detect market strength using ADX

    """


    adx = row.get(
        "ADX",
        0
    )



    if adx >= 25:

        return "TRENDING"



    return "RANGING"




# ==================================================
# MARKET REGIME CLASSIFIER
# ==================================================

def detect_market_regime(row):

    """
    Main institutional market classifier.


    Priority:

    1. Trend Strength
    2. Range Condition
    3. Volatility as filter


    Returns:

    TRENDING
    RANGING
    QUIET_RANGE
    NEUTRAL

    """


    volatility = volatility_regime(
        row
    )


    strength = strength_regime(
        row
    )



    # ----------------------------------------------
    # Trending Market
    # ----------------------------------------------

    if strength == "TRENDING":


        return "TRENDING"



    # ----------------------------------------------
    # Ranging Market
    # ----------------------------------------------

    if strength == "RANGING":


        if volatility == "LOW_VOLATILITY":

            return "QUIET_RANGE"



        return "RANGING"



    return "NEUTRAL"




# ==================================================
# STRATEGY ROUTER
# ==================================================

def recommended_strategy(row):

    """
    Select preferred strategy
    according to market regime.

    """


    regime = detect_market_regime(
        row
    )



    mapping = {


        "TRENDING":

            "TREND_FOLLOWING",



        "RANGING":

            "FIBONACCI_REVERSAL",



        "QUIET_RANGE":

            "FIBONACCI_REVERSAL",



        "NEUTRAL":

            "WAIT",

    }



    return mapping.get(

        regime,

        "WAIT"

    )




# ==================================================
# REGIME SUMMARY
# ==================================================

def regime_summary(row):

    """
    Full market environment report

    """


    return {


        "trend":

            trend_regime(row),



        "volatility":

            volatility_regime(row),



        "strength":

            strength_regime(row),



        "regime":

            detect_market_regime(row),



        "strategy":

            recommended_strategy(row),

    }