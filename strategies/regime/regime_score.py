"""
==========================================
SULTAN QUANT OS
Regime Score Engine
Version : 1.0.0
==========================================

Responsibilities:

- Quantify Market Regime
- Provide Institutional Confidence

"""


from strategies.regime.market_regime import (
    detect_market_regime,
)



# ==================================================
# REGIME SCORE
# ==================================================

def regime_score(row):


    regime = detect_market_regime(
        row
    )


    scores = {


        "TRENDING":
            80,


        "VOLATILE_TREND":
            90,


        "RANGING":
            60,


        "QUIET_RANGE":
            50,


        "NEUTRAL":
            0,


    }


    return scores.get(

        regime,

        0

    )



# ==================================================
# REGIME BIAS
# ==================================================

def regime_bias(row):


    score = regime_score(
        row
    )


    if score >= 80:

        return "ACTIVE"


    if score >= 50:

        return "SELECTIVE"


    return "WAIT"

# ==================================================
# REGIME SUMMARY
# ==================================================

def regime_summary(row):

    regime = detect_market_regime(row)

    return {
        "regime": regime,
        "score": regime_score(row),
        "bias": regime_bias(row),
    }    