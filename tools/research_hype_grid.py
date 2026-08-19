"""
==========================================
SULTAN QUANT OS
HYPEUSDT Grid Research
Version : 1.0.1
==========================================
"""

from pathlib import Path
import sys

import pandas as pd


# ============================================================
# PROJECT ROOT
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from engine.grid_research import (
    GridResearchEngine,
    print_research_report,
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "bitget"
    / "HYPEUSDT_5m.csv"
)


OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "bitget"
    / "HYPEUSDT_5m_grid_research.csv"
)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("SULTAN QUANT OS")
    print("HYPEUSDT GRID RESEARCH")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK DATA
    # --------------------------------------------------------

    if not DATA_FILE.exists():

        raise FileNotFoundError(
            f"Data not found: {DATA_FILE}"
        )

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = pd.read_csv(
        DATA_FILE
    )

    print(
        f"Loaded candles : {len(df):,}"
    )

    print(
        f"Data file      : {DATA_FILE}"
    )

    # --------------------------------------------------------
    # RESEARCH ENGINE
    #
    # 5-minute candles
    # 288 candles = 24 hours
    # --------------------------------------------------------

    engine = GridResearchEngine(
        df,
        horizon_bars=288,
    )

    # --------------------------------------------------------
    # GRID LEVELS TO RESEARCH
    # --------------------------------------------------------

    drawdown_levels = [
        0.005,
        0.0075,
        0.010,
        0.0125,
        0.015,
        0.020,
        0.025,
        0.030,
    ]

    recovery_levels = [
        0.005,
        0.0075,
        0.010,
        0.0125,
        0.015,
        0.020,
    ]

    # --------------------------------------------------------
    # RUN RESEARCH
    # --------------------------------------------------------

    result = engine.research(
        drawdown_levels=drawdown_levels,
        recovery_levels=recovery_levels,
    )

    # --------------------------------------------------------
    # PRINT REPORT
    # --------------------------------------------------------

    print_research_report(
        result
    )

    # --------------------------------------------------------
    # SAVE MAE / MFE DATA
    # --------------------------------------------------------

    output = df.copy()

    output["MAE"] = result.mae

    output["MFE"] = result.mfe

    output.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print(
        f"Research CSV : {OUTPUT_FILE}"
    )

    print()
    print("=" * 70)
    print("GRID RESEARCH COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()