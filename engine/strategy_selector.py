"""
==========================================
SULTAN QUANT OS
Strategy Selector
Version : 3.0.0
==========================================

Responsibilities:

- Analyze market
- Filter strategies
- Select best candidates

"""

from engine.market_analyzer import analyze_market
from engine.strategy_filter import filter_strategies


# ==================================================
# SELECT STRATEGIES
# ==================================================

def select_strategies(df):

    """
    Analyze market then return
    filtered strategy candidates.
    """

    market = analyze_market(df)

    candidates = filter_strategies(

        market,

    )

    return candidates


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_strategy(df):

    candidates = select_strategies(

        df,

    )

    if not candidates:

        return None

    return candidates[0]


# ==================================================
# TOP STRATEGIES
# ==================================================

def get_top_strategies(

    df,

    top_n=5,

):

    candidates = select_strategies(

        df,

    )

    return candidates[:top_n]


# ==================================================
# STRATEGY IDS
# ==================================================

def get_strategy_ids(df):

    candidates = select_strategies(

        df,

    )

    return [

        item["id"]

        for item in candidates

    ]


# ==================================================
# PRINT
# ==================================================

def print_selected(df):

    candidates = select_strategies(

        df,

    )

    print()

    print("=" * 60)
    print("SELECTED STRATEGIES")
    print("=" * 60)

    for i, item in enumerate(

        candidates,

        start=1,

    ):

        print(

            f"{i:>2}. "

            f"{item['name']:<30}"

            f"Score : {item['score']}"

        )

    print()