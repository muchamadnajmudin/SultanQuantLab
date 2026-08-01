"""
==========================================
SULTAN QUANT OS
Strategy Analyzer Engine
Version : 1.0.0
==========================================

Responsibilities:

- Analyze strategy performance
- Detect strengths
- Detect weaknesses
- Generate improvement suggestions

Does NOT:
- Execute trades
- Modify strategy
- Change backtest engine
==========================================
"""


def analyze_strategy(
    statistics: dict,
    risk_dashboard: dict | None = None,
):
    """
    Analyze strategy quality.

    Parameters:
        statistics:
            Backtest statistics output

        risk_dashboard:
            Institutional risk dashboard output

    Returns:
        dict
        strategy analysis result
    """

    if not statistics:
        return {
            "score": 0,
            "grade": "EMPTY",
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
        }


    score = 0

    strengths = []
    weaknesses = []
    recommendations = []


    # ======================================
    # PROFIT FACTOR ANALYSIS
    # ======================================

    profit_factor = statistics.get(
        "profit_factor",
        0
    )


    if profit_factor >= 2:
        score += 25
        strengths.append(
            "Excellent profit factor"
        )

    elif profit_factor >= 1.5:
        score += 20
        strengths.append(
            "Positive profit factor"
        )

    else:
        weaknesses.append(
            "Low profit factor"
        )
        recommendations.append(
            "Improve entry filtering"
        )


    # ======================================
    # EXPECTANCY
    # ======================================

    expectancy = statistics.get(
        "expectancy",
        0
    )


    if expectancy > 0:
        score += 20
        strengths.append(
            "Positive expectancy"
        )

    else:
        weaknesses.append(
            "Negative expectancy"
        )


    # ======================================
    # WIN RATE
    # ======================================

    win_rate = statistics.get(
        "win_rate",
        0
    )


    if win_rate >= 50:
        score += 15
        strengths.append(
            "High win rate"
        )

    elif win_rate >= 40:
        score += 10

    else:
        weaknesses.append(
            "Low win rate"
        )


    # ======================================
    # DRAWDOWN
    # ======================================

    drawdown = statistics.get(
        "max_drawdown_percent",
        100
    )


    if drawdown < 20:
        score += 20
        strengths.append(
            "Controlled drawdown"
        )

    elif drawdown < 35:
        score += 10

    else:
        weaknesses.append(
            "High drawdown"
        )
        recommendations.append(
            "Improve risk management"
        )


    # ======================================
    # TRADE COUNT
    # ======================================

    total_trade = statistics.get(
        "total_trade",
        0
    )


    if total_trade >= 50:
        score += 20
        strengths.append(
            "Sufficient trade sample"
        )

    else:
        weaknesses.append(
            "Small trade sample"
        )
        recommendations.append(
            "Collect more historical data"
        )


    # ======================================
    # GRADE
    # ======================================

    if score >= 85:
        grade = "INSTITUTIONAL"

    elif score >= 70:
        grade = "GOOD"

    elif score >= 50:
        grade = "AVERAGE"

    else:
        grade = "WEAK"



    return {

        "score": score,

        "grade": grade,

        "strengths": strengths,

        "weaknesses": weaknesses,

        "recommendations": recommendations,

    }