"""
==========================================
SULTAN QUANT OS
Monte Carlo Analyzer
Version : 3.3.0
==========================================

Responsibilities:

- Analyze Monte Carlo simulations
- Calculate confidence metrics
- Classify risk

"""



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

    }



# ==================================================
# PERCENTILE
# ==================================================

def percentile(
    values,
    percent,
):

    if not values:

        return 0


    values = sorted(values)


    index = int(
        len(values)
        *
        percent
    )


    return values[index]



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

            item.get(
                "final_balance",
                0
            )

        )


        drawdowns.append(

            item.get(
                "max_drawdown",
                0
            )

        )



    simulation_count = len(
        results
    )


    median_balance = (

        sorted(balances)

        [
            simulation_count // 2
        ]

    )



    worst_balance = min(
        balances
    )


    best_balance = max(
        balances
    )


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


        "simulation_count":

            simulation_count,


        "median_balance":

            round(
                median_balance,
                2
            ),


        "best_balance":

            round(
                best_balance,
                2
            ),


        "worst_balance":

            round(
                worst_balance,
                2
            ),


        "worst_drawdown":

            round(
                worst_drawdown,
                2
            ),


        "risk_level":

            risk,

    }