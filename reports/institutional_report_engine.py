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
            f"Mean Balance        : {value(monte_carlo,'mean_balance')}\n"
        )

        text += (
            f"Std Balance         : {value(monte_carlo,'std_balance')}\n"
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

        text += (
            f"Robustness Score    : {value(monte_carlo,'robustness_score')}\n"
        )

        text += (
            f"Confidence Interval : "
            f"{value(monte_carlo,'confidence_low')}"
            f" - "
            f"{value(monte_carlo,'confidence_high')}\n"
        )

        text += (
            f"Value at Risk 95    : "
            f"{value(monte_carlo,'value_at_risk_95')}\n"
        )

        text += (
            f"Conditional VaR 95  : "
            f"{value(monte_carlo,'conditional_var_95')}\n"
        )

    text += "\n"

    # ------------------------------------------
    # WALK FORWARD SUMMARY
    # ------------------------------------------

    if wfo:

        text += (
            f"WFO Stability       : "
            f"{value(wfo,'stability_score')}%\n"
        )

        text += (
            f"WFO Risk            : "
            f"{value(wfo,'overfitting_risk')}\n"
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

        # Existing
        ("simulation_count", "Simulation Count"),
        ("median_balance", "Median Balance"),
        ("best_balance", "Best Balance"),
        ("worst_balance", "Worst Balance"),
        ("worst_drawdown", "Worst Drawdown"),
        ("risk_level", "Risk Level"),

        # Sprint 3.1
        ("balance_percentile_5", "Balance Percentile 5%"),
        ("balance_percentile_95", "Balance Percentile 95%"),

        ("mean_balance", "Mean Balance"),
        ("std_balance", "Std Balance"),

        ("median_drawdown", "Median Drawdown"),
        ("drawdown_percentile_95", "Drawdown Percentile 95%"),

        ("mean_drawdown", "Mean Drawdown"),
        ("std_drawdown", "Std Drawdown"),

        ("probability_profit", "Probability Profit"),
        ("probability_loss", "Probability Loss"),
        ("ruin_probability", "Ruin Probability"),

        ("confidence_low", "Confidence Low"),
        ("confidence_high", "Confidence High"),

        ("value_at_risk_95", "Value at Risk 95%"),
        ("conditional_var_95", "Conditional VaR 95%"),

        ("robustness_score", "Robustness Score"),

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
# METRIC SUMMARY
# Sprint 3.1
# ==================================================

def metric_summary(

    monte_carlo,

):

    report = ""

    report += header(

        "MONTE CARLO METRIC SUMMARY"

    )

    if not monte_carlo:

        report += "No Monte Carlo Result\n"

        return report

    report += (
        f"Mean Balance             : {value(monte_carlo,'mean_balance')}\n"
    )

    report += (
        f"Std Balance              : {value(monte_carlo,'std_balance')}\n"
    )

    report += (
        f"Mean Drawdown            : {value(monte_carlo,'mean_drawdown')}\n"
    )

    report += (
        f"Std Drawdown             : {value(monte_carlo,'std_drawdown')}\n"
    )

    report += (
        f"Confidence Low           : {value(monte_carlo,'confidence_low')}\n"
    )

    report += (
        f"Confidence High          : {value(monte_carlo,'confidence_high')}\n"
    )

    report += (
        f"Value at Risk (95%)      : {value(monte_carlo,'value_at_risk_95')}\n"
    )

    report += (
        f"Conditional VaR (95%)    : {value(monte_carlo,'conditional_var_95')}\n"
    )

    report += (
        f"Robustness Score         : {value(monte_carlo,'robustness_score')}\n"
    )

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

    robustness = value(

        monte_carlo,

        "robustness_score",

        0,

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
        f"Monte Carlo Risk     : {mc_risk}\n"
    )

    report += (
        f"Robustness Score     : {robustness}\n\n"
    )

    if (

        pf >= 2.0
        and dd <= 15
        and stability >= 80
        and robustness >= 90
        and mc_risk == "LOW"

    ):

        assessment = "READY FOR LIVE TRADING"

    elif (

        pf >= 1.5
        and stability >= 60
        and robustness >= 75

    ):

        assessment = "READY FOR FORWARD TEST"

    elif pf >= 1.2:

        assessment = "NEEDS FURTHER OPTIMIZATION"

    else:

        assessment = "NOT RECOMMENDED"

    report += (
        f"Assessment : {assessment}\n"
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

    report += metric_summary(

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