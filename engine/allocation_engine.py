"""
==========================================
SULTAN QUANT OS
Portfolio Allocation Engine
Version : 2.0.0
==========================================

Responsibilities:

- Select qualified strategies
- Calculate dynamic allocation
- Normalize portfolio weights
- Prevent weak strategies from receiving capital
"""

MIN_PROFIT_FACTOR = 1.0
MIN_SCORE = 25
MAX_STRATEGIES = 3


def _safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


def build_allocation(
    results,
    max_strategies=MAX_STRATEGIES,
    minimum_pf=MIN_PROFIT_FACTOR,
    minimum_score=MIN_SCORE,
):
    """
    Build dynamic portfolio allocation.

    Priority:
    1. Strategy score
    2. Profit factor
    3. Positive expectancy
    """

    if not results:
        return []

    candidates = []

    for item in results:

        statistics = item.get(
            "statistics",
            {},
        )

        pf = _safe_float(
            statistics.get(
                "profit_factor",
                0,
            )
        )

        score = _safe_float(
            item.get(
                "score",
                0,
            )
        )

        expectancy = _safe_float(
            statistics.get(
                "expectancy",
                0,
            )
        )

        # --------------------------------------
        # QUALITY FILTER
        # --------------------------------------

        if pf < minimum_pf:
            continue

        if score < minimum_score:
            continue

        if expectancy <= 0:
            continue

        candidate = dict(item)

        # Score-based weight
        candidate["weight"] = max(
            score,
            0,
        )

        candidates.append(candidate)

    # ------------------------------------------
    # FALLBACK
    # ------------------------------------------

    if not candidates:

        for item in results:

            statistics = item.get(
                "statistics",
                {},
            )

            pf = _safe_float(
                statistics.get(
                    "profit_factor",
                    0,
                )
            )

            if pf > 0:

                candidate = dict(item)

                candidate["weight"] = max(
                    _safe_float(
                        item.get(
                            "score",
                            0,
                        )
                    ),
                    1,
                )

                candidates.append(candidate)

    # ------------------------------------------
    # SORT
    # ------------------------------------------

    candidates.sort(
        key=lambda x: (
            x.get("score", 0),
            x.get("statistics", {}).get(
                "profit_factor",
                0,
            ),
        ),
        reverse=True,
    )

    candidates = candidates[
        :max_strategies
    ]

    # ------------------------------------------
    # NORMALIZE
    # ------------------------------------------

    total_weight = sum(
        item["weight"]
        for item in candidates
    )

    if total_weight <= 0:

        equal_weight = (
            1 / len(candidates)
        )

        for item in candidates:
            item["allocation"] = round(
                equal_weight,
                4,
            )

    else:

        for item in candidates:

            item["allocation"] = round(
                item["weight"]
                / total_weight,
                4,
            )

    return candidates