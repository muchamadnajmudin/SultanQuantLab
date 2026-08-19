"""
==========================================
SULTAN QUANT OS
Strategy Filter
Version : 1.0.0
==========================================

Responsibilities:

- Filter strategies
- Match strategy capability
- Return candidate strategies

"""

from strategies.strategy_capability import (
    get_all_capabilities,
)

from strategies.strategy_metadata import (
    get_all_strategy_info,
)


# ==================================================
# FILTER STRATEGIES
# ==================================================

def filter_strategies(market_profile):

    capabilities = get_all_capabilities()

    metadata = get_all_strategy_info()

    candidates = []

    trend = market_profile.get(

        "trend",

        "UNCLEAR",

    )

    volatility = market_profile.get(

        "volatility",

        "LOW",

    )

    session = market_profile.get(

        "session",

        "UNKNOWN",

    )

    for strategy_id, capability in capabilities.items():

        info = metadata.get(

            strategy_id,

            {},

        )

        if info.get(

            "status",

            "PLANNED",

        ) != "ACTIVE":

            continue

        score = calculate_match_score(

            capability,

            trend,

            volatility,

            session,

        )

        candidates.append(

            {

                "id": strategy_id,

                "name": info.get(

                    "name",

                    strategy_id,

                ),

                "score": score,

                "category": info.get(

                    "category",

                    "",

                ),

            }

        )

    candidates.sort(

        key=lambda x: x["score"],

        reverse=True,

    )

    return candidates


# ==================================================
# MATCH SCORE
# ==================================================

def calculate_match_score(

    capability,

    trend,

    volatility,

    session,

):

    score = 0

    market_conditions = capability.get(

        "market_condition",

        [],

    )

    if trend == "UPTREND":

        if "trend" in market_conditions:

            score += 40

    elif trend == "DOWNTREND":

        if "trend" in market_conditions:

            score += 40

    elif trend == "RANGE":

        if "range" in market_conditions:

            score += 40

    if volatility == "HIGH":

        if "volatile" in market_conditions:

            score += 20

    if session == "LONDON":

        score += 10

    if session == "NEW_YORK":

        score += 10

    return score


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_candidate(

    market_profile,

):

    candidates = filter_strategies(

        market_profile,

    )

    if not candidates:

        return None

    return candidates[0]


# ==================================================
# TOP N
# ==================================================

def get_top_candidates(

    market_profile,

    top_n=5,

):

    candidates = filter_strategies(

        market_profile,

    )

    return candidates[:top_n]


# ==================================================
# PRINT
# ==================================================

def print_candidates(

    market_profile,

):

    candidates = filter_strategies(

        market_profile,

    )

    print()

    print("=" * 60)
    print("STRATEGY FILTER")
    print("=" * 60)

    for i, strategy in enumerate(

        candidates,

        start=1,

    ):

        print(

            f"{i:>2}. "

            f"{strategy['name']:<30}"

            f"Score : {strategy['score']}"

        )

    print()