"""
==========================================
SULTAN QUANT OS
Strategy Engine
Version : 3.0.0
==========================================

Responsibilities:

- Execute selected strategy
- Load strategy from registry
- Keep strategy interface consistent
"""

import pandas as pd

from strategies.registry import get_strategy


# ==================================================
# RUN STRATEGY
# ==================================================

def run_strategy(
    df: pd.DataFrame,
    strategy: str = "xau_strategy",
    **params,
) -> pd.DataFrame:
    """
    Execute selected strategy.

    Parameters
    ----------
    df : pd.DataFrame
        Price data.

    strategy : str
        Registered strategy name.

    params :
        Additional strategy parameters.

    Returns
    -------
    pd.DataFrame
    """

    strategy_callable = get_strategy(strategy)

    return strategy_callable(
        df,
        **params,
    )