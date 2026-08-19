"""
SULTAN QUANT OS
Tool : Flexible HYPEUSDT Grid Optimizer
Version: 2.1.0

Run from project root:
    python tools\run_grid_optimizer.py
"""

from pathlib import Path
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from optimizer.grid_optimizer import (
    optimize_flexible_grid,
    best_by_capital_and_layers,
    save_optimizer_result,
)


DATA = ROOT / "data" / "bitget" / "HYPEUSDT_5m.csv"
OUTPUT = ROOT / "data" / "bitget" / "HYPEUSDT_5m_grid_flexible_optimization.csv"


def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Data not found: {DATA}")

    df = pd.read_csv(DATA)

    print("=" * 110)
    print("SULTAN QUANT OS - HYPEUSDT FLEXIBLE GRID OPTIMIZER")
    print("=" * 110)
    print(f"Candles : {len(df):,}")
    print()
    print("Searching:")
    print("  Capital : $15, $30, $50, $100, $250, $500")
    print("  Layers  : 2, 3, 4, 5")
    print("  Spacing : automatic combinations from 0.50% to 3.00%")
    print("  TP      : 0.50% to 2.00%")
    print("  Allocation: equal + deeper-layer weighted")
    print("  Costs   : maker/taker fee parameters + slippage")
    print()

    # IMPORTANT:
    # Keep these as parameters until the live Bitget fee endpoint
    # is successfully wired into the cost provider.
    maker_fee_rate = 0.0010
    taker_fee_rate = 0.0010

    result = optimize_flexible_grid(
        df=df,
        capitals=[15, 30, 50, 100, 250, 500],
        layer_counts=[2, 3, 4, 5],
        spacing_levels=[
            0.0050,
            0.0075,
            0.0100,
            0.0125,
            0.0150,
            0.0200,
            0.0250,
            0.0300,
        ],
        tp_percents=[
            0.0050,
            0.0060,
            0.0075,
            0.0100,
            0.0125,
            0.0150,
            0.0200,
        ],
        allocation_modes=["equal", "deeper"],
        deeper_growth=1.25,
        maker_fee_rate=maker_fee_rate,
        taker_fee_rate=taker_fee_rate,
        buy_slippage_rate=0.0,
        sell_slippage_rate=0.0,
        entry_fee_type="maker",
        exit_fee_type="maker",
        min_cycles=10,
        drawdown_penalty=1.0,
    )

    save_optimizer_result(result, OUTPUT)

    best = best_by_capital_and_layers(result)

    cols = [
        "capital",
        "layers",
        "allocation_mode",
        "layer_capital",
        "spacing",
        "tp_percent",
        "cycles",
        "win_rate",
        "fees",
        "net_profit",
        "profit_factor",
        "max_drawdown_pct",
        "max_capital_used",
        "avg_layers",
        "score",
    ]

    print("=" * 110)
    print("BEST CONFIGURATION PER CAPITAL × LAYERS")
    print("=" * 110)
    print(best[cols].to_string(index=False))

    print()
    print("=" * 110)
    print("TOP 20 OVERALL")
    print("=" * 110)
    print(result[cols].head(20).to_string(index=False))

    print()
    print(f"All results : {OUTPUT}")
    print(f"Total tests: {len(result):,}")
    print("=" * 110)


if __name__ == "__main__":
    main()
