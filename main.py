"""
==========================================
SULTAN QUANT OS
Main Pipeline
Version : 2.4.1
==========================================
"""

from pathlib import Path

from config.settings import DEFAULT_STRATEGY

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics
from engine.trade_logger import save_trade_journal

from reports.report_engine import generate_report
from reports.report_writer import save_report


# =====================================================
# CONSTANT
# =====================================================

REPORT_DIR = Path("reports/output")
REPORT_FILE = REPORT_DIR / "backtest_report.txt"
TRADE_JOURNAL = REPORT_DIR / "trade_journal.csv"


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

        # Tidak tampilkan equity curve di console
        if key == "equity_curve":
            continue

        print(f"{key:20}: {value}")

    print("=" * 50)


# =====================================================
# MAIN
# =====================================================

def main():

    # Pastikan folder output tersedia
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print_header()

    # -------------------------------------
    # LOAD DATA
    # -------------------------------------

    print("Loading Data...")

    df = load_data(
        "data/XAUUSDc_M1.csv"
    )

    print("[OK] Data Loaded")

    # -------------------------------------
    # INDICATORS
    # -------------------------------------

    print()
    print("Calculating Indicators...")

    df = calculate_indicators(df)

    print("[OK] Indicator Done")

    # -------------------------------------
    # STRATEGY
    # -------------------------------------

    print()
    print("Running Strategy...")

    df = run_strategy(
        df,
        strategy=DEFAULT_STRATEGY,
    )

    print("[OK] Strategy Done")

    # -------------------------------------
    # BACKTEST
    # -------------------------------------

    print()
    print("Running Backtest...")

    trades = run_backtest(df)

    print("[OK] Backtest Done")

    # -------------------------------------
    # STATISTICS
    # -------------------------------------

    print()
    print("Generating Statistics...")

    stats = calculate_statistics(trades)

    print("[OK] Statistics Done")

    # -------------------------------------
    # PRINT RESULT
    # -------------------------------------

    print_statistics(stats)

    # -------------------------------------
    # SAVE REPORT
    # -------------------------------------

    print()
    print("Saving Report...")

    report = generate_report(stats)

    save_report(
        report,
        str(REPORT_FILE),
    )

    print("[OK] Report Saved")

    # -------------------------------------
    # SAVE TRADE JOURNAL
    # -------------------------------------

    print()
    print("Saving Trade Journal...")

    save_trade_journal(
        trades,
        str(TRADE_JOURNAL),
    )

    print("[OK] Trade Journal Saved")

    print()
    print(f"Report Location : {REPORT_FILE}")
    print(f"Trade Journal   : {TRADE_JOURNAL}")


# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    main()