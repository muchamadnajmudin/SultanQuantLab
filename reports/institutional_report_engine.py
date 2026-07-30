"""
==========================================
SULTAN QUANT OS
Institutional Report Engine
Version : 5.2.1
==========================================

Responsibilities:

- Generate Institutional Research Report
- Merge Backtest
- Merge Monte Carlo
- Merge Walk Forward
- Merge Risk Dashboard
- Produce Executive Summary

"""

from pathlib import Path
from datetime import datetime


# ==================================================
# OUTPUT
# ==================================================

OUTPUT_DIR = Path(
    "reports/output"
)

REPORT_FILE = (
    OUTPUT_DIR /
    "institutional_report.txt"
)


# ==================================================
# HEADER
# ==================================================

def header(title: str):

    return (
        "\n"
        + "=" * 70
        + "\n"
        + title
        + "\n"
        + "=" * 70
        + "\n"
    )


# ==================================================
# SAFE VALUE
# ==================================================

def value(

    dictionary,

    key,

    default="-",

):

    if not dictionary:

        return default

    result = dictionary.get(

        key,

        default,

    )

    if result is None:

        return default

    return result


# ==================================================
# EXECUTIVE SUMMARY
# ==================================================

def executive_summary(

    statistics,

    monte_carlo,

    wfo,

):

    text = ""

    text += header(

        "EXECUTIVE SUMMARY"

    )

    text += (

        f"Generated : "
        f"{datetime.now():%Y-%m-%d %H:%M:%S}\n\n"

    )

    text += (
        f"Net Profit          : {value(statistics,'net_profit')}\n"
    )

    text += (
        f"Profit Factor       : {value(statistics,'profit_factor')}\n"
    )

    text += (
        f"Win Rate            : {value(statistics,'win_rate')}%\n"
    )

    text += (
        f"Max Drawdown        : {value(statistics,'max_drawdown')}\n"
    )

    text += (
        f"Sharpe Ratio        : {value(statistics,'sharpe_ratio')}\n"
    )

    text += "\n"

    # ------------------------------------------
    # MONTE CARLO SUMMARY
    # ------------------------------------------

    if monte_carlo:

        text += (
            f"Monte Carlo Runs    : {value(monte_carlo,'simulation_count')}\n"
        )

        text += (
            f"Median Balance      : {value(monte_carlo,'median_balance')}\n"
        )

        text += (
            f"Best Balance        : {value(monte_carlo,'best_balance')}\n"
        )

        text += (
            f"Worst Balance       : {value(monte_carlo,'worst_balance')}\n"
        )

        text += (
            f"Worst Drawdown      : {value(monte_carlo,'worst_drawdown')}\n"
        )

        text += (
            f"Monte Carlo Risk    : {value(monte_carlo,'risk_level')}\n"
        )

    text += "\n"

    # ------------------------------------------
    # WALK FORWARD SUMMARY
    # ------------------------------------------

    if wfo:

        text += (
            f"WFO Stability       : {value(wfo,'stability_score')}%\n"
        )

        text += (
            f"WFO Risk            : {value(wfo,'overfitting_risk')}\n"
        )

    return text

    # ==================================================
# BACKTEST SECTION
# ==================================================

def backtest_section(

    statistics,

):

    report = ""

    report += header(

        "BACKTEST PERFORMANCE"

    )

    if not statistics:

        report += "No Backtest Result\n"

        return report

    for key, value_ in statistics.items():

        if key in [

            "equity_curve",

            "drawdown_curve",

        ]:

            continue

        report += (

            f"{key:25}: {value_}\n"

        )

    return report


# ==================================================
# MONTE CARLO SECTION
# ==================================================

def monte_carlo_section(

    monte_carlo,

):

    report = ""

    report += header(

        "MONTE CARLO ANALYSIS"

    )

    if not monte_carlo:

        report += "No Monte Carlo Result\n"

        return report

    fields = [

        ("simulation_count", "Simulation Count"),

        ("median_balance", "Median Balance"),

        ("best_balance", "Best Balance"),

        ("worst_balance", "Worst Balance"),

        ("worst_drawdown", "Worst Drawdown"),

        ("risk_level", "Risk Level"),

        # Sprint 3.3

        ("balance_p5", "Balance P5"),

        ("balance_p95", "Balance P95"),

        ("median_drawdown", "Median Drawdown"),

        ("drawdown_p95", "Drawdown P95"),

        ("probability_profit", "Probability Profit"),

        ("probability_loss", "Probability Loss"),

        ("ruin_probability", "Ruin Probability"),

    ]

    for key, label in fields:

        if key in monte_carlo:

            report += (

                f"{label:25}: "

                f"{monte_carlo[key]}\n"

            )

    return report

    # ==================================================
