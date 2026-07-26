"""
==========================================
SULTAN QUANT OS
WFO Analyzer
Version : 3.1.0
==========================================

Analyze Walk Forward Optimization results.

Responsibilities:

- Calculate validation performance
- Measure consistency
- Detect overfitting risk

"""



# ==================================================
# EMPTY RESULT
# ==================================================

def empty_analysis():

    return {

        "total_window": 0,

        "average_profit_factor": 0,

        "average_net_profit": 0,

        "profitable_window": 0,

        "losing_window": 0,

        "stability_score": 0,

        "overfitting_risk": "UNKNOWN",

    }



# ==================================================
# MAIN ANALYZER
# ==================================================

def analyze_wfo(
    results: list[dict],
):


    if not results:

        return empty_analysis()



    total_window = len(results)



    profit_factors = []

    net_profits = []

    profitable = 0

    losing = 0



    for item in results:


        validation = item.get(
            "validation",
            {}
        )


        pf = validation.get(
            "profit_factor",
            0
        )


        net = validation.get(
            "net_profit",
            0
        )


        profit_factors.append(
            pf
        )


        net_profits.append(
            net
        )



        if net > 0:

            profitable += 1

        else:

            losing += 1



    average_pf = (

        sum(profit_factors)
        /
        len(profit_factors)

    )



    average_net = (

        sum(net_profits)
        /
        len(net_profits)

    )



    stability_score = (

        profitable
        /
        total_window
        *
        100

    )



    if stability_score >= 70:

        risk = "LOW"


    elif stability_score >= 50:

        risk = "MEDIUM"


    else:

        risk = "HIGH"



    return {


        "total_window":

            total_window,


        "average_profit_factor":

            round(
                average_pf,
                2
            ),


        "average_net_profit":

            round(
                average_net,
                2
            ),


        "profitable_window":

            profitable,


        "losing_window":

            losing,


        "stability_score":

            round(
                stability_score,
                2
            ),


        "overfitting_risk":

            risk,

    }