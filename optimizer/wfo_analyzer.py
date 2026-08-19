"""
============================================================
SULTAN QUANT OS
Walk Forward Optimization Analyzer
Version : 4.0.0
============================================================

Responsibilities:

- Analyze Walk Forward Optimization results
- Calculate validation performance
- Measure consistency
- Measure Profit Factor consistency
- Measure Net Profit consistency
- Detect losing / winning streaks
- Detect overfitting risk
- Generate WFO robustness score
- Preserve backward-compatible output keys

Backward Compatible:

Existing keys remain available:

- total_window
- average_profit_factor
- average_net_profit
- profitable_window
- losing_window
- stability_score
- overfitting_risk

Additional institutional metrics:

- profitable_window_ratio
- pf_ge_1_ratio
- median_profit_factor
- best_profit_factor
- worst_profit_factor
- std_profit_factor
- median_net_profit
- best_net_profit
- worst_net_profit
- std_net_profit
- max_losing_streak
- max_winning_streak
- pf_consistency_score
- return_consistency_score
- wfo_robustness_score
- overfitting_score

============================================================
"""


import statistics


# ============================================================
# EMPTY RESULT
# ============================================================

def empty_analysis():

    return {

        # ----------------------------------------------------
        # Backward-compatible keys
        # ----------------------------------------------------

        "total_window": 0,

        "average_profit_factor": 0,

        "average_net_profit": 0,

        "profitable_window": 0,

        "losing_window": 0,

        "stability_score": 0,

        "overfitting_risk": "UNKNOWN",

        # ----------------------------------------------------
        # Additional institutional metrics
        # ----------------------------------------------------

        "profitable_window_ratio": 0,

        "pf_ge_1_ratio": 0,

        "median_profit_factor": 0,

        "best_profit_factor": 0,

        "worst_profit_factor": 0,

        "std_profit_factor": 0,

        "median_net_profit": 0,

        "best_net_profit": 0,

        "worst_net_profit": 0,

        "std_net_profit": 0,

        "max_losing_streak": 0,

        "max_winning_streak": 0,

        "pf_consistency_score": 0,

        "return_consistency_score": 0,

        "wfo_robustness_score": 0,

        "overfitting_score": 100,

    }


# ============================================================
# SAFE FLOAT
# ============================================================

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


# ============================================================
# SAFE VALIDATION
# ============================================================

def _get_validation(
    item,
):

    if not isinstance(
        item,
        dict,
    ):

        return {}

    validation = item.get(
        "validation",
        {},
    )

    if not isinstance(
        validation,
        dict,
    ):

        return {}

    return validation


# ============================================================
# PROFIT FACTOR
# ============================================================

def _get_profit_factor(
    validation,
):

    return max(
        0.0,
        _safe_float(
            validation.get(
                "profit_factor",
                0,
            ),
            0,
        ),
    )


# ============================================================
# NET PROFIT
# ============================================================

def _get_net_profit(
    validation,
):

    return _safe_float(
        validation.get(
            "net_profit",
            0,
        ),
        0,
    )


# ============================================================
# MEDIAN
# ============================================================

def _median(
    values,
):

    if not values:

        return 0.0

    return statistics.median(
        values
    )


# ============================================================
# STANDARD DEVIATION
# ============================================================

def _standard_deviation(
    values,
):

    if len(values) < 2:

        return 0.0

    return statistics.stdev(
        values
    )


# ============================================================
# PERCENTAGE
# ============================================================

def _percentage(
    numerator,
    denominator,
):

    if denominator <= 0:

        return 0.0

    return (
        numerator
        /
        denominator
        *
        100
    )


# ============================================================
# STREAK ANALYZER
# ============================================================

def _calculate_streaks(
    net_profits,
):

    max_losing_streak = 0
    max_winning_streak = 0

    current_losing = 0
    current_winning = 0

    for net in net_profits:

        if net > 0:

            current_winning += 1
            current_losing = 0

        else:

            current_losing += 1
            current_winning = 0

        if current_winning > max_winning_streak:

            max_winning_streak = (
                current_winning
            )

        if current_losing > max_losing_streak:

            max_losing_streak = (
                current_losing
            )

    return (
        max_losing_streak,
        max_winning_streak,
    )