# WALK FORWARD SECTION
# ==================================================

def walk_forward_section(

    wfo,

):

    report = ""

    report += header(

        "WALK FORWARD ANALYSIS"

    )

    if not wfo:

        report += "No Walk Forward Result\n"

        return report

    fields = [

        ("total_window", "Total Window"),

        ("average_profit_factor", "Average Profit Factor"),

        ("average_net_profit", "Average Net Profit"),

        ("stability_score", "Stability Score"),

        ("overfitting_risk", "Overfitting Risk"),

    ]

    for key, label in fields:

        if key in wfo:

            report += (

                f"{label:25}: "

                f"{wfo[key]}\n"

            )

    return report


# ==================================================
# RISK DASHBOARD SECTION
# ==================================================

def risk_section(

    risk,

):

    report = ""

    report += header(

        "RISK DASHBOARD"

    )

    if not risk:

        report += "No Risk Dashboard\n"

        return report

    if isinstance(risk, dict):

        summary = risk.get("summary")

        if isinstance(summary, dict):

            report += "SUMMARY\n"

            report += "-" * 70 + "\n"

            for key, value_ in summary.items():

                report += (

                    f"{key:25}: {value_}\n"

                )

            report += "\n"

        for key, value_ in risk.items():

            if key == "summary":

                continue

            report += (

                f"{key:25}: {value_}\n"

            )

    else:

        report += str(risk) + "\n"

    return report


# ==================================================
# CONCLUSION
# ==================================================

def conclusion(

    statistics,

    wfo,

    monte_carlo=None,

):

    report = ""

    report += header(

        "FINAL CONCLUSION"

    )

    pf = value(

        statistics,

        "profit_factor",

        0,

    )

    dd = value(

        statistics,

        "max_drawdown_percent",

        0,

    )

    stability = value(

        wfo,

        "stability_score",

        0,

    )

    mc_risk = value(

        monte_carlo,

        "risk_level",

        "UNKNOWN",

    )

    report += (

        f"Profit Factor        : {pf}\n"

    )

    report += (

        f"Drawdown (%)         : {dd}\n"

    )

    report += (

        f"WFO Stability (%)    : {stability}\n"

    )

    report += (

        f"Monte Carlo Risk     : {mc_risk}\n\n"

    )

    if (

        pf >= 1.5
        and stability >= 70
        and mc_risk == "LOW"

    ):

        report += (

            "Assessment : READY FOR LIVE TEST\n"

        )

    elif pf >= 1.2:

        report += (

            "Assessment : NEEDS FURTHER OPTIMIZATION\n"

        )

    else:

        report += (

            "Assessment : NOT RECOMMENDED\n"

        )

    return report

    # ==================================================
# MAIN REPORT GENERATOR
# ==================================================

def generate_institutional_report(

    statistics,

    monte_carlo=None,

    wfo=None,

    risk=None,

):

    report = ""

    report += header(

        "SULTAN QUANT OS\nINSTITUTIONAL REPORT"

    )

    report += executive_summary(

        statistics,

        monte_carlo,

        wfo,

    )

    report += backtest_section(

        statistics,

    )

    report += monte_carlo_section(

        monte_carlo,

    )

    report += walk_forward_section(

        wfo,

    )

    report += risk_section(

        risk,

    )

    report += conclusion(

        statistics,

        wfo,

        monte_carlo,

    )

    return report


# ==================================================
# SAVE REPORT
# ==================================================

def save_institutional_report(

    report: str,

    filename=REPORT_FILE,

):

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    filename = Path(filename)

    filename.write_text(

        report,

        encoding="utf-8",

    )

    return filename


# ==================================================
# BUILD + SAVE
# ==================================================

def build_institutional_report(

    statistics,

    monte_carlo=None,

    wfo=None,

    risk=None,

):

    report = generate_institutional_report(

        statistics=statistics,

        monte_carlo=monte_carlo,

        wfo=wfo,

        risk=risk,

    )

    report_file = save_institutional_report(

        report,

    )

    return {

        "report": report,

        "report_file": report_file,

    }