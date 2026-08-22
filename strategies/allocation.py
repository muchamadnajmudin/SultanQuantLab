"""
==========================================

SULTAN QUANT OS

Strategy Allocation Engine

Version : 2.0.0

==========================================

Responsibilities:

- Calculate strategy allocation
- Normalize portfolio weights
- Support canonical market regimes
- Preserve legacy regime compatibility
"""

from engine.market_regime import (
    STRONG_TREND,
    TRENDING,
    RANGE,
    VOLATILE,
    TRANSITION,
    UNKNOWN,
    normalize_market_regime,
)


# ==================================================
# NORMALIZE ALLOCATION
# ==================================================

def normalize_allocation(
    weights,
):

    """
    Normalize strategy weights.

    Returns weights with total approximately 1.0.
    """

    if weights is None:

        return {}

    if not isinstance(
        weights,
        dict,
    ):

        raise TypeError(
            "weights must be a dictionary."
        )

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

            value
            /
            total,

            2,

        )

        for key, value
        in weights.items()

    }


# ==================================================
# DEFAULT ALLOCATION
# ==================================================

def default_allocation(
    regime,
):

    """
    Return default strategy allocation based on
    market regime.

    Accepts canonical and legacy regime names.

    Canonical:

    - STRONG_TREND
    - TRENDING
    - RANGE
    - VOLATILE
    - TRANSITION
    - UNKNOWN

    Legacy aliases are normalized automatically.
    """

    regime = normalize_market_regime(
        regime,
        default=UNKNOWN,
    )

    # ==============================================
    # STRONG TREND
    # ==============================================

    if regime == STRONG_TREND:

        return normalize_allocation({

            "TREND_FOLLOWING":
                60,

            "FIBONACCI":
                25,

            "PRICE_ACTION":
                15,

        })

    # ==============================================
    # NORMAL TREND
    # ==============================================

    if regime == TRENDING:

        return normalize_allocation({

            "TREND_FOLLOWING":
                50,

            "FIBONACCI":
                30,

            "PRICE_ACTION":
                20,

        })

    # ==============================================
    # RANGE
    # ==============================================

    if regime == RANGE:

        return normalize_allocation({

            "PRICE_ACTION":
                50,

            "FIBONACCI":
                40,

            "BREAKOUT":
                10,

        })

    # ==============================================
    # VOLATILE
    # ==============================================

    if regime == VOLATILE:

        return normalize_allocation({

            "BREAKOUT":
                60,

            "PRICE_ACTION":
                20,

            "FIBONACCI":
                20,

        })

    # ==============================================
    # TRANSITION
    #
    # Conservative allocation.
    # ==============================================

    if regime == TRANSITION:

        return normalize_allocation({

            "PRICE_ACTION":
                50,

            "FIBONACCI":
                30,

            "TREND_FOLLOWING":
                20,

        })

    # ==============================================
    # UNKNOWN
    # ==============================================

    return {}