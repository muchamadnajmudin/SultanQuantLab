"""
==========================================
SULTAN QUANT OS
Monte Carlo Analyzer
Version : 4.2.0
==========================================

Responsibilities:

- Analyze Monte Carlo simulations
- Calculate balance statistics
- Calculate drawdown statistics
- Calculate drawdown percentage
- Calculate probability metrics
- Calculate percentile interval
- Calculate confidence interval
- Calculate VaR / CVaR
- Calculate loss VaR / CVaR
- Calculate robustness score
- Classify overall Monte Carlo risk
- Validate simulation results

Backward Compatible:
- All previous keys remain available
"""

import math
import statistics


# ==================================================
# CONSTANTS
# ==================================================

DEFAULT_INITIAL_BALANCE = 10000.0
DEFAULT_CONFIDENCE_LEVEL = 0.95

RUIN_THRESHOLD = 0.50

LOW_DRAWDOWN = 0.10
MEDIUM_DRAWDOWN = 0.20

LOW_ROBUSTNESS = 60
MEDIUM_ROBUSTNESS = 80


# ==================================================
# EMPTY RESULT
# ==================================================

def empty_analysis():
    """
    Return empty Monte Carlo analysis result.
    """

    return {

        # --------------------------------------------------
        # Existing / Backward Compatible
        # --------------------------------------------------

        "simulation_count": 0,

        "median_balance": 0,
        "best_balance": 0,
        "worst_balance": 0,

        "worst_drawdown": 0,
        "risk_level": "UNKNOWN",

        "balance_percentile_5": 0,
        "balance_percentile_95": 0,

        "median_drawdown": 0,
        "drawdown_percentile_95": 0,

        "probability_profit": 0,
        "probability_loss": 0,
        "ruin_probability": 0,

        "mean_balance": 0,
        "std_balance": 0,

        "mean_drawdown": 0,
        "std_drawdown": 0,

        "confidence_low": 0,
        "confidence_high": 0,

        "value_at_risk_95": 0,
        "conditional_var_95": 0,

        "robustness_score": 0,

        # --------------------------------------------------
        # Institutional Metrics
        # --------------------------------------------------

        "valid_simulations": 0,
        "invalid_simulations": 0,

        "loss_var_95": 0,
        "loss_cvar_95": 0,

        "drawdown_percent": 0,
        "median_drawdown_percent": 0,
        "drawdown_percentile_95_percent": 0,

        "mean_drawdown_percent": 0,
        "std_drawdown_percent": 0,

        "percentile_interval_low": 0,
        "percentile_interval_high": 0,

        "confidence_level": DEFAULT_CONFIDENCE_LEVEL,

        "initial_balance": DEFAULT_INITIAL_BALANCE,

        "risk_score": 0,
    }


# ==================================================
# SAFE FLOAT
# ==================================================

def safe_float(value):
    """
    Safely convert a value to float.

    Returns:
        float or None
    """

    try:

        number = float(value)

    except (TypeError, ValueError):

        return None

    if not math.isfinite(number):

        return None

    return number


# ==================================================
# SORTED COPY
# ==================================================

def sorted_copy(values):
    """
    Return sorted copy without modifying original data.
    """

    return sorted(values)


# ==================================================
# PERCENTILE
# ==================================================

def percentile(values, percent):
    """
    Calculate interpolated percentile.

    percent:
        0.00 -> minimum
        0.05 -> 5th percentile
        0.50 -> median
        0.95 -> 95th percentile
        1.00 -> maximum
    """

    if not values:

        return 0

    ordered = sorted_copy(values)

    if percent <= 0:

        return ordered[0]

    if percent >= 1:

        return ordered[-1]

    position = (len(ordered) - 1) * percent

    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))

    if lower_index == upper_index:

        return ordered[lower_index]

    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]

    weight = position - lower_index

    return (
        lower_value
        +
        (upper_value - lower_value) * weight
    )


# ==================================================
# MEDIAN
# ==================================================

def median(values):
    """
    Calculate median.
    """

    if not values:

        return 0

    return statistics.median(values)


# ==================================================
# MEAN
# ==================================================

def mean(values):
    """
    Calculate arithmetic mean.
    """

    if not values:

        return 0

    return sum(values) / len(values)


