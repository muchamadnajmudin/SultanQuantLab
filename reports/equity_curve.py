"""
==========================================
SULTAN QUANT OS
Equity Curve Engine
Version : 4.1.0
==========================================

Responsibilities:

- Generate equity curve data
- Calculate balance progression

"""



# ==================================================
# BUILD EQUITY CURVE
# ==================================================

def build_equity_curve(
    trades: list[float],
    initial_balance: float = 10000,
):


    balance = initial_balance


    equity = [

        balance

    ]



    for profit in trades:


        balance += profit


        equity.append(

            balance

        )



    return equity



# ==================================================
# FINAL BALANCE
# ==================================================

def get_final_balance(
    equity: list[float],
):


    if not equity:

        return 0



    return equity[-1]