"""
==========================================
SULTAN QUANT OS
Monte Carlo Analyzer
Version : 4.0.0
==========================================

Responsibilities:

- Analyze Monte Carlo simulations
- Calculate balance statistics
- Calculate drawdown statistics
- Calculate probability metrics
- Classify overall Monte Carlo risk

Backward Compatible:
- All previous keys remain available

"""

import math


# ==================================================
# EMPTY RESULT
# ==================================================

def empty_analysis():

    return {

        "simulation_count": 0,

        "median_balance": 0,

        "best_balance": 0,

        "worst_balance": 0,

        "worst_drawdown": 0,

        "risk_level": "UNKNOWN",

        # New metrics
        "balance_percentile_5": 0,
        "balance_percentile_95": 0,
        "median_drawdown": 0,
        "drawdown_percentile_95": 0,
        "probability_profit": 0,
        "probability_loss": 0,
        "ruin_probability": 0,

    }


# ==================================================
# SORTED COPY
# ==================================================

def sorted_copy(values):

    return sorted(values)


# ==================================================
# PERCENTILE
# ==================================================

def percentile(

    values,

    percent,

):

    if not values:

        return 0

    ordered = sorted_copy(values)

    if percent <= 0:

        return ordered[0]

    if percent >= 1:

        return ordered[-1]

    index = int(

        (len(ordered) - 1)

        * percent

    )

    return ordered[index]


# ==================================================
# MEDIAN
# ==================================================

def median(

    values,

):

    if not values:

        return 0

    ordered = sorted_copy(values)

    n = len(ordered)

    middle = n // 2

    if n % 2 == 0:

        return (

            ordered[middle - 1]

            + ordered[middle]

        ) / 2

    return ordered[middle]


# ==================================================
# PROBABILITY
# ==================================================

def probability(

    values,

    condition,

):

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

def calculate_balance_metrics(

    balances,

):

    return {

        "median_balance":

            round(

                median(

                    balances

                ),

                2,

            ),

        "best_balance":

            round(

                max(

                    balances

                ),

                2,

            ),

        "worst_balance":

            round(

                min(

                    balances

                ),

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

    }


# ==================================================
# DRAWDOWN METRICS
# ==================================================

def calculate_drawdown_metrics(

    drawdowns,

):

    worst_drawdown = max(

        drawdowns

    )

    if worst_drawdown < 1000:

        risk = "LOW"

    elif worst_drawdown < 2500:

        risk = "MEDIUM"

    else:

        risk = "HIGH"

    return {

        "median_drawdown":

            round(

                median(

                    drawdowns

                ),

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

            value <= initial_balance * 0.5,

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
# ANALYZE MONTE CARLO
# ==================================================

def analyze_monte_carlo(
    results: list[dict],
):

    if not results:

        return empty_analysis()

    balances = []

    drawdowns = []

    for item in results:

        balances.append(

            float(

                item.get(

                    "final_balance",

                    0,

                )

            )

        )

        drawdowns.append(

            float(

                item.get(

                    "max_drawdown",

                    0,

                )

            )

        )

    simulation_count = len(

        results

    )

    balance_metrics = calculate_balance_metrics(

        balances

    )

    drawdown_metrics = calculate_drawdown_metrics(

        drawdowns

    )

    probability_metrics = calculate_probability_metrics(

        balances,

        10000,

    )

    analysis = {

        "simulation_count":

            simulation_count,

        # =====================================
        # Existing Keys (Backward Compatible)
        # =====================================

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

        # =====================================
        # New Metrics
        # =====================================

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

    }

    return analysis

    # ==================================================
# TEST
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
        sample_results
    )

    print("=" * 50)
    print("MONTE CARLO ANALYZER")
    print("=" * 50)

    for key, value in analysis.items():

        print(
            f"{key:25}: {value}"
        )