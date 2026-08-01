"""
==========================================
SULTAN QUANT OS
Institutional Risk Dashboard
Version : 3.6.0
==========================================

Responsibilities:

- Combine validation metrics
- Calculate institutional quality score
- Weight robustness over profitability
- Classify overall risk
- Generate institutional recommendations

Backward Compatible:
- All previous keys remain available

"""


# ==================================================
# EMPTY DASHBOARD
# ==================================================

def empty_dashboard():

    return {

        "quality_score": 0,

        "risk_level": "UNKNOWN",

        "summary": {},

        "recommendations": [],

    }


# ==================================================
# PROFIT FACTOR SCORE
# ==================================================

def calculate_profit_factor_score(statistics):

    pf = statistics.get(
        "profit_factor",
        0,
    )

    if pf >= 2:
        score = 25

    elif pf >= 1.5:
        score = 20

    elif pf >= 1:
        score = 10

    else:
        score = 0

    return pf, score


# ==================================================
# WFO SCORE
# ==================================================

def calculate_wfo_score(wfo_analysis):

    stability = wfo_analysis.get(
        "stability_score",
        0,
    )

    if stability >= 80:
        score = 35

    elif stability >= 60:
        score = 25

    elif stability >= 40:
        score = 15

    else:
        score = 0

    return stability, score


# ==================================================
# MONTE CARLO SCORE
# ==================================================

def calculate_monte_carlo_score(

    monte_carlo_analysis,

):

    robustness = monte_carlo_analysis.get(
        "robustness_score",
        0,
    )

    risk = monte_carlo_analysis.get(
        "risk_level",
        "HIGH",
    )

    if robustness >= 90:

        score = 20

    elif robustness >= 70:

        score = 15

    elif robustness >= 50:

        score = 10

    else:

        score = 0

    return risk, robustness, score


# ==================================================
# DRAWDOWN SCORE
# ==================================================

def calculate_drawdown_score(statistics):

    drawdown = statistics.get(
        "max_drawdown_percent",
        100,
    )

    if drawdown <= 10:

        score = 20

    elif drawdown <= 20:

        score = 15

    elif drawdown <= 30:

        score = 10

    elif drawdown <= 50:

        score = 5

    else:

        score = 0

    return drawdown, score


# ==================================================
# CLASSIFICATION
# ==================================================

def classify_quality(score):

    if score >= 90:

        return "EXCELLENT"

    elif score >= 75:

        return "GOOD"

    elif score >= 60:

        return "ACCEPTABLE"

    elif score >= 40:

        return "WEAK"

    return "FAIL"


# ==================================================
# RECOMMENDATIONS
# ==================================================

def build_recommendations(

    statistics,

    wfo_analysis,

    monte_carlo_analysis,

):

    recommendations = []

    if statistics.get(
        "profit_factor",
        0,
    ) < 2:

        recommendations.append(
            "Improve Profit Factor above 2.0."
        )

    if statistics.get(
        "max_drawdown_percent",
        100,
    ) > 20:

        recommendations.append(
            "Reduce maximum drawdown below 20%."
        )

    if wfo_analysis.get(
        "stability_score",
        0,
    ) < 60:

        recommendations.append(
            "Increase Walk Forward stability."
        )

    if monte_carlo_analysis.get(
        "robustness_score",
        0,
    ) < 80:

        recommendations.append(
            "Improve Monte Carlo robustness."
        )

    if monte_carlo_analysis.get(
        "ruin_probability",
        100,
    ) > 1:

        recommendations.append(
            "Reduce probability of ruin."
        )

    if not recommendations:

        recommendations.append(
            "Institutional validation passed."
        )

    return recommendations


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

    pf, pf_score = calculate_profit_factor_score(
        statistics
    )
    score += pf_score

    stability, wfo_score = calculate_wfo_score(
        wfo_analysis
    )
    score += wfo_score

    mc_risk, robustness, mc_score = calculate_monte_carlo_score(
        monte_carlo_analysis
    )
    score += mc_score

    drawdown, dd_score = calculate_drawdown_score(
        statistics
    )
    score += dd_score

    level = classify_quality(score)

    recommendations = build_recommendations(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )

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

                "monte_carlo_robustness":
                    robustness,

                "confidence_low":
                    monte_carlo_analysis.get(
                        "confidence_low",
                        0,
                    ),

                "confidence_high":
                    monte_carlo_analysis.get(
                        "confidence_high",
                        0,
                    ),

                "value_at_risk_95":
                    monte_carlo_analysis.get(
                        "value_at_risk_95",
                        0,
                    ),

                "conditional_var_95":
                    monte_carlo_analysis.get(
                        "conditional_var_95",
                        0,
                    ),

                "drawdown":
                    drawdown,

                "drawdown_score":
                    dd_score,

            },

        "recommendations":

            recommendations,

    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    statistics = {

        "profit_factor": 1.96,

        "max_drawdown_percent": 20.56,

    }

    wfo = {

        "stability_score": 40,

    }

    monte = {

        "risk_level": "LOW",

        "robustness_score": 100,

        "confidence_low": 10088.75,

        "confidence_high": 10088.75,

        "value_at_risk_95": 10088.75,

        "conditional_var_95": 10088.75,

        "ruin_probability": 0,

    }

    dashboard = build_risk_dashboard(

        statistics,

        wfo,

        monte,

    )

    print("=" * 60)

    print("RISK DASHBOARD")

    print("=" * 60)

    for key, value in dashboard.items():

        print(f"{key:20}: {value}")
        