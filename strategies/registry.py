"""
==========================================
SULTAN QUANT OS
Strategy Registry
Version : 1.0.0
==========================================

Responsibilities:

- Register available strategies
- Return strategy callable
- List available strategies

"""

from strategies.xau_strategy import generate_signal


# ==================================================
# STRATEGY REGISTRY
# ==================================================

STRATEGIES = {

    "xau_strategy": generate_signal,

}


# ==================================================
# GET STRATEGY
# ==================================================

def get_strategy(name: str):

    if name not in STRATEGIES:

        raise ValueError(

            f"Strategy '{name}' not found."

        )

    return STRATEGIES[name]


# ==================================================
# LIST STRATEGIES
# ==================================================

def list_strategies():

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

    STRATEGIES[name] = strategy_callable