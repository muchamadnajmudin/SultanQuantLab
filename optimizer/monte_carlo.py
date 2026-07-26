"""
==========================================
SULTAN QUANT OS
Monte Carlo Simulation Engine
Version : 3.3.0
==========================================

Responsibilities:

- Randomize trade sequence
- Simulate equity paths
- Measure robustness

Monte Carlo does NOT:
- create signals
- optimize parameters
- run backtest

"""

import random



# ==================================================
# EQUITY SIMULATION
# ==================================================

def simulate_equity(
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
# MAX DRAW DOWN
# ==================================================

def calculate_drawdown(
    equity: list[float],
):

    peak = equity[0]

    max_drawdown = 0


    for value in equity:


        if value > peak:

            peak = value


        drawdown = (
            peak - value
        )


        if drawdown > max_drawdown:

            max_drawdown = drawdown



    return max_drawdown



# ==================================================
# SINGLE SIMULATION
# ==================================================

def run_simulation(
    trades: list[float],
    initial_balance: float = 10000,
):


    shuffled = trades.copy()


    random.shuffle(
        shuffled
    )


    equity = simulate_equity(
        shuffled,
        initial_balance,
    )


    drawdown = calculate_drawdown(
        equity
    )


    return {

        "final_balance":
            equity[-1],

        "max_drawdown":
            drawdown,

        "equity":
            equity,

    }



# ==================================================
# MONTE CARLO ENGINE
# ==================================================

def run_monte_carlo(
    trades: list[float],
    simulations: int = 1000,
    initial_balance: float = 10000,
):


    results = []


    for _ in range(simulations):


        result = run_simulation(

            trades,

            initial_balance,

        )


        results.append(
            result
        )


    return results