"""
==========================================
SULTAN QUANT OS
WFO Advanced Report Engine
Version : 5.1.0
==========================================

Responsibilities:

- Generate detailed WFO research report
- Summarize parameter stability
- Analyze validation performance

"""


from collections import Counter
from datetime import datetime



# ==================================================
# HEADER
# ==================================================

def _header(title):

    return (
        "\n"
        + "=" * 60
        + "\n"
        + title
        + "\n"
        + "=" * 60
        + "\n"
    )



# ==================================================
# PARAMETER STABILITY
# ==================================================

def analyze_parameter_stability(
    results:list[dict],
):


    if not results:

        return {}



    parameters = []



    for item in results:


        parameter = item.get(
            "best_parameter",
            {}
        )


        parameters.append(

            (
                parameter.get(
                    "RSI_OVERSOLD",
                    0
                ),

                parameter.get(
                    "RSI_OVERBOUGHT",
                    0
                )

            )

        )



    counter = Counter(
        parameters
    )



    return {

        "most_used":

            counter.most_common(1)[0][0],

        "frequency":

            counter.most_common(1)[0][1],

        "total":

            len(parameters),

    }



# ==================================================
# SCORE
# ==================================================

def calculate_wfo_score(
    analysis:dict,
):


    stability = analysis.get(
        "stability_score",
        0
    )


    avg_pf = analysis.get(
        "average_profit_factor",
        0
    )



    score = 0



    score += min(
        stability,
        50
    )



    if avg_pf >= 1:

        score += 25



    if avg_pf >= 1.5:

        score += 25



    return round(
        score,
        2
    )



# ==================================================
# REPORT
# ==================================================

def generate_wfo_advanced_report(
    analysis:dict,
    results:list[dict],
):


    report = ""



    report += _header(
        "SULTAN QUANT OS\n"
        "ADVANCED WFO REPORT"
    )



    report += (

        f"Generated : "
        f"{datetime.now():%Y-%m-%d %H:%M:%S}\n\n"

    )



    report += (

        f"Total Window      : "
        f"{analysis.get('total_window',0)}\n"

    )


    report += (

        f"Average PF        : "
        f"{analysis.get('average_profit_factor',0)}\n"

    )


    report += (

        f"Average Net       : "
        f"{analysis.get('average_net_profit',0)}\n"

    )


    report += (

        f"Stability Score   : "
        f"{analysis.get('stability_score',0)}%\n"

    )


    report += (

        f"Overfitting Risk  : "
        f"{analysis.get('overfitting_risk','UNKNOWN')}\n"

    )



    score = calculate_wfo_score(
        analysis
    )



    report += (

        f"WFO Score        : "
        f"{score}/100\n"

    )



    stability = analyze_parameter_stability(
        results
    )



    report += _header(
        "PARAMETER STABILITY"
    )



    if stability:


        report += (

            f"Most Used RSI Parameter : "
            f"{stability['most_used']}\n"

        )


        report += (

            f"Frequency              : "
            f"{stability['frequency']}/"
            f"{stability['total']}\n"

        )



    report += _header(
        "WINDOW SUMMARY"
    )



    for item in results:


        validation = item.get(
            "validation",
            {}
        )


        report += (

            f"\nWindow {item.get('window')}\n"

        )


        report += (

            f"Parameter : "
            f"{item.get('best_parameter')}\n"

        )


        report += (

            f"PF        : "
            f"{validation.get('profit_factor',0)}\n"

        )


        report += (

            f"Net       : "
            f"{validation.get('net_profit',0)}\n"

        )


        report += "-" * 40



    return report