# ============================================================
# PROFIT FACTOR CONSISTENCY
# ============================================================

def _calculate_pf_consistency_score(
    profit_factors,
):

    if not profit_factors:

        return 0.0

    total = len(
        profit_factors
    )

    # --------------------------------------------------------
    # Percentage of validation windows with PF >= 1
    # --------------------------------------------------------

    profitable_pf = sum(
        1
        for pf in profit_factors
        if pf >= 1.0
    )

    pf_ratio = (
        profitable_pf
        /
        total
    )

    # --------------------------------------------------------
    # Standard deviation penalty
    #
    # Low variation = more consistent.
    # --------------------------------------------------------

    pf_std = _standard_deviation(
        profit_factors
    )

    if pf_std <= 0.10:

        consistency_component = 100

    elif pf_std <= 0.25:

        consistency_component = 90

    elif pf_std <= 0.50:

        consistency_component = 75

    elif pf_std <= 0.75:

        consistency_component = 60

    elif pf_std <= 1.00:

        consistency_component = 45

    else:

        consistency_component = 30

    score = (
        pf_ratio * 70
        +
        consistency_component * 0.30
    )

    return round(
        min(
            max(
                score,
                0,
            ),
            100,
        ),
        2,
    )


# ============================================================
# RETURN CONSISTENCY
# ============================================================

def _calculate_return_consistency_score(
    net_profits,
):

    if not net_profits:

        return 0.0

    total = len(
        net_profits
    )

    profitable = sum(
        1
        for value in net_profits
        if value > 0
    )

    profitable_ratio = (
        profitable
        /
        total
    )

    std_net = _standard_deviation(
        net_profits
    )

    average_net = abs(
        sum(net_profits)
        /
        total
    )

    # --------------------------------------------------------
    # If average return is very small, consistency cannot
    # receive a high score merely because volatility is small.
    # --------------------------------------------------------

    if average_net <= 0:

        magnitude_score = 0

    else:

        coefficient = (
            std_net
            /
            average_net
        )

        if coefficient <= 0.50:

            magnitude_score = 100

        elif coefficient <= 1.00:

            magnitude_score = 85

        elif coefficient <= 1.50:

            magnitude_score = 70

        elif coefficient <= 2.00:

            magnitude_score = 55

        elif coefficient <= 3.00:

            magnitude_score = 40

        else:

            magnitude_score = 25

    score = (
        profitable_ratio * 70
        +
        magnitude_score * 0.30
    )

    return round(
        min(
            max(
                score,
                0,
            ),
            100,
        ),
        2,
    )


# ============================================================
# OVERFITTING SCORE
# ============================================================

def _calculate_overfitting_score(
    stability_score,
    pf_ge_1_ratio,
    average_profit_factor,
    max_losing_streak,
    total_window,
):

    """
    Overfitting score:

    0   = very low concern
    100 = very high concern

    This is a heuristic risk indicator.

    It does NOT claim statistical proof of overfitting.
    """

    if total_window <= 0:

        return 100.0

    score = 0.0

    # --------------------------------------------------------
    # Low profitable-window ratio
    # --------------------------------------------------------

    if stability_score < 40:

        score += 35

    elif stability_score < 50:

        score += 25

    elif stability_score < 60:

        score += 15

    elif stability_score < 70:

        score += 5

    # --------------------------------------------------------
    # Low PF >= 1 ratio
    # --------------------------------------------------------

    if pf_ge_1_ratio < 40:

        score += 30

    elif pf_ge_1_ratio < 50:

        score += 20

    elif pf_ge_1_ratio < 60:

        score += 10

    # --------------------------------------------------------
    # Average PF
    # --------------------------------------------------------

    if average_profit_factor < 0.80:

        score += 25

    elif average_profit_factor < 1.00:

        score += 15

    elif average_profit_factor < 1.20:

        score += 5

    # --------------------------------------------------------
    # Losing streak
    # --------------------------------------------------------

    losing_streak_ratio = (
        max_losing_streak
        /
        total_window
    )

    if losing_streak_ratio >= 0.40:

        score += 15

    elif losing_streak_ratio >= 0.30:

        score += 10

    elif losing_streak_ratio >= 0.20:

        score += 5

    return round(
        min(
            max(
                score,
                0,
            ),
            100,
        ),
        2,
    )


