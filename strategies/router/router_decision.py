"""
==========================================
SULTAN QUANT OS

Router Decision Engine

Version : 1.1.0
==========================================

Responsibilities:

- Convert market regime
- Into strategy decision

"""


# ==================================================
# STRATEGY MAP
# ==================================================

STRATEGY_MAP = {


    "TRENDING":

        "TREND_FOLLOWING",



    "RANGING":

        "PRICE_ACTION",



    "QUIET_RANGE":

        "PRICE_ACTION",



    "NEUTRAL":

        "NO_TRADE",



    "VOLATILE":

        "BREAKOUT",

}




# ==================================================
# DECISION
# ==================================================

def decide_strategy(regime):


    return STRATEGY_MAP.get(

        regime,

        "NO_TRADE"

    )