# ==================================================
# STANDARD DEVIATION
# ==================================================

def standard_deviation(values):
    """
    Calculate sample standard deviation.
    """

    if len(values) < 2:

        return 0

    return statistics.stdev(values)


# ==================================================
# PROBABILITY
# ==================================================

def probability(values, condition):
    """
    Calculate percentage of values satisfying condition.
    """

    if not values:

        return 0

    count = 0

    for value in values:

        if condition(value):

            count += 1

    return round(
        (count / len(values)) * 100,
        2,
    )


# ==================================================
# BALANCE METRICS
# ==================================================

def calculate_balance_metrics(balances):
    """
    Calculate balance statistics.
    """

    if not balances:

        return {

            "median_balance": 0,
            "best_balance": 0,
            "worst_balance": 0,

            "balance_percentile_5": 0,
            "balance_percentile_95": 0,

            "mean_balance": 0,
            "std_balance": 0,

        }

    return {

        "median_balance":
            round(
                median(balances),
                2,
            ),

        "best_balance":
            round(
                max(balances),
                2,
            ),

        "worst_balance":
            round(
                min(balances),
                2,
            ),

        "balance_percentile_5":
            round(
                percentile(
                    balances,
                    0.05,
                ),
                2,
            ),

        "balance_percentile_95":
            round(
                percentile(
                    balances,
                    0.95,
                ),
                2,
            ),

        "mean_balance":
            round(
                mean(balances),
                2,
            ),

        "std_balance":
            round(
                standard_deviation(balances),
                2,
            ),
    }


# ==================================================
# DRAWDOWN METRICS
# ==================================================

def calculate_drawdown_metrics(
    drawdowns,
    initial_balance=DEFAULT_INITIAL_BALANCE,
):
    """
    Calculate absolute and percentage drawdown statistics.

    Risk classification is based primarily on
    drawdown percentage rather than account size.
    """

    if not drawdowns:

        return {

            "median_drawdown": 0,
            "worst_drawdown": 0,

            "drawdown_percentile_95": 0,

            "mean_drawdown": 0,
            "std_drawdown": 0,

            "drawdown_percent": 0,
            "median_drawdown_percent": 0,

            "drawdown_percentile_95_percent": 0,

            "mean_drawdown_percent": 0,
            "std_drawdown_percent": 0,

            "risk_level": "UNKNOWN",

        }

    safe_initial = safe_float(initial_balance)

    if safe_initial is None or safe_initial <= 0:

        safe_initial = DEFAULT_INITIAL_BALANCE

    drawdown_percentages = [

        (
            value
            /
            safe_initial
        )
        * 100

        for value in drawdowns
    ]

    worst_drawdown = max(drawdowns)

    worst_drawdown_percent = (
        worst_drawdown
        /
        safe_initial
    ) * 100

    if worst_drawdown_percent < 10:

        risk = "LOW"

    elif worst_drawdown_percent < 20:

        risk = "MEDIUM"

    else:

        risk = "HIGH"

    return {

        "median_drawdown":
            round(
                median(drawdowns),
                2,
            ),

        "worst_drawdown":
            round(
                worst_drawdown,
                2,
            ),

        "drawdown_percentile_95":
            round(
                percentile(
                    drawdowns,
                    0.95,
                ),
                2,
            ),

        "mean_drawdown":
            round(
                mean(drawdowns),
                2,
            ),

        "std_drawdown":
            round(
                standard_deviation(drawdowns),
                2,
            ),

        "drawdown_percent":
            round(
                worst_drawdown_percent,
                2,
            ),

        "median_drawdown_percent":
            round(
                median(
                    drawdown_percentages
                ),
                2,
            ),

        "drawdown_percentile_95_percent":
            round(
                percentile(
                    drawdown_percentages,
                    0.95,
                ),
                2,
            ),

        "mean_drawdown_percent":
            round(
                mean(
                    drawdown_percentages
                ),
                2,
            ),

        "std_drawdown_percent":
            round(
                standard_deviation(
                    drawdown_percentages
                ),
                2,
            ),

        "risk_level":
            risk,
    }


# ==================================================
# PROBABILITY METRICS
# ==================================================

