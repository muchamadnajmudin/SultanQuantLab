"""
==========================================
SULTAN QUANT OS
Institutional Risk Dashboard
Version : 3.5.0
==========================================

Responsibilities:

- Combine validation metrics
- Calculate institutional quality score
- Weight robustness over profitability
- Classify overall risk

"""


# ==================================================
# EMPTY DASHBOARD
# ==================================================

def empty_dashboard():

    return {

        "quality_score": 0,

        "risk_level": "UNKNOWN",

        "summary": {},

    }



# ==================================================
# BUILD DASHBOARD
# ==================================================

def build_risk_dashboard(

    statistics,
    wfo_analysis,
    monte_carlo_analysis,

):


    if not statistics:

        return empty_dashboard()



    score = 0



    # ==================================================
    # PROFIT FACTOR SCORE
    # Weight : 25%
    # ==================================================

    pf = statistics.get(
        "profit_factor",
        0
    )


    if pf >= 2:

        pf_score = 25

    elif pf >= 1.5:

        pf_score = 20

    elif pf >= 1:

        pf_score = 10

    else:

        pf_score = 0



    score += pf_score



    # ==================================================
    # WFO STABILITY SCORE
    # Weight : 35%
    # ==================================================

    stability = wfo_analysis.get(
        "stability_score",
        0
    )


    if stability >= 80:

        wfo_score = 35

    elif stability >= 60:

        wfo_score = 25

    elif stability >= 40:

        wfo_score = 15

    else:

        wfo_score = 0



    score += wfo_score



    # ==================================================
    # MONTE CARLO SCORE
    # Weight : 20%
    # ==================================================

    mc_risk = monte_carlo_analysis.get(
        "risk_level",
        "HIGH"
    )


    if mc_risk == "LOW":

        mc_score = 20

    elif mc_risk == "MEDIUM":

        mc_score = 10

    else:

        mc_score = 0



    score += mc_score



    # ==================================================
    # DRAWDOWN SCORE
    # Weight : 20%
    # ==================================================

    drawdown = statistics.get(
        "max_drawdown_percent",
        100
    )


    if drawdown <= 10:

        dd_score = 20

    elif drawdown <= 20:

        dd_score = 15

    elif drawdown <= 30:

        dd_score = 10

    elif drawdown <= 50:

        dd_score = 5

    else:

        dd_score = 0



    score += dd_score



    # ==================================================
    # CLASSIFICATION
    # ==================================================

    if score >= 90:

        level = "EXCELLENT"


    elif score >= 75:

        level = "GOOD"


    elif score >= 60:

        level = "ACCEPTABLE"


    elif score >= 40:

        level = "WEAK"


    else:

        level = "FAIL"



    return {


        "quality_score":

            round(score, 2),



        "risk_level":

            level,



        "summary":

            {


                "profit_factor":

                    pf,


                "profit_factor_score":

                    pf_score,


                "wfo_stability":

                    stability,


                "wfo_score":

                    wfo_score,


                "monte_carlo":

                    mc_risk,


                "monte_carlo_score":

                    mc_score,


                "drawdown":

                    drawdown,


                "drawdown_score":

                    dd_score,

            }

    }