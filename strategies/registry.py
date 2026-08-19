"""
==========================================
SULTAN QUANT OS
Strategy Registry
Version : 2.0.0
==========================================

Responsibilities:

- Register available strategies
- Normalize strategy names
- Return strategy callable
- List available strategies
- Register new strategies dynamically

"""

from strategies.xau_strategy import (
    generate_signal as xau_generate_signal,
)

from strategies.sultan_baseline import (
    generate_signal as sultan_baseline_generate_signal,
)

from strategies.price_action import (
    generate_signal as price_action_generate_signal,
)

from strategies.smart_money import (
    generate_signal as smart_money_generate_signal,
)

from strategies.trend_following import (
    generate_signal as trend_following_generate_signal,
)

from strategies.fibonacci import (
    generate_signal as fibonacci_generate_signal,
)

from strategies.breakout import (
    generate_signal as breakout_generate_signal,
)

from strategies.mean_reversion import (
    generate_signal as mean_reversion_generate_signal,
)

from strategies.supply_demand import (
    generate_signal as supply_demand_generate_signal,
)

from strategies.momentum import (
    generate_signal as momentum_generate_signal,
)

from strategies.seasonal import (
    generate_signal as seasonal_generate_signal,
)

from strategies.statistical_quant import (
    generate_signal as statistical_quant_generate_signal,
)


# ==================================================
# STRATEGY REGISTRY
# ==================================================

STRATEGIES = {

    # ==================================================
    # BASELINE STRATEGIES
    # ==================================================

    "xau_strategy":
        xau_generate_signal,

    "sultan_baseline":
        sultan_baseline_generate_signal,

    # ==================================================
    # CORE STRATEGIES
    # ==================================================

    "price_action":
        price_action_generate_signal,

    "smart_money":
        smart_money_generate_signal,

    "trend_following":
        trend_following_generate_signal,

    "fibonacci":
        fibonacci_generate_signal,

    "breakout":
        breakout_generate_signal,

    "mean_reversion":
        mean_reversion_generate_signal,

    "supply_demand":
        supply_demand_generate_signal,

    "momentum":
        momentum_generate_signal,

    "seasonal":
        seasonal_generate_signal,

    "statistical_quant":
        statistical_quant_generate_signal,

}


# ==================================================
# NORMALIZE STRATEGY NAME
# ==================================================

def normalize_strategy_name(
    name: str,
) -> str:

    """
    Normalize strategy identifier.

    Examples:

        TREND_FOLLOWING
        Trend_Following
        trend-following
        trend following

    become:

        trend_following
    """

    if not isinstance(name, str):

        raise ValueError(
            "Strategy name must be a string."
        )

    normalized = (
        name
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )

    return normalized


# ==================================================
# GET STRATEGY
# ==================================================

def get_strategy(
    name: str,
):

    """
    Return strategy callable.

    Strategy names are normalized
    before lookup.
    """

    normalized_name = normalize_strategy_name(
        name
    )

    if normalized_name not in STRATEGIES:

        raise ValueError(

            f"Strategy '{name}' not found. "
            f"Available strategies: "
            f"{list(STRATEGIES.keys())}"

        )

    return STRATEGIES[
        normalized_name
    ]


# ==================================================
# LIST STRATEGIES
# ==================================================

def list_strategies():

    """
    Return all registered strategies.
    """

    return list(
        STRATEGIES.keys()
    )


# ==================================================
# REGISTER STRATEGY
# ==================================================

def register_strategy(
    name: str,
    strategy_callable,
):

    """
    Register a new strategy.

    The strategy name is normalized
    before registration.
    """

    normalized_name = normalize_strategy_name(
        name
    )

    if not callable(
        strategy_callable
    ):

        raise ValueError(
            "strategy_callable must be callable."
        )

    STRATEGIES[
        normalized_name
    ] = strategy_callable


# ==================================================
# CHECK STRATEGY
# ==================================================

def has_strategy(
    name: str,
) -> bool:

    """
    Check whether a strategy exists.
    """

    normalized_name = normalize_strategy_name(
        name
    )

    return (
        normalized_name
        in STRATEGIES
    )