# ============================================================
# OVERFITTING RISK CLASSIFICATION
# ============================================================
def _classify_overfitting_risk(
    overfitting_score,
    stability_score=None,
    average_profit_factor=None,
):
    """
    Classify WFO overfitting risk.

    Backward-compatible behavior:

    - Stability below 50%  -> HIGH
    - Stability 50-69.99%  -> MEDIUM
    - Stability >= 70%     -> LOW

    Additional overfitting score can strengthen the
    classification, but must not make a historically
    MEDIUM WFO result appear LOW merely because other
    metrics are favorable.
    """

    # --------------------------------------------------------
    # No data
    # --------------------------------------------------------

    if stability_score is None:

        if overfitting_score >= 70:

            return "HIGH"

        if overfitting_score >= 40:

            return "MEDIUM"

        return "LOW"

    # --------------------------------------------------------
    # Legacy WFO stability classification
    #
    # This preserves the original SQL behavior.
    # --------------------------------------------------------

    if stability_score < 50:

        return "HIGH"

    if stability_score < 70:

        return "MEDIUM"

    # --------------------------------------------------------
    # Strong stability can still be downgraded if the
    # overfitting score itself is extremely concerning.
    # --------------------------------------------------------

    if overfitting_score >= 70:

        return "HIGH"

    if overfitting_score >= 50:

        return "MEDIUM"

    return "LOW"


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_wfo(
    results: list[dict],
):

    """
    Analyze Walk Forward Optimization results.

    Parameters
    ----------
    results : list[dict]

        Expected structure:

        [
            {
                "validation": {
                    "profit_factor": ...,
                    "net_profit": ...
                }
            }
        ]

    Returns
    -------
    dict

        Complete WFO analysis.

    Backward compatibility
    ----------------------

    Existing keys are preserved.
    """

    if not results:

        return empty_analysis()

    # ========================================================
    # EXTRACT VALIDATION DATA
    # ========================================================

    profit_factors = []

    net_profits = []

    for item in results:

        validation = _get_validation(
            item
        )

        pf = _get_profit_factor(
            validation
        )

        net = _get_net_profit(
            validation
        )

        profit_factors.append(
            pf
        )

        net_profits.append(
            net
        )

    total_window = len(
        results
    )

    # ========================================================
    # BASIC COUNTS
    # ========================================================

    profitable_window = sum(
        1
        for net in net_profits
        if net > 0
    )

    losing_window = (
        total_window
        -
        profitable_window
    )

    # ========================================================
    # PROFIT FACTOR >= 1
    # ========================================================

    pf_ge_1_window = sum(
        1
        for pf in profit_factors
        if pf >= 1.0
    )

    # ========================================================
    # BASIC AVERAGES
    # ========================================================

    average_profit_factor = (
        sum(profit_factors)
        /
        total_window
    )

    average_net_profit = (
        sum(net_profits)
        /
        total_window
    )

    # ========================================================
    # STABILITY
    #
    # BACKWARD COMPATIBLE:
    #
    # stability_score continues to mean:
    # percentage of profitable validation windows.
    # ========================================================

    stability_score = (
        profitable_window
        /
        total_window
        *
        100
    )

    # ========================================================
    # RATIOS
    # ========================================================

    profitable_window_ratio = (
        _percentage(
            profitable_window,
            total_window,
        )
    )

    pf_ge_1_ratio = (
        _percentage(
            pf_ge_1_window,
            total_window,
        )
    )

    # ========================================================
    # DISTRIBUTION METRICS
    # ========================================================

    median_profit_factor = _median(
        profit_factors
    )

    best_profit_factor = max(
        profit_factors
    )

    worst_profit_factor = min(
        profit_factors
    )

    std_profit_factor = (
        _standard_deviation(
            profit_factors
        )
    )

    median_net_profit = _median(
        net_profits
    )

    best_net_profit = max(
        net_profits
    )

    worst_net_profit = min(
        net_profits
    )

    std_net_profit = (
        _standard_deviation(
            net_profits
        )
    )

    # ========================================================
    # STREAKS
    # ========================================================

    (
        max_losing_streak,
        max_winning_streak,
    ) = _calculate_streaks(
        net_profits
    )

    # ========================================================
    # CONSISTENCY SCORES
    # ========================================================

    pf_consistency_score = (
        _calculate_pf_consistency_score(
            profit_factors
        )
    )

    return_consistency_score = (
        _calculate_return_consistency_score(
            net_profits
        )
    )

    # ========================================================
    # OVERFITTING SCORE
    # ========================================================

    overfitting_score = (
        _calculate_overfitting_score(
            stability_score=stability_score,
            pf_ge_1_ratio=pf_ge_1_ratio,
            average_profit_factor=(
                average_profit_factor
            ),
            max_losing_streak=(
                max_losing_streak
            ),
            total_window=total_window,
        )
    )
    
    overfitting_risk = (
        _classify_overfitting_risk(
            overfitting_score,
            stability_score,
            average_profit_factor,
        )
    )


    # ========================================================
    # WFO ROBUSTNESS SCORE
    # ========================================================

    """
    Institutional WFO robustness score.

    Components:

    40% profitable windows
    30% PF consistency
    30% return consistency

    This is deliberately separate from the legacy
    stability_score.
    """

    wfo_robustness_score = (

        stability_score * 0.40

        +

        pf_consistency_score * 0.30

        +

        return_consistency_score * 0.30

    )

    wfo_robustness_score = round(
        min(
            max(
                wfo_robustness_score,
                0,
            ),
            100,
        ),
        2,
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        # ----------------------------------------------------
        # Backward-compatible keys
        # ----------------------------------------------------

        "total_window":
            total_window,

        "average_profit_factor":
            round(
                average_profit_factor,
                2,
            ),

        "average_net_profit":
            round(
                average_net_profit,
                2,
            ),

        "profitable_window":
            profitable_window,

        "losing_window":
            losing_window,

        "stability_score":
            round(
                stability_score,
                2,
            ),

        "overfitting_risk":
            overfitting_risk,

        # ----------------------------------------------------
        # Additional institutional metrics
        # ----------------------------------------------------

        "profitable_window_ratio":
            round(
                profitable_window_ratio,
                2,
            ),

        "pf_ge_1_ratio":
            round(
                pf_ge_1_ratio,
                2,
            ),

        "median_profit_factor":
            round(
                median_profit_factor,
                2,
            ),

        "best_profit_factor":
            round(
                best_profit_factor,
                2,
            ),

        "worst_profit_factor":
            round(
                worst_profit_factor,
                2,
            ),

        "std_profit_factor":
            round(
                std_profit_factor,
                2,
            ),

        "median_net_profit":
            round(
                median_net_profit,
                2,
            ),

        "best_net_profit":
            round(
                best_net_profit,
                2,
            ),

        "worst_net_profit":
            round(
                worst_net_profit,
                2,
            ),

        "std_net_profit":
            round(
                std_net_profit,
                2,
            ),

        "max_losing_streak":
            max_losing_streak,

        "max_winning_streak":
            max_winning_streak,

        "pf_consistency_score":
            pf_consistency_score,

        "return_consistency_score":
            return_consistency_score,

        "wfo_robustness_score":
            wfo_robustness_score,

        "overfitting_score":
            overfitting_score,

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_results = [

        {
            "validation": {
                "profit_factor": 1.50,
                "net_profit": 25,
            }
        },

        {
            "validation": {
                "profit_factor": 1.20,
                "net_profit": 15,
            }
        },

        {
            "validation": {
                "profit_factor": 0.80,
                "net_profit": -10,
            }
        },

        {
            "validation": {
                "profit_factor": 1.40,
                "net_profit": 20,
            }
        },

        {
            "validation": {
                "profit_factor": 0.90,
                "net_profit": -5,
            }
        },

    ]

    analysis = analyze_wfo(
        sample_results
    )

    print(
        "=" * 60
    )

    print(
        "SULTAN QUANT OS"
    )

    print(
        "WFO ANALYZER 4.0.0"
    )

    print(
        "=" * 60
    )

    for key, value in analysis.items():

        print(
            f"{key:30}: {value}"
        )