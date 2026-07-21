"""
==========================================
SULTAN QUANT OS
Main Pipeline
Version : 2.2
==========================================
"""

from config.settings import DEFAULT_STRATEGY

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics

from reports.report_engine import generate_report
from reports.report_writer import save_report


# =====================================================
# DISPLAY
# =====================================================

def print_header():

    print("=" * 50)
    print("SULTAN QUANT OS")
    print("=" * 50)


def print_statistics(stats: dict):

    print()
    print("=" * 50)
    print("BACKTEST RESULT")
    print("=" * 50)

    for key, value in stats.items():
        print(f"{key:20}: {value}")

    print("=" * 50)


# =====================================================
# MAIN
# =====================================================

def main():

    print_header()

    # -------------------------------------
    # LOAD DATA
    # -------------------------------------

    print("Loading Data...")

    df = load_data(
        "data/XAUUSDc_M1.csv"
    )

    print("✓ Data Loaded")

    # -------------------------------------
    # INDICATORS
    # -------------------------------------

    print("Calculating Indicators...")

    df = calculate_indicators(df)

    print("✓ Indicator Done")

    # -------------------------------------
    # STRATEGY
    # -------------------------------------

    print("Running Strategy...")

    df = run_strategy(
        df,
        strategy=DEFAULT_STRATEGY,
    )

    print("✓ Strategy Done")

    # -------------------------------------
    # BACKTEST
    # -------------------------------------

    print("Running Backtest...")

    trades = run_backtest(df)

    print("✓ Backtest Done")

    # -------------------------------------
    # STATISTICS
    # -------------------------------------

    print("Generating Statistics...")

    stats = calculate_statistics(trades)

    print("✓ Statistics Done")

    # -------------------------------------
    # PRINT RESULT
    # -------------------------------------

    print_statistics(stats)

    # -------------------------------------
    # SAVE REPORT
    # -------------------------------------

    print("Saving Report...")

    report = generate_report(stats)

    save_report(
        report,
        "backtest_report.txt",
    )

    print("✓ Report Saved")

    print()
    print("Report Location : reports/backtest_report.txt")


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    main()