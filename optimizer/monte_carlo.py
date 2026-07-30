"""
==========================================
SULTAN QUANT OS
Monte Carlo Simulation Engine
Version : 6.0.0
==========================================

Responsibilities:

- Randomize trade sequence
- Bootstrap trade sequence
- Simulate equity paths
- Measure robustness

Compatible with:

- list[Trade]
- list[float]

"""

import random


# ==================================================
# PROFIT EXTRACTION
# ==================================================

def _extract_profit(trade):

    if hasattr(trade, "profit"):

        return float(trade.profit)

    if isinstance(trade, dict):

        return float(

            trade.get(

                "profit",

                0,

            )

        )

    return float(trade)


# ==================================================
# NORMALIZE INPUT
# ==================================================

def normalize_trades(

    trades,

):

    return [

        _extract_profit(trade)

        for trade in trades

    ]


# ==================================================
# SHUFFLE
# ==================================================

def shuffle_trades(

    profits,

):

    shuffled = profits.copy()

    random.shuffle(

        shuffled

    )

    return shuffled


# ==================================================
# BOOTSTRAP
# ==================================================

def bootstrap_trades(

    profits,

):

    if not profits:

        return []

    return [

        random.choice(

            profits

        )

        for _ in range(

            len(profits)

        )

    ]


# ==================================================
# EQUITY CURVE
# ==================================================

def simulate_equity(

    profits,

    initial_balance=10000,

):

    balance = float(

        initial_balance

    )

    equity = [

        balance

    ]

    for profit in profits:

        balance += profit

        equity.append(

            balance

        )

    return equity

    # ==================================================
# MAX DRAWDOWN
# ==================================================

def calculate_drawdown(

    equity,

):

    if not equity:

        return 0.0

    peak = equity[0]

    max_drawdown = 0.0

    for value in equity:

        if value > peak:

            peak = value

        drawdown = peak - value

        if drawdown > max_drawdown:

            max_drawdown = drawdown

    return round(

        max_drawdown,

        2,

    )


# ==================================================
# INTERNAL RANDOMIZER
# ==================================================

def _randomize(

    profits,

    method="shuffle",

):

    if method == "bootstrap":

        return bootstrap_trades(

            profits

        )

    return shuffle_trades(

        profits

    )


# ==================================================
# SINGLE SIMULATION
# ==================================================

def run_simulation(

    trades,

    initial_balance=10000,

    method="shuffle",

):

    profits = normalize_trades(

        trades

    )

    randomized = _randomize(

        profits,

        method,

    )

    equity = simulate_equity(

        randomized,

        initial_balance,

    )

    drawdown = calculate_drawdown(

        equity

    )

    return {

        "final_balance":

            round(

                equity[-1],

                2,

            ),

        "max_drawdown":

            drawdown,

        "equity":

            equity,

        "trade_count":

            len(

                randomized

            ),

        "method":

            method,

    }

    # ==================================================
# MONTE CARLO
# ==================================================

def run_monte_carlo(

    trades,

    simulations=1000,

    initial_balance=10000,

):

    results = []

    for _ in range(

        simulations

    ):

        results.append(

            run_simulation(

                trades,

                initial_balance,

                method="shuffle",

            )

        )

    return results


# ==================================================
# BOOTSTRAP MONTE CARLO
# ==================================================

def run_bootstrap_monte_carlo(

    trades,

    simulations=1000,

    initial_balance=10000,

):

    results = []

    for _ in range(

        simulations

    ):

        results.append(

            run_simulation(

                trades,

                initial_balance,

                method="bootstrap",

            )

        )

    return results


# ==================================================
# SUMMARY
# ==================================================

def summarize_results(

    results,

):

    if not results:

        return {

            "simulation_count": 0,

            "average_balance": 0,

            "average_drawdown": 0,

        }

    balances = [

        item["final_balance"]

        for item in results

    ]

    drawdowns = [

        item["max_drawdown"]

        for item in results

    ]

    return {

        "simulation_count":

            len(results),

        "average_balance":

            round(

                sum(balances)

                / len(balances),

                2,

            ),

        "average_drawdown":

            round(

                sum(drawdowns)

                / len(drawdowns),

                2,

            ),

    }

    # ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    class DummyTrade:

        def __init__(self, profit):

            self.profit = profit

    trades = [

        DummyTrade(5),

        DummyTrade(-3),

        DummyTrade(8),

        DummyTrade(-1),

        DummyTrade(10),

        DummyTrade(-6),

    ]

    print("=" * 60)
    print("SULTAN QUANT OS")
    print("MONTE CARLO TEST")
    print("=" * 60)

    print()
    print("SHUFFLE MODE")

    shuffle_results = run_monte_carlo(

        trades,

        simulations=5,

    )

    for index, result in enumerate(

        shuffle_results,

        start=1,

    ):

        print(

            f"Simulation {index}"

        )

        print(

            f"  Method         : {result['method']}"

        )

        print(

            f"  Final Balance  : {result['final_balance']}"

        )

        print(

            f"  Max Drawdown   : {result['max_drawdown']}"

        )

        print()

    print("=" * 60)

    print()

    print("BOOTSTRAP MODE")

    bootstrap_results = run_bootstrap_monte_carlo(

        trades,

        simulations=5,

    )

    for index, result in enumerate(

        bootstrap_results,

        start=1,

    ):

        print(

            f"Simulation {index}"

        )

        print(

            f"  Method         : {result['method']}"

        )

        print(

            f"  Final Balance  : {result['final_balance']}"

        )

        print(

            f"  Max Drawdown   : {result['max_drawdown']}"

        )

        print()

    print("=" * 60)

    print("SUMMARY")
    print("=" * 60)

    summary = summarize_results(

        shuffle_results,

    )

    for key, value in summary.items():

        print(

            f"{key:20}: {value}"

        )