"""
==========================================
SULTAN QUANT OS
Strategy Weight Engine
Version : 2.0.0
==========================================

Responsibilities:

- Calculate strategy performance weight
- Normalize strategy weights
- Support historical memory
- Penalize insufficient evidence
- Preserve backward compatibility
==========================================
"""

from numbers import Number


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
# CALCULATE WEIGHT
# ==================================================

def calculate_weight(
    performance,
):

    """
    Calculate raw adaptive strategy weight.

    Backward-compatible behavior:

        calculate_weight(statistics)

    New behavior supports:

        {
            "win_rate": ...,
            "profit": ...,
            "profit_factor": ...,
            "expectancy": ...,
            "trades": ...
        }

    The result is intentionally a RAW score.
    normalize_weights() converts it into portfolio weights.
    """

    if not isinstance(
        performance,
        dict,
    ):

        return 0.0

    win_rate = _safe_float(
        performance.get(
            "win_rate",
            0,
        )
    )

    profit = _safe_float(
        performance.get(
            "profit",
            performance.get(
                "net_profit",
                0,
            ),
        )
    )

    profit_factor = _safe_float(
        performance.get(
            "profit_factor",
            0,
        )
    )

    expectancy = _safe_float(
        performance.get(
            "expectancy",
            0,
        )
    )

    trades = _safe_float(
        performance.get(
            "trades",
            performance.get(
                "total_trade",
                performance.get(
                    "total_trades",
                    0,
                ),
            ),
        )
    )

    # --------------------------------------------------
    # Legacy compatibility
    #
    # Existing tests / callers may expect:
    #
    # win_rate + profit
    #
    # Preserve this exact behavior when the newer
    # quality metrics are unavailable.
    # --------------------------------------------------

    advanced_metrics_available = any(

        key in performance

        for key in (
            "profit_factor",
            "expectancy",
            "trades",
            "total_trade",
            "total_trades",
        )

    )

    if not advanced_metrics_available:

        return (

            win_rate
            +
            profit

        )

    # ==================================================
    # INSTITUTIONAL ADAPTIVE SCORE
    # ==================================================

    score = 0.0

    # --------------------------------------------------
    # Win Rate
    # --------------------------------------------------

    score += max(
        0,
        min(
            win_rate,
            100,
        )
    ) * 0.30

    # --------------------------------------------------
    # Profit Factor
    # --------------------------------------------------

    if profit_factor > 0:

        score += (

            min(
                max(
                    profit_factor,
                    0,
                ),
                3,
            )
            /
            3
            *
            30

        )

    # --------------------------------------------------
    # Expectancy
    # --------------------------------------------------

    if expectancy > 0:

        score += min(
            expectancy,
            10,
        ) * 2

    # --------------------------------------------------
    # Profit
    #
    # Only a capped contribution.
    # Prevent enormous backtest profits from completely
    # dominating strategy quality.
    # --------------------------------------------------

    if profit > 0:

        score += min(
            profit,
            100,
        ) * 0.10

    # --------------------------------------------------
    # Reliability
    #
    # More observations = more confidence.
    # --------------------------------------------------

    if trades > 0:

        reliability = min(
            trades / 100,
            1.0,
        )

        score *= (
            0.50
            +
            0.50 * reliability
        )

    return round(
        max(
            score,
            0,
        ),
        6,
    )


# ==================================================
# NORMALIZE WEIGHTS
# ==================================================

def normalize_weights(
    scores,
):

    if not isinstance(
        scores,
        dict,
    ):

        return {}

    if not scores:

        return {}

    clean_scores = {

        key: max(
            0.0,
            _safe_float(
                value,
                0,
            ),
        )

        for key, value
        in scores.items()

    }

    total = sum(
        clean_scores.values()
    )

    if total <= 0:

        return {

            key: 0

            for key
            in clean_scores

        }

    normalized = {

        key: round(
            value / total,
            4,
        )

        for key, value
        in clean_scores.items()

    }

    # --------------------------------------------------
    # Floating point correction
    #
    # Ensure normalized weights sum to exactly 1.0
    # when there is positive total score.
    # --------------------------------------------------

    difference = round(
        1.0
        -
        sum(
            normalized.values()
        ),
        4,
    )

    if difference != 0:

        best_key = max(
            normalized,
            key=normalized.get,
        )

        normalized[best_key] = round(
            normalized[best_key]
            +
            difference,
            4,
        )

    return normalized


# ==================================================
# BUILD WEIGHTS
# ==================================================

def build_weights(
    performances,
):

    """
    Convert:

        {
            strategy: performance
        }

    into normalized adaptive weights.
    """

    if not isinstance(
        performances,
        dict,
    ):

        return {}

    scores = {

        strategy:
            calculate_weight(
                performance
            )

        for strategy, performance
        in performances.items()

    }

    return normalize_weights(
        scores
    )