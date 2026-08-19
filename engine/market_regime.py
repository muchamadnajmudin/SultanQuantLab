"""
==========================================
SULTAN QUANT OS
Market Regime Detector
Version : 1.0.0
==========================================

Responsibilities

- Detect Market Condition
- Detect Trend
- Detect Volatility
- Strategy Bias Mapping

"""


# ==================================================
# TREND DETECTION
# ==================================================

def detect_trend(row):

    """
    EMA Trend Detection

    Bullish:
        EMA20 > EMA50 > EMA200

    Bearish:
        EMA20 < EMA50 < EMA200

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


    return "SIDEWAYS"




# ==================================================
# VOLATILITY DETECTION
# ==================================================

def detect_volatility(row):

    """
    ATR based volatility

    """

    atr = row.get(
        "ATR",
        0
    )


    close = row.get(
        "close",
        row.get(
            "Close",
            1
        )
    )


    if close == 0:

        return "UNKNOWN"


    atr_percent = (

        atr / close

    ) * 100



    if atr_percent >= 0.5:

        return "HIGH"


    if atr_percent <= 0.15:

        return "LOW"


    return "NORMAL"




# ==================================================
# REGIME DETECTION
# ==================================================

def detect_regime(row):


    trend = detect_trend(
        row
    )


    volatility = detect_volatility(
        row
    )


    adx = row.get(
        "ADX",
        0
    )



    # ------------------------------------------
    # High Volatility
    # ------------------------------------------

    if volatility == "HIGH":

        return "HIGH_VOLATILITY"



    # ------------------------------------------
    # Trending
    # ------------------------------------------

    if adx >= 25:


        return "TRENDING"



    # ------------------------------------------
    # Range
    # ------------------------------------------

    if adx < 20:


        return "RANGING"



    return "UNKNOWN"




# ==================================================
# STRATEGY BIAS
# ==================================================

def strategy_bias(
    regime,
    trend=None,
):


    if regime == "TRENDING":


        return [

            "trend_following",

            "price_action",

        ]



    if regime == "RANGING":


        return [

            "breakout",

            "fibonacci",

        ]



    if regime == "HIGH_VOLATILITY":


        return [

            "price_action",

            "fibonacci",

        ]



    return []




# ==================================================
# FULL ANALYSIS
# ==================================================

def analyze_market(row):


    trend = detect_trend(
        row
    )


    volatility = detect_volatility(
        row
    )


    regime = detect_regime(
        row
    )


    return {


        "regime":

            regime,


        "trend":

            trend,


        "volatility":

            volatility,


        "strategy_bias":

            strategy_bias(

                regime,

                trend,

            ),


    }