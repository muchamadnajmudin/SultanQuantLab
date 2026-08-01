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
import statistics


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

       "mean_balance": 0,
       "std_balance": 0,

       "mean_drawdown": 0,
       "std_drawdown": 0,

       "confidence_low": 0,
       "confidence_high": 0,

       "value_at_risk_95": 0,
       "conditional_var_95": 0,

       "robustness_score": 0,
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
# MEAN
# ==================================================

def mean(values):

    if not values:
        return 0

    return sum(values) / len(values)



# ==================================================
# STANDARD DEVIATION
# ==================================================

def standard_deviation(values):

    if len(values) < 2:
        return 0

    return statistics.stdev(values)

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

):

    if not drawdowns:

        return {

            "median_drawdown": 0,

            "worst_drawdown": 0,

            "drawdown_percentile_95": 0,

            "mean_drawdown": 0,

            "std_drawdown": 0,

            "risk_level": "UNKNOWN",

        }


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
# RISK METRICS
# ==================================================

def calculate_confidence_interval(
    balances,
):

    if len(balances) < 2:

        return 0, 0


    avg = mean(balances)

    std = standard_deviation(
        balances
    )


    return (

        round(
            avg - (1.96 * std),
            2,
        ),

        round(
            avg + (1.96 * std),
            2,
        )

    )



def calculate_var_cvar(
    balances,
):

    if not balances:

        return 0, 0


    ordered = sorted(
        balances
    )


    index = int(
        len(ordered) * 0.05
    )


    var = ordered[index]


    tail = [

        x

        for x in ordered

        if x <= var

    ]


    if tail:

        cvar = mean(tail)

    else:

        cvar = var


    return (

        round(var,2),

        round(cvar,2),

    )



def calculate_robustness_score(
    probability_profit,
    ruin_probability,
    worst_drawdown,
):

    score = 100


    score -= ruin_probability


    if probability_profit < 50:

        score -= 20


    if worst_drawdown > 2000:

        score -= 20


    elif worst_drawdown > 1000:

        score -= 10


    return max(
        0,
        round(score,2)
    )   

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

    confidence_low, confidence_high = calculate_confidence_interval(
        balances
    )


    value_at_risk_95, conditional_var_95 = calculate_var_cvar(
        balances
    )


    robustness_score = calculate_robustness_score(

        probability_metrics[
            "probability_profit"
        ],

        probability_metrics[
            "ruin_probability"
        ],

        drawdown_metrics[
            "worst_drawdown"
        ],

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

        "mean_balance":

            balance_metrics[
                "mean_balance"
            ],


        "std_balance":

            balance_metrics[
                "std_balance"
            ],   

        "median_drawdown":

            drawdown_metrics[

                "median_drawdown"

            ],

        "drawdown_percentile_95":

            drawdown_metrics[

                "drawdown_percentile_95"

            ],

        "mean_drawdown":

            drawdown_metrics[
                "mean_drawdown"
            ],


        "std_drawdown":

            drawdown_metrics[
                "std_drawdown"
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