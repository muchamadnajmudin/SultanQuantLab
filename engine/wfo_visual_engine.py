"""
==========================================
SULTAN QUANT OS
WFO Visual Engine
Version : 5.1.0
==========================================

Responsibilities:

- Generate WFO equity visualization
- Generate parameter stability chart
- Create research graphics

"""

from pathlib import Path
from collections import Counter

import matplotlib.pyplot as plt



# ==================================================
# CONFIG
# ==================================================

OUTPUT_DIR = Path(
    "reports/output"
)



# ==================================================
# PREPARE
# ==================================================

def _prepare_output():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )



# ==================================================
# WFO EQUITY CURVE
# ==================================================

def save_wfo_equity_curve(
    results:list[dict],
):


    _prepare_output()


    equity = []

    balance = 0



    for item in results:


        validation = item.get(
            "validation",
            {}
        )


        profit = validation.get(
            "net_profit",
            0
        )


        balance += profit

        equity.append(
            balance
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
        "WFO Equity Curve"
    )


    plt.xlabel(
        "Window"
    )


    plt.ylabel(
        "Cumulative Profit"
    )


    plt.grid(
        True
    )


    plt.tight_layout()



    file_path = (

        OUTPUT_DIR /
        "wfo_equity_curve.png"

    )



    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# ==================================================
# PARAMETER STABILITY
# ==================================================

def save_parameter_stability_chart(
    results:list[dict],
):


    _prepare_output()



    parameters = []



    for item in results:


        parameter = item.get(
            "best_parameter",
            {}
        )


        key = (

            str(
                parameter.get(
                    "RSI_OVERSOLD",
                    0
                )
            )
            +
            "/"
            +
            str(
                parameter.get(
                    "RSI_OVERBOUGHT",
                    0
                )
            )

        )


        parameters.append(
            key
        )



    if not parameters:

        return None



    counter = Counter(
        parameters
    )



    labels = list(
        counter.keys()
    )


    values = list(
        counter.values()
    )



    plt.figure(
        figsize=(10,5)
    )


    plt.bar(
        labels,
        values
    )


    plt.title(
        "WFO Parameter Stability"
    )


    plt.xlabel(
        "Parameter"
    )


    plt.ylabel(
        "Frequency"
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
        "wfo_parameter_stability.png"

    )



    plt.savefig(
        file_path,
        dpi=150
    )


    plt.close()



    return file_path



# ==================================================
# MAIN
# ==================================================

def generate_wfo_visual_reports(
    results:list[dict],
):


    files = []


    equity = save_wfo_equity_curve(
        results
    )


    if equity:

        files.append(
            equity
        )



    stability = save_parameter_stability_chart(
        results
    )


    if stability:

        files.append(
            stability
        )



    return files