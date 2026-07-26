"""
==========================================
SULTAN QUANT OS
Institutional Risk Dashboard
Version : 3.4.0
==========================================

Responsibilities:

- Combine validation metrics
- Calculate strategy quality score
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



    # ------------------------------
    # Profit Factor
    # ------------------------------

    pf = statistics.get(
        "profit_factor",
        0
    )


    if pf >= 2:

        score += 30

    elif pf >= 1.5:

        score += 20



    # ------------------------------
    # WFO Stability
    # ------------------------------

    stability = wfo_analysis.get(
        "stability_score",
        0
    )


    if stability >= 70:

        score += 30

    elif stability >= 50:

        score += 20



    # ------------------------------
    # Monte Carlo Risk
    # ------------------------------

    risk = monte_carlo_analysis.get(
        "risk_level",
        "HIGH"
    )


    if risk == "LOW":

        score += 40

    elif risk == "MEDIUM":

        score += 20



    # ------------------------------
    # Classification
    # ------------------------------

    if score >= 80:

        level = "INSTITUTIONAL"


    elif score >= 60:

        level = "GOOD"


    elif score >= 40:

        level = "MODERATE"


    else:

        level = "HIGH RISK"



    return {


        "quality_score":

            score,


        "risk_level":

            level,


        "summary":

            {

                "profit_factor":

                    pf,


                "wfo_stability":

                    stability,


                "monte_carlo":

                    risk,

            }

    }