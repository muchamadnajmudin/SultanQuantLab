"""
==========================================
SULTAN QUANT OS
Institutional Report Generator
Version : 3.5.0
==========================================

Responsibilities:

- Combine all validation reports
- Generate final strategy report

"""



# ==================================================
# HEADER
# ==================================================

def section(title):

    return (

        "\n"
        + "=" * 50
        + "\n"
        + title
        + "\n"
        + "=" * 50
        + "\n"

    )



# ==================================================
# GENERATE REPORT
# ==================================================

def generate_institutional_report(

    statistics,

    wfo_analysis,

    monte_carlo_analysis,

    dashboard,

):


    report = ""



    report += section(

        "SULTAN QUANT OS\nINSTITUTIONAL STRATEGY REPORT"

    )



    # ==============================
    # PERFORMANCE
    # ==============================

    report += section(
        "PERFORMANCE"
    )


    report += (

        f"Total Trade       : "
        f"{statistics.get('total_trade',0)}\n"

    )


    report += (

        f"Win Rate          : "
        f"{statistics.get('win_rate',0)}\n"

    )


    report += (

        f"Profit Factor     : "
        f"{statistics.get('profit_factor',0)}\n"

    )


    report += (

        f"Net Profit        : "
        f"{statistics.get('net_profit',0)}\n"

    )



    # ==============================
    # WFO
    # ==============================

    report += section(
        "WALK FORWARD VALIDATION"
    )


    report += (

        f"Windows Tested    : "
        f"{wfo_analysis.get('total_window',0)}\n"

    )


    report += (

        f"Stability Score   : "
        f"{wfo_analysis.get('stability_score',0)}%\n"

    )


    report += (

        f"Overfitting Risk  : "
        f"{wfo_analysis.get('overfitting_risk','UNKNOWN')}\n"

    )



    # ==============================
    # MONTE CARLO
    # ==============================

    report += section(
        "MONTE CARLO VALIDATION"
    )


    report += (

        f"Simulation Count  : "
        f"{monte_carlo_analysis.get('simulation_count',0)}\n"

    )


    report += (

        f"Worst Drawdown    : "
        f"{monte_carlo_analysis.get('worst_drawdown',0)}\n"

    )


    report += (

        f"Risk Level        : "
        f"{monte_carlo_analysis.get('risk_level','UNKNOWN')}\n"

    )



    # ==============================
    # FINAL SCORE
    # ==============================

    report += section(
        "FINAL SCORE"
    )


    report += (

        f"Quality Score     : "
        f"{dashboard.get('quality_score',0)}\n"

    )


    report += (

        f"Rating            : "
        f"{dashboard.get('risk_level','UNKNOWN')}\n"

    )



    return report