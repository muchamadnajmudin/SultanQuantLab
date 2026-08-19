"""
==========================================
SULTAN QUANT OS
Portfolio Decision Engine
Version : 2.0.0
==========================================

Responsibilities:

- Evaluate portfolio quality
- Evaluate risk
- Select best strategy
- Generate institutional decision
"""

def _safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


def _get_drawdown(statistics):

    return _safe_float(
        statistics.get(
            "max_drawdown_percent",
            statistics.get(
                "max_drawdown",
                0,
            ),
        )
    )


def evaluate_decision(
    risk,
    results,
):
    """
    Institutional portfolio decision.
    """

    if not results:

        return {
            "decision": "NO TRADE",
            "best_strategy": None,
            "profit_factor": 0,
            "drawdown": 0,
            "reason": "No strategy available",
        }

    # ------------------------------------------
    # BEST STRATEGY
    # ------------------------------------------

    best = max(
        results,
        key=lambda x: (
            _safe_float(
                x.get("score", 0)
            ),
            _safe_float(
                x.get("statistics", {}).get(
                    "profit_factor",
                    0,
                )
            ),
        ),
    )

    statistics = best.get(
        "statistics",
        {},
    )

    pf = _safe_float(
        statistics.get(
            "profit_factor",
            0,
        )
    )

    drawdown = _get_drawdown(
        statistics
    )

    risk_status = risk.get(
        "status",
        "HIGH",
    )

    # ------------------------------------------
    # DECISION
    # ------------------------------------------

    if risk_status == "HIGH":

        decision = "BLOCKED"

        reason = (
            "Portfolio risk is too high."
        )

    elif pf < 1.0:

        decision = "NOT RECOMMENDED"

        reason = (
            "Best strategy has negative "
            "trading expectancy."
        )

    elif pf < 1.2:

        decision = "NEEDS OPTIMIZATION"

        reason = (
            "Profit factor is below "
            "institutional minimum."
        )

    elif drawdown > 30:

        decision = "NEEDS OPTIMIZATION"

        reason = (
            "Portfolio drawdown is excessive."
        )

    elif drawdown > 20:

        decision = "CAUTIOUS"

        reason = (
            "Drawdown is elevated."
        )

    elif pf >= 2.0:

        decision = "APPROVED"

        reason = (
            "Strategy meets strong "
            "profitability threshold."
        )

    else:

        decision = "NEEDS OPTIMIZATION"

        reason = (
            "Strategy is profitable but "
            "does not yet meet institutional "
            "quality threshold."
        )

    return {

        "decision":
            decision,

        "best_strategy":
            best.get(
                "name"
            ),

        "profit_factor":
            round(
                pf,
                2,
            ),

        "drawdown":
            round(
                drawdown,
                2,
            ),

        "score":
            round(
                _safe_float(
                    best.get(
                        "score",
                        0,
                    )
                ),
                2,
            ),

        "risk_status":
            risk_status,

        "reason":
            reason,
    }