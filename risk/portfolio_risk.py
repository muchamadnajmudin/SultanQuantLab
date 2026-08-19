"""
==========================================
SULTAN QUANT OS
Portfolio Risk Engine
Version : 2.0.0
==========================================

Responsibilities:

- Calculate portfolio exposure
- Calculate portfolio risk
- Calculate weighted drawdown
- Detect concentration
- Control portfolio exposure
"""

def _safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


def calculate_portfolio_risk(
    allocation,
    max_exposure=1.0,
):
    """
    Accepts:

    Dict:
        {
            "A": 0.5,
            "B": 0.5
        }

    OR list:

        [
            {
                "name": "A",
                "allocation": 0.5,
                "statistics": {...}
            }
        ]
    """

    if not allocation:

        return {
            "exposure": 0.0,
            "risk_score": 0.0,
            "drawdown": 0.0,
            "concentration": 0.0,
            "status": "NORMAL",
        }

    # ------------------------------------------
    # DICT FORMAT
    # ------------------------------------------

    if isinstance(
        allocation,
        dict,
    ):

        weights = [
            _safe_float(value)
            for value in allocation.values()
        ]

        exposure = sum(weights)

        drawdown = 0.0

        concentration = (
            max(weights)
            if weights
            else 0.0
        )

    # ------------------------------------------
    # LIST FORMAT
    # ------------------------------------------

    elif isinstance(
        allocation,
        list,
    ):

        weights = []

        weighted_drawdown = 0.0

        for item in allocation:

            weight = _safe_float(
                item.get(
                    "allocation",
                    0,
                )
            )

            weights.append(weight)

            statistics = item.get(
                "statistics",
                {},
            )

            dd = _safe_float(
                statistics.get(
                    "max_drawdown_percent",
                    statistics.get(
                        "max_drawdown",
                        0,
                    ),
                )
            )

            weighted_drawdown += (
                weight * dd
            )

        exposure = sum(weights)

        drawdown = (
            weighted_drawdown
            if weights
            else 0.0
        )

        concentration = (
            max(weights)
            if weights
            else 0.0
        )

    else:

        raise TypeError(
            "allocation must be dict or list"
        )

    # ------------------------------------------
    # RISK SCORE
    # ------------------------------------------

    exposure_ratio = (
        exposure / max_exposure
        if max_exposure > 0
        else 0
    )

    # Drawdown contribution
    drawdown_score = min(
        drawdown / 20.0,
        1.0,
    )

    # Concentration contribution
    concentration_score = min(
        concentration,
        1.0,
    )

    risk_score = (
        0.5 * exposure_ratio
        + 0.3 * drawdown_score
        + 0.2 * concentration_score
    )

    risk_score = round(
        min(risk_score, 1.0),
        2,
    )

    # ------------------------------------------
    # STATUS
    # ------------------------------------------

    if drawdown > 30:

        status = "HIGH"

    elif drawdown > 20:

        status = "ELEVATED"

    else:

        status = "NORMAL"

    return {

        "exposure":
            round(
                exposure,
                2,
            ),

        "risk_score":
            risk_score,

        "drawdown":
            round(
                drawdown,
                2,
            ),

        "concentration":
            round(
                concentration,
                2,
            ),

        "status":
            status,
    }


def allow_trade(risk):

    return risk.get(
        "status",
        "HIGH",
    ) not in {
        "HIGH",
    }