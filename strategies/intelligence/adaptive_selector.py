"""
==========================================
SULTAN QUANT OS
Adaptive Strategy Selector
Version : 2.1.0
==========================================

Responsibilities:

- Select strategy from adaptive weights
- Support candidate restriction
- Support minimum weight
- Rank adaptive candidates
- Calculate selection confidence
- Support fallback strategy
- Preserve backward compatibility

Architecture:

Strategy Memory
       ↓
Strategy Weight
       ↓
Adaptive Selector
       ↓
Selected Strategy
       ↓
Execution / Portfolio
==========================================
"""


# ==================================================
# SAFE FLOAT
# ==================================================

def _safe_float(
    value,
    default=0.0,
):

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==================================================
# PREPARE AVAILABLE WEIGHTS
# ==================================================

def _prepare_weights(
    weights,
    candidates=None,
    minimum_weight=0.0,
):

    if not isinstance(
        weights,
        dict,
    ):

        return {}

    if not weights:

        return {}

    # --------------------------------------------------
    # Candidate restriction
    # --------------------------------------------------

    if candidates is not None:

        try:

            candidate_set = set(
                candidates
            )

        except TypeError:

            return {}

        available = {

            strategy: weight

            for strategy, weight
            in weights.items()

            if strategy in candidate_set

        }

    else:

        available = dict(
            weights
        )

    if not available:

        return {}

    # --------------------------------------------------
    # Minimum weight
    # --------------------------------------------------

    minimum_weight = _safe_float(
        minimum_weight,
        0.0,
    )

    return {

        strategy: _safe_float(
            weight,
            0.0,
        )

        for strategy, weight
        in available.items()

        if _safe_float(
            weight,
            0.0,
        ) >= minimum_weight

    }


# ==================================================
# RANK STRATEGIES
# ==================================================

def rank_strategies(
    weights,
    candidates=None,
    minimum_weight=0.0,
):

    """
    Return strategies ordered by adaptive weight.

    Example:

        {
            "price_action": 0.45,
            "breakout": 0.35,
            "fibonacci": 0.20
        }

    returns:

        [
            {
                "strategy": "price_action",
                "weight": 0.45,
                "rank": 1,
            },
            ...
        ]
    """

    available = _prepare_weights(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
    )

    if not available:

        return []

    ranked = sorted(
        available.items(),
        key=lambda item: (
            item[1],
            item[0],
        ),
        reverse=True,
    )

    return [

        {
            "strategy": strategy,
            "weight": weight,
            "rank": index,
        }

        for index, (
            strategy,
            weight,
        )
        in enumerate(
            ranked,
            start=1,
        )

    ]


# ==================================================
# SELECTION CONFIDENCE
# ==================================================

def calculate_selection_confidence(
    weights,
    candidates=None,
    minimum_weight=0.0,
):

    """
    Calculate confidence of the adaptive selection.

    Confidence is based on the dominance of the
    highest-weight strategy relative to all available
    candidates.

    Returns a value between 0 and 1.

    Examples:

        One dominant strategy:
            confidence → high

        Nearly equal strategies:
            confidence → low
    """

    available = _prepare_weights(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
    )

    if not available:

        return 0.0

    positive = {

        strategy: weight

        for strategy, weight
        in available.items()

        if weight > 0

    }

    if not positive:

        return 0.0

    total = sum(
        positive.values()
    )

    if total <= 0:

        return 0.0

    best = max(
        positive.values()
    )

    confidence = best / total

    return round(
        min(
            max(
                confidence,
                0.0,
            ),
            1.0,
        ),
        4,
    )


# ==================================================
# SELECT BEST STRATEGY
# ==================================================

