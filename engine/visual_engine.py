"""
==========================================
SULTAN QUANT OS
Module : Visual Engine
Version : 2.3.2
==========================================
"""

from pathlib import Path
from collections import defaultdict

import matplotlib.pyplot as plt



# =====================================================
# CONFIG
# =====================================================

OUTPUT_DIR = Path(
    "reports/output"
)



# =====================================================
# PREPARE OUTPUT
# =====================================================

def _prepare_output():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )



# =====================================================
# EQUITY CURVE
# =====================================================

def save_equity_curve(stats: dict):


    equity = stats.get(
        "equity_curve",
        []
    )


    if not equity:

        return None



    plt.figure(
        figsize=(10,5)
    )


    plt.plot(
        equity
    )


    plt.title(
        "Equity Curve"
    )


    plt.xlabel(
        "Trade"
    )


    plt.ylabel(
        "Balance"
    )


    plt.grid(
        True
    )


    plt.tight_layout()



    file_path = (
        OUTPUT_DIR /
        "equity_curve.png"
    )


    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# =====================================================
# DRAWDOWN
# =====================================================

def save_drawdown_chart(stats: dict):


    drawdown = stats.get(
        "drawdown_curve",
        []
    )


    if not drawdown:

        return None



    plt.figure(
        figsize=(10,5)
    )


    plt.plot(
        drawdown
    )


    plt.title(
        "Drawdown"
    )


    plt.xlabel(
        "Trade"
    )


    plt.ylabel(
        "Drawdown"
    )


    plt.grid(
        True
    )


    plt.tight_layout()



    file_path = (
        OUTPUT_DIR /
        "drawdown.png"
    )


    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# =====================================================
# PROFIT DISTRIBUTION
# =====================================================

def save_profit_distribution(trades):


    profits = [

        float(trade.profit)

        for trade in trades

    ]


    if not profits:

        return None



    plt.figure(
        figsize=(10,5)
    )


    plt.hist(
        profits,
        bins=20
    )


    plt.title(
        "Profit Distribution"
    )


    plt.xlabel(
        "Profit"
    )


    plt.ylabel(
        "Frequency"
    )


    plt.grid(
        True
    )


    plt.tight_layout()



    file_path = (
        OUTPUT_DIR /
        "profit_distribution.png"
    )


    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# =====================================================
# MONTHLY RETURNS
# =====================================================

def save_monthly_returns(trades):


    monthly = defaultdict(float)



    for trade in trades:


        if trade.exit_time:

            key = (
                trade.exit_time
                .strftime("%Y-%m")
            )


            monthly[key] += float(
                trade.profit
            )



    if not monthly:

        return None



    months = list(
        monthly.keys()
    )


    values = list(
        monthly.values()
    )



    plt.figure(
        figsize=(10,5)
    )


    plt.bar(
        months,
        values
    )


    plt.title(
        "Monthly Returns"
    )


    plt.xlabel(
        "Month"
    )


    plt.ylabel(
        "Profit"
    )


    plt.xticks(
        rotation=45
    )


    plt.grid(
        True
    )


    plt.tight_layout()



    file_path = (
        OUTPUT_DIR /
        "monthly_returns.png"
    )


    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# =====================================================
# MAIN VISUAL REPORT
# =====================================================

def generate_visual_reports(
    stats: dict,
    trades
):


    _prepare_output()



    files = []


    for result in [

        save_equity_curve(stats),

        save_drawdown_chart(stats),

        save_profit_distribution(trades),

        save_monthly_returns(trades),

    ]:


        if result:

            files.append(
                result
            )



    return files