"""
==========================================
SULTAN QUANT OS

Institutional Strategy Router

Version : 1.0.0
==========================================

Responsibilities:

- Select strategy automatically
- Based on market regime

"""


from strategies.regime.market_regime import (
    detect_market_regime,
)


from strategies.router.router_decision import (
    decide_strategy,
)


# ==================================================
# ROUTER
# ==================================================

def route_strategy(row):


    regime = detect_market_regime(

        row

    )


    strategy = decide_strategy(

        regime

    )


    return {

        "regime": regime,

        "strategy": strategy,

    }



# ==================================================
# SIMPLE API
# ==================================================

def recommended_strategy(row):


    result = route_strategy(

        row

    )


    return result["strategy"]