def calculate_probability_metrics(
    balances,
    initial_balance,
):
    """
    Calculate profit, loss and ruin probabilities.
    """

    profit_probability = probability(
        balances,

        lambda value:
            value > initial_balance,
    )

    loss_probability = probability(
        balances,

        lambda value:
            value < initial_balance,
    )

    ruin_probability = probability(
        balances,

        lambda value:
            value <= (
                initial_balance
                *
                RUIN_THRESHOLD
            ),
    )

    return {

        "probability_profit":
            profit_probability,

        "probability_loss":
            loss_probability,

        "ruin_probability":
            ruin_probability,

    }


# ==================================================
# PERCENTILE INTERVAL
# ==================================================

def calculate_percentile_interval(
    balances,
    confidence_level=DEFAULT_CONFIDENCE_LEVEL,
):
    """
    Calculate empirical percentile interval.

    For 95%:
        lower = 2.5th percentile
        upper = 97.5th percentile
    """

    if not balances:

        return 0, 0

    alpha = (
        1
        -
        confidence_level
    ) / 2

    low = percentile(
        balances,
        alpha,
    )

    high = percentile(
        balances,
        1 - alpha,
    )

    return (
        round(low, 2),
        round(high, 2),
    )


# ==================================================
# CONFIDENCE INTERVAL
# ==================================================

def calculate_confidence_interval(
    balances,
):
    """
    Calculate approximate 95% confidence interval
    for the sample mean.

    Uses:

        mean +/- 1.96 * standard_error

    where:

        standard_error = sample_std / sqrt(n)
    """

    if len(balances) < 2:

        return 0, 0

    avg = mean(balances)

    std = standard_deviation(balances)

    standard_error = (
        std
        /
        math.sqrt(len(balances))
    )

    margin = 1.96 * standard_error

    return (

        round(
            avg - margin,
            2,
        ),

        round(
            avg + margin,
            2,
        ),
    )


# ==================================================
# LOSS METRICS
# ==================================================

def calculate_loss_var_cvar(
    balances,
    initial_balance,
):
    """
    Calculate downside loss VaR / CVaR.

    Loss is measured relative to initial balance.

    Positive number:
        amount at risk.

    Example:

        initial = 10000
        balance = 9950

        loss = 50
    """

    if not balances:

        return 0, 0

    losses = [

        max(
            initial_balance - balance,
            0,
        )

        for balance in balances
    ]

    losses.sort()

    var = percentile(
        losses,
        0.95,
    )

    tail = [

        loss

        for loss in losses

        if loss >= var
    ]

    if tail:

        cvar = mean(tail)

    else:

        cvar = var

    return (

        round(var, 2),

        round(cvar, 2),
    )


# ==================================================
# BACKWARD COMPATIBLE VAR / CVAR
# ==================================================

def calculate_var_cvar(
    balances,
):
    """
    Backward-compatible balance-based VaR / CVaR.

    NOTE:
    These values represent the lower-tail final balance,
    not monetary loss.

    New code should prefer calculate_loss_var_cvar().
    """

    if not balances:

        return 0, 0

    var = percentile(
        balances,
        0.05,
    )

    tail = [

        value

        for value in balances

        if value <= var
    ]

    if tail:

        cvar = mean(tail)

    else:

        cvar = var

    return (

        round(var, 2),

        round(cvar, 2),
    )


# ==================================================
# ROBUSTNESS SCORE
# ==================================================

def calculate_robustness_score(
    probability_profit,
    ruin_probability,
    drawdown_percent,
    loss_cvar_percent=0,
):
    """
    Calculate Monte Carlo robustness score.

    Components:

    1. Probability of profit
    2. Ruin probability
    3. Worst drawdown percentage
    4. Tail loss severity

    Score:
        0 - 100
    """

    score = 100.0

    # --------------------------------------------------
    # Ruin
    # --------------------------------------------------

    score -= ruin_probability

    # --------------------------------------------------
    # Probability of profit
    # --------------------------------------------------

    if probability_profit < 50:

        score -= 20

    elif probability_profit < 60:

        score -= 10

    # --------------------------------------------------
    # Drawdown
    # --------------------------------------------------

    if drawdown_percent > 30:

        score -= 25

    elif drawdown_percent > 20:

        score -= 15

    elif drawdown_percent > 10:

        score -= 5

    # --------------------------------------------------
    # Tail loss
    # --------------------------------------------------

    if loss_cvar_percent > 20:

        score -= 15

    elif loss_cvar_percent > 10:

        score -= 10

    elif loss_cvar_percent > 5:

        score -= 5

    return max(
        0,
        round(
            score,
            2,
        ),
    )


