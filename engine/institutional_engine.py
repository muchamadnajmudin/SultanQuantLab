"""
==========================================
SULTAN QUANT OS
Institutional Engine
Version : 5.2.1
==========================================

Responsibilities:

- Execute complete institutional pipeline
- Generate reports
- Generate Monte Carlo
- Generate Walk Forward Optimization
- Generate Risk Dashboard
- Generate Institutional Report

"""

from pathlib import Path

from config.settings import DEFAULT_STRATEGY

from config.wfo_settings import (
    WFO_CONFIG,
    WFO_PARAMETER_GRID,
)

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics
from engine.trade_logger import save_trade_journal
from engine.visual_engine import generate_visual_reports

from reports.report_engine import generate_report
from reports.report_writer import save_report
from reports.html_report import generate_html_report

from optimizer.monte_carlo import run_monte_carlo
from optimizer.monte_carlo_analyzer import analyze_monte_carlo

from optimizer.wfo_runner import run_wfo

# ===== PERBAIKAN =====
from optimizer.risk_dashboard import (
    build_risk_dashboard,
)

from reports.institutional_report_engine import (
    build_institutional_report,
)


# ==================================================
# OUTPUT
# ==================================================

OUTPUT_DIR = Path(
    "reports/output"
)

REPORT_FILE = (
    OUTPUT_DIR /
    "backtest_report.txt"
)

TRADE_FILE = (
    OUTPUT_DIR /
    "trade_journal.csv"
)


# ==================================================
# BACKTEST PIPELINE
# ==================================================

def run_backtest_pipeline(
    data_file: str,
):

    df = load_data(
        data_file
    )

    df = calculate_indicators(
        df
    )

    df = run_strategy(
        df,
        strategy=DEFAULT_STRATEGY,
    )

    trades = run_backtest(
        df
    )

    statistics = calculate_statistics(
        trades
    )

    return {

        "data":
            df,

        "trades":
            trades,

        "statistics":
            statistics,

    }


# ==================================================
# REPORTS
# ==================================================

def generate_reports(

    statistics,

    trades,

):

    report = generate_report(
        statistics
    )

    save_report(
        report,
        str(REPORT_FILE),
    )

    html_report = generate_html_report(
        statistics
    )

    save_trade_journal(
        trades,
        str(TRADE_FILE),
    )

    visual_files = generate_visual_reports(
        statistics,
        trades,
    )

    return {

        "text_report":
            REPORT_FILE,

        "html_report":
            html_report,

        "trade_journal":
            TRADE_FILE,

        "visual_files":
            visual_files,

    }


# ==================================================
# MONTE CARLO
# ==================================================

def run_monte_carlo_pipeline(

    trades,

):

    simulations = run_monte_carlo(
        trades
    )

    analysis = analyze_monte_carlo(
        simulations
    )

    return {

        "simulation":
            simulations,

        "analysis":
            analysis,

    }

    # ==================================================
# WFO
# ==================================================

def run_wfo_pipeline(

    data_file,

):

    return run_wfo(

        data_file=data_file,

        parameter_grid=WFO_PARAMETER_GRID,

        config=WFO_CONFIG,

    )


# ==================================================
# RISK DASHBOARD
# ==================================================

def run_risk_pipeline(

    statistics,

    wfo_analysis,

    monte_carlo_analysis,

):

    return build_risk_dashboard(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )


# ==================================================
# INSTITUTIONAL REPORT
# ==================================================

def run_institutional_report(

    statistics,

    monte_carlo,

    wfo,

    risk,

):

    return build_institutional_report(

        statistics=statistics,

        monte_carlo=monte_carlo,

        wfo=wfo,

        risk=risk,

    )


# ==================================================
# COMPLETE PIPELINE
# ==================================================

def execute_pipeline(

    data_file,

):

    # ------------------------------------------
    # BACKTEST
    # ------------------------------------------

    backtest = run_backtest_pipeline(

        data_file

    )

    statistics = backtest["statistics"]

    trades = backtest["trades"]


    # ------------------------------------------
    # REPORTS
    # ------------------------------------------

    reports = generate_reports(

        statistics,

        trades,

    )


    # ------------------------------------------
    # MONTE CARLO
    # ------------------------------------------

    monte = run_monte_carlo_pipeline(

        trades

    )


    # ------------------------------------------
    # WALK FORWARD
    # ------------------------------------------

    wfo = run_wfo_pipeline(

        data_file

    )


    # ------------------------------------------
    # RISK DASHBOARD
    # ------------------------------------------

    risk = run_risk_pipeline(

        statistics,

        wfo["analysis"],

        monte["analysis"],

    )


    # ------------------------------------------
    # INSTITUTIONAL REPORT
    # ------------------------------------------

    institutional = run_institutional_report(

        statistics,

        monte["analysis"],

        wfo["analysis"],

        risk,

    )


    return {

        "statistics":

            statistics,

        "reports":

            reports,

        "monte_carlo":

            monte,

        "wfo":

            wfo,

        "risk":

            risk,

        "institutional":

            institutional,

    }

# ==================================================
# PUBLIC API
# ==================================================

def run_institutional(

    data_file: str,

):

    OUTPUT_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

    result = execute_pipeline(

        data_file

    )

    print()

    print("=" * 60)
    print("SULTAN QUANT OS")
    print("INSTITUTIONAL MODE")
    print("=" * 60)

    print()

    print("PERFORMANCE")

    for key, value in result["statistics"].items():

        if key in [

            "equity_curve",

            "drawdown_curve",

        ]:

            continue

        print(

            f"{key:25}: {value}"

        )

    print()

    print("=" * 60)
    print("GENERATED REPORTS")
    print("=" * 60)

    print(

        f"Text Report        : {result['reports']['text_report']}"

    )

    

    print(

    f"HTML Report        : {result['reports']['html_report']}"

    )

    
    print(

    f"Trade Journal      : {result['reports']['trade_journal']}"

    )


    print()

    print("VISUAL REPORTS")

    for file in result["reports"]["visual_files"]:

        print(

            f" - {file}"

        )

    print()

    print("=" * 60)
    print("MONTE CARLO")
    print("=" * 60)

    for key, value in result["monte_carlo"]["analysis"].items():

        print(

            f"{key:25}: {value}"

        )

    print()

    print("=" * 60)
    print("WALK FORWARD")
    print("=" * 60)

    for key, value in result["wfo"]["analysis"].items():

        print(

            f"{key:25}: {value}"

        )

    print()

    print("=" * 60)
    print("RISK DASHBOARD")
    print("=" * 60)

    for key, value in result["risk"].items():

        print(

            f"{key:25}: {value}"

        )

    print()

    print("=" * 60)
    print("INSTITUTIONAL REPORT")
    print("=" * 60)

    institutional = result["institutional"]

    if isinstance(institutional, dict):

        for key, value in institutional.items():

            print(

                f"{key:25}: {value}"

            )

    else:

        print(institutional)

    print()

    print("=" * 60)
    print("SULTAN QUANT OS INSTITUTIONAL COMPLETE")
    print("=" * 60)

    return result


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    run_institutional(

        "data/XAUUSDc_M1.csv"

    )

