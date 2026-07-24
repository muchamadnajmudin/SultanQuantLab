"""
==========================================
SULTAN QUANT OS
Visual Engine
Version : 2.3.1
==========================================
"""

from pathlib import Path

import matplotlib.pyplot as plt


# =====================================================
# CONFIG
# =====================================================

OUTPUT_DIR = Path("reports/output")


# =====================================================
# INTERNAL
# =====================================================

def _prepare_output():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# =====================================================
# EQUITY CURVE
# =====================================================

def save_equity_curve(stats: dict):

    equity = stats.get("equity_curve", [])

    if not equity:
        return

    plt.figure(figsize=(10, 5))

    plt.plot(equity)

    plt.title("Equity Curve")

    plt.xlabel("Trade")

    plt.ylabel("Balance")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "equity_curve.png",
        dpi=150,
    )

    plt.close()


# =====================================================
# DRAWDOWN
# =====================================================

def save_drawdown_chart(stats: dict):

    equity = stats.get("equity_curve", [])

    if not equity:
        return

    peak = []

    highest = equity[0]

    for value in equity:

        highest = max(highest, value)

        peak.append(highest)

    drawdown = []

    for current, high in zip(equity, peak):

        drawdown.append(current - high)

    plt.figure(figsize=(10, 5))

    plt.plot(drawdown)

    plt.title("Drawdown")

    plt.xlabel("Trade")

    plt.ylabel("Drawdown")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "drawdown.png",
        dpi=150,
    )

    plt.close()


# =====================================================
# PROFIT DISTRIBUTION
# =====================================================

def save_profit_distribution(trades):

    profits = [trade.profit for trade in trades]

    if len(profits) == 0:
        return

    plt.figure(figsize=(10, 5))

    plt.hist(profits, bins=20)

    plt.title("Profit Distribution")

    plt.xlabel("Profit")

    plt.ylabel("Frequency")

    plt.grid(True)

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "profit_distribution.png",
        dpi=150,
    )

    plt.close()


# =====================================================
# MONTHLY RETURNS
# =====================================================

def save_monthly_returns(trades):

    """
    Placeholder.

    Akan dibuat pada Sprint 2.3.2
    """

    return


# =====================================================
# MAIN VISUAL REPORT
# =====================================================

def generate_visual_reports(
    stats: dict,
    trades,
):

    _prepare_output()

    save_equity_curve(stats)

    save_drawdown_chart(stats)

    save_profit_distribution(trades)

    save_monthly_returns(trades)