"""
==========================================

SULTAN QUANT OS

Strategy Allocation Engine

Version : 1.0.0

==========================================

Responsibilities:

- Calculate strategy allocation
- Normalize portfolio weights

"""


def normalize_allocation(weights):

    total = sum(
        weights.values()
    )


    if total == 0:

        return {
            key: 0
            for key in weights
        }


    return {

        key: round(
            value / total,
            2
        )

        for key, value in weights.items()

    }



def default_allocation(regime):


    if regime == "TRENDING":


        return normalize_allocation({

            "TREND_FOLLOWING":50,

            "FIBONACCI":30,

            "PRICE_ACTION":20,

        })



    if regime in (
        "RANGING",
        "QUIET_RANGE",
    ):


        return normalize_allocation({

            "PRICE_ACTION":50,

            "FIBONACCI":40,

            "BREAKOUT":10,

        })



    if regime == "VOLATILE":


        return normalize_allocation({

            "BREAKOUT":60,

            "PRICE_ACTION":20,

            "FIBONACCI":20,

        })



    return {}