"""
==========================================
SULTAN QUANT OS
Main Pipeline
Version : 5.0.1
==========================================
"""

import sys
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


from optimizer.wfo_runner import run_wfo


from reports.report_engine import generate_report
from reports.report_writer import save_report
from reports.html_report import generate_html_report



# =====================================================
# CONSTANT
# =====================================================

REPORT_DIR = Path(
    "reports/output"
)


REPORT_FILE = (
    REPORT_DIR /
    "backtest_report.txt"
)


TRADE_JOURNAL = (
    REPORT_DIR /
    "trade_journal.csv"
)



# =====================================================
# DISPLAY
# =====================================================

def print_header():

    print("=" * 50)
    print("SULTAN QUANT OS")
    print("=" * 50)
    print()



def print_statistics(stats: dict):

    print()
    print("=" * 50)
    print("BACKTEST RESULT")
    print("=" * 50)


    for key, value in stats.items():

        if key in [

            "equity_curve",

            "drawdown_curve"

        ]:

            continue


        print(
            f"{key:20}: {value}"
        )


    print("=" * 50)



# =====================================================
# WFO MODE
# =====================================================

def run_wfo_mode():


    print("=" * 50)
    print("SULTAN QUANT OS WFO MODE")
    print("=" * 50)



    result = run_wfo(

        data_file="data/XAUUSDc_M1.csv",

        parameter_grid=WFO_PARAMETER_GRID,

        config=WFO_CONFIG,

    )



    print()

    print("=" * 50)
    print("WFO RESULT")
    print("=" * 50)



    for key, value in result["analysis"].items():


        print(

            f"{key:25}: {value}"

        )



    print()

    print(
        "WFO Report :"
    )


    print(
        result["report_file"]
    )



    print()

    print(
        "SULTAN QUANT OS WFO COMPLETE"
    )



# =====================================================
# NORMAL BACKTEST MODE
# =====================================================

def main():


    REPORT_DIR.mkdir(

        parents=True,

        exist_ok=True

    )


    print_header()



    print("Loading Data...")


    df = load_data(

        "data/XAUUSDc_M1.csv"

    )


    print("[OK] Data Loaded")



    print()

    print(
        "Calculating Indicators..."
    )


    df = calculate_indicators(df)


    print(
        "[OK] Indicator Done"
    )



    print()

    print(
        "Running Strategy..."
    )


    df = run_strategy(

        df,

        strategy=DEFAULT_STRATEGY,

    )


    print(
        "[OK] Strategy Done"
    )



    print()

    print(
        "Running Backtest..."
    )


    trades = run_backtest(df)


    print(
        "[OK] Backtest Done"
    )



    print()

    print(
        "Generating Statistics..."
    )


    stats = calculate_statistics(

        trades

    )


    print(
        "[OK] Statistics Done"
    )



    print_statistics(stats)



    # -------------------------------------
    # TEXT REPORT
    # -------------------------------------

    print()

    print(
        "Saving Report..."
    )


    report = generate_report(

        stats

    )


    save_report(

        report,

        str(REPORT_FILE)

    )


    print(
        "[OK] Report Saved"
    )



    # -------------------------------------
    # HTML REPORT
    # -------------------------------------

    print()

    print(
        "Generating HTML Report..."
    )


    html_report = generate_html_report(

        stats

    )


    print(
        "[OK] HTML Report Saved"
    )


    print(
        f" - {html_report}"
    )



    # -------------------------------------
    # TRADE JOURNAL
    # -------------------------------------

    print()

    print(
        "Saving Trade Journal..."
    )


    save_trade_journal(

        trades,

        str(TRADE_JOURNAL)

    )


    print(
        "[OK] Trade Journal Saved"
    )



    # -------------------------------------
    # VISUAL
    # -------------------------------------

    print()

    print(
        "Generating Visual Analytics..."
    )


    visual_files = generate_visual_reports(

        stats,

        trades

    )


    print(
        "[OK] Visual Reports Generated"
    )



    for file in visual_files:

        print(
            f" - {file}"
        )



    print()

    print(
        f"Report Location : {REPORT_FILE}"
    )


    print(
        f"HTML Report     : {html_report}"
    )


    print(
        f"Trade Journal   : {TRADE_JOURNAL}"
    )


    print()

    print(
        "SULTAN QUANT OS COMPLETE"
    )



# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":


    if "--wfo" in sys.argv:

        run_wfo_mode()


    else:

        main()