def select_best_strategy(
    weights,
    candidates=None,
    minimum_weight=0.0,
    fallback=None,
):

    """
    Select highest-weight strategy.

    Backward-compatible:

        select_best_strategy(weights)

    Advanced:

        select_best_strategy(
            weights,
            candidates=[
                "price_action",
                "breakout",
            ],
        )

    Minimum weight:

        select_best_strategy(
            weights,
            minimum_weight=0.20,
        )

    Fallback:

        select_best_strategy(
            weights,
            minimum_weight=0.50,
            fallback="price_action",
        )

    Strategies outside candidates are ignored.

    If no strategy passes the filters:

        fallback is returned if provided,
        otherwise None.
    """

    available = _prepare_weights(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
    )

    if not available:

        return fallback

    return max(
        available,
        key=available.get,
    )


# ==================================================
# SELECT WITH METADATA
# ==================================================

def select_strategy_details(
    weights,
    candidates=None,
    minimum_weight=0.0,
    fallback=None,
):

    """
    Return complete adaptive selection metadata.

    Example:

        {
            "strategy": "price_action",
            "weight": 0.52,
            "rank": 1,
            "confidence": 0.52,
            "candidate_count": 3,
            "fallback_used": False,
        }
    """

    ranked = rank_strategies(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
    )

    if ranked:

        selected = ranked[0]

        return {

            "strategy":
                selected["strategy"],

            "weight":
                selected["weight"],

            "rank":
                selected["rank"],

            "confidence":
                calculate_selection_confidence(
                    weights,
                    candidates=candidates,
                    minimum_weight=minimum_weight,
                ),

            "candidate_count":
                len(ranked),

            "fallback_used":
                False,

        }

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    if fallback is not None:

        return {

            "strategy":
                fallback,

            "weight":
                0.0,

            "rank":
                0,

            "confidence":
                0.0,

            "candidate_count":
                0,

            "fallback_used":
                True,

        }

    return {

        "strategy":
            None,

        "weight":
            0.0,

        "rank":
            0,

        "confidence":
            0.0,

        "candidate_count":
            0,

        "fallback_used":
            False,

    }


# ==================================================
# TOP N STRATEGIES
# ==================================================

def get_top_strategies(
    weights,
    top_n=3,
    candidates=None,
    minimum_weight=0.0,
):

    """
    Return top N adaptive strategies.
    """

    ranked = rank_strategies(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
    )

    try:

        top_n = int(
            top_n
        )

    except (
        TypeError,
        ValueError,
    ):

        top_n = 3

    if top_n <= 0:

        return []

    return ranked[:top_n]


# ==================================================
# HAS QUALIFIED STRATEGY
# ==================================================

def has_qualified_strategy(
    weights,
    candidates=None,
    minimum_weight=0.0,
):

    """
    Return True when at least one strategy passes
    candidate and minimum-weight filters.
    """

    return bool(
        _prepare_weights(
            weights,
            candidates=candidates,
            minimum_weight=minimum_weight,
        )
    )


# ==================================================
# PRINT SELECTION
# ==================================================

def print_selection(
    weights,
    candidates=None,
    minimum_weight=0.0,
    fallback=None,
):

    """
    Print institutional adaptive selection summary.
    """

    details = select_strategy_details(
        weights,
        candidates=candidates,
        minimum_weight=minimum_weight,
        fallback=fallback,
    )

    print()

    print("=" * 60)
    print("ADAPTIVE STRATEGY SELECTION")
    print("=" * 60)

    print(
        f"{'Strategy':<25}: "
        f"{details['strategy']}"
    )

    print(
        f"{'Weight':<25}: "
        f"{details['weight']}"
    )

    print(
        f"{'Rank':<25}: "
        f"{details['rank']}"
    )

    print(
        f"{'Confidence':<25}: "
        f"{details['confidence']}"
    )

    print(
        f"{'Candidates':<25}: "
        f"{details['candidate_count']}"
    )

    print(
        f"{'Fallback Used':<25}: "
        f"{details['fallback_used']}"
    )

    print()


# ==================================================
# BACKWARD COMPATIBILITY ALIAS
# ==================================================

select_strategy = select_best_strategy