# ==================================================
# RISK SCORE
# ==================================================

def classify_risk_score(score):
    """
    Convert robustness score into risk classification.
    """

    if score >= MEDIUM_ROBUSTNESS:

        return "LOW"

    if score >= LOW_ROBUSTNESS:

        return "MEDIUM"

    return "HIGH"


# ==================================================
# ANALYZE MONTE CARLO
# ==================================================

def analyze_monte_carlo(
    results: list[dict],
    initial_balance=DEFAULT_INITIAL_BALANCE,
    confidence_level=DEFAULT_CONFIDENCE_LEVEL,
):
    """
    Analyze Monte Carlo simulation results.

    Parameters
    ----------
    results:
        List of simulation dictionaries.

    initial_balance:
        Starting account balance.

    confidence_level:
        Confidence level used for percentile interval.
    """

    if not results:

        return empty_analysis()

    safe_initial = safe_float(
        initial_balance
    )

    if safe_initial is None or safe_initial <= 0:

        safe_initial = DEFAULT_INITIAL_BALANCE

    safe_confidence = safe_float(
        confidence_level
    )

    if (
        safe_confidence is None
        or safe_confidence <= 0
        or safe_confidence >= 1
    ):

        safe_confidence = DEFAULT_CONFIDENCE_LEVEL

    balances = []
    drawdowns = []

    invalid_simulations = 0

    # ==================================================
    # VALIDATE SIMULATIONS
    # ==================================================

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            invalid_simulations += 1

            continue

        final_balance = safe_float(
            item.get(
                "final_balance"
            )
        )

        max_drawdown = safe_float(
            item.get(
                "max_drawdown",
                0,
            )
        )

        if final_balance is None:

            invalid_simulations += 1

            continue

        if max_drawdown is None:

            invalid_simulations += 1

            continue

        # --------------------------------------------------
        # Drawdown should never be negative.
        # --------------------------------------------------

        max_drawdown = max(
            0,
            max_drawdown,
        )

        balances.append(
            final_balance
        )

        drawdowns.append(
            max_drawdown
        )

    valid_simulations = len(
        balances
    )

    simulation_count = len(
        results
    )

    if not balances:

        analysis = empty_analysis()

        analysis[
            "simulation_count"
        ] = simulation_count

        analysis[
            "invalid_simulations"
        ] = invalid_simulations

        return analysis

    # ==================================================
    # BALANCE
    # ==================================================

    balance_metrics = (
        calculate_balance_metrics(
            balances
        )
    )

    # ==================================================
    # DRAWDOWN
    # ==================================================

    drawdown_metrics = (
        calculate_drawdown_metrics(
            drawdowns,
            safe_initial,
        )
    )

    # ==================================================
    # PROBABILITY
    # ==================================================

    probability_metrics = (
        calculate_probability_metrics(
            balances,
            safe_initial,
        )
    )

    # ==================================================
    # CONFIDENCE INTERVAL
    # ==================================================

    confidence_low, confidence_high = (
        calculate_confidence_interval(
            balances
        )
    )

    # ==================================================
    # PERCENTILE INTERVAL
    # ==================================================

    percentile_interval_low, percentile_interval_high = (
        calculate_percentile_interval(
            balances,
            safe_confidence,
        )
    )

    # ==================================================
    # BACKWARD COMPATIBLE BALANCE VAR / CVAR
    # ==================================================

    value_at_risk_95, conditional_var_95 = (
        calculate_var_cvar(
            balances
        )
    )

    # ==================================================
    # TRUE LOSS VAR / CVAR
    # ==================================================

    loss_var_95, loss_cvar_95 = (
        calculate_loss_var_cvar(
            balances,
            safe_initial,
        )
    )

    # ==================================================
    # LOSS CVAR AS PERCENT
    # ==================================================

    loss_cvar_percent = 0

    if safe_initial > 0:

        loss_cvar_percent = (
            loss_cvar_95
            /
            safe_initial
        ) * 100

    # ==================================================
    # ROBUSTNESS
    # ==================================================

    robustness_score = (
        calculate_robustness_score(
            probability_metrics[
                "probability_profit"
            ],

            probability_metrics[
                "ruin_probability"
            ],

            drawdown_metrics[
                "drawdown_percent"
            ],

            loss_cvar_percent,
        )
    )

    risk_score = robustness_score

    # ==================================================
    # FINAL ANALYSIS
    # ==================================================

    analysis = {

        # --------------------------------------------------
        # Existing / Backward Compatible
        # --------------------------------------------------

        "simulation_count":
            simulation_count,

        "median_balance":
            balance_metrics[
                "median_balance"
            ],

        "best_balance":
            balance_metrics[
                "best_balance"
            ],

        "worst_balance":
            balance_metrics[
                "worst_balance"
            ],

        "worst_drawdown":
            drawdown_metrics[
                "worst_drawdown"
            ],

        "risk_level":
            drawdown_metrics[
                "risk_level"
            ],

        "balance_percentile_5":
            balance_metrics[
                "balance_percentile_5"
            ],

        "balance_percentile_95":
            balance_metrics[
                "balance_percentile_95"
            ],

        "median_drawdown":
            drawdown_metrics[
                "median_drawdown"
            ],

        "drawdown_percentile_95":
            drawdown_metrics[
                "drawdown_percentile_95"
            ],

        "probability_profit":
            probability_metrics[
                "probability_profit"
            ],

        "probability_loss":
            probability_metrics[
                "probability_loss"
            ],

        "ruin_probability":
            probability_metrics[
                "ruin_probability"
            ],

        "mean_balance":
            balance_metrics[
                "mean_balance"
            ],

        "std_balance":
            balance_metrics[
                "std_balance"
            ],

        "mean_drawdown":
            drawdown_metrics[
                "mean_drawdown"
            ],

        "std_drawdown":
            drawdown_metrics[
                "std_drawdown"
            ],

        "confidence_low":
            confidence_low,

        "confidence_high":
            confidence_high,

        "value_at_risk_95":
            value_at_risk_95,

        "conditional_var_95":
            conditional_var_95,

        "robustness_score":
            robustness_score,

        # --------------------------------------------------
        # Institutional Metrics
        # --------------------------------------------------

        "valid_simulations":
            valid_simulations,

        "invalid_simulations":
            invalid_simulations,

        "loss_var_95":
            loss_var_95,

        "loss_cvar_95":
            loss_cvar_95,

        "drawdown_percent":
            drawdown_metrics[
                "drawdown_percent"
            ],

        "median_drawdown_percent":
            drawdown_metrics[
                "median_drawdown_percent"
            ],

        "drawdown_percentile_95_percent":
            drawdown_metrics[
                "drawdown_percentile_95_percent"
            ],

        "mean_drawdown_percent":
            drawdown_metrics[
                "mean_drawdown_percent"
            ],

        "std_drawdown_percent":
            drawdown_metrics[
                "std_drawdown_percent"
            ],

        "percentile_interval_low":
            percentile_interval_low,

        "percentile_interval_high":
            percentile_interval_high,

        "confidence_level":
            safe_confidence,

        "initial_balance":
            safe_initial,

        "risk_score":
            risk_score,
    }

    return analysis


# ==================================================
# TEST / MANUAL EXECUTION
# ==================================================

if __name__ == "__main__":

    sample_results = [

        {
            "final_balance": 10125.50,
            "max_drawdown": 125.40,
        },

        {
            "final_balance": 9980.75,
            "max_drawdown": 340.10,
        },

        {
            "final_balance": 10450.20,
            "max_drawdown": 210.55,
        },

        {
            "final_balance": 9700.00,
            "max_drawdown": 620.00,
        },

        {
            "final_balance": 10980.80,
            "max_drawdown": 180.25,
        },

    ]

    analysis = analyze_monte_carlo(
        sample_results,
        initial_balance=10000,
    )

    print("=" * 60)
    print("SULTAN QUANT OS")
    print("MONTE CARLO ANALYZER")
    print("=" * 60)

    for key, value in analysis.items():

        print(
            f"{key:35}: {value}"
        )