"""
==========================================
SULTAN QUANT OS
Monte Carlo Simulation Engine
Version : 6.1.0
==========================================

Responsibilities:

- Randomize trade sequence
- Bootstrap trade sequence
- Simulate equity paths
- Measure robustness
- Reproducible simulation with seed

Compatible with:

- list[Trade]
- list[float]
- Previous run_monte_carlo()

Backward Compatible:
- Existing function names preserved
- Existing return keys preserved

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
# RANDOM GENERATOR
# ==================================================

def _create_rng(seed=None):

    return random.Random(

        seed

    )



# ==================================================
# SHUFFLE
# ==================================================

def shuffle_trades(

    profits,

    rng=None,

):

    if rng is None:

        rng = _create_rng()


    shuffled = profits.copy()


    rng.shuffle(

        shuffled

    )


    return shuffled



# ==================================================
# BOOTSTRAP
# ==================================================

def bootstrap_trades(

    profits,

    rng=None,

):

    if not profits:

        return []


    if rng is None:

        rng = _create_rng()



    return [

        rng.choice(

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


        balance += float(

            profit

        )


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

    rng=None,

):

    if method == "bootstrap":

        return bootstrap_trades(

            profits,

            rng,

        )


    return shuffle_trades(

        profits,

        rng,

    )



# ==================================================
# SINGLE SIMULATION
# ==================================================

def run_simulation(

    trades,

    initial_balance=10000,

    method="shuffle",

    seed=None,

):


    rng = _create_rng(

        seed

    )


    profits = normalize_trades(

        trades

    )


    randomized = _randomize(

        profits,

        method,

        rng,

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

    method="shuffle",

    seed=None,

):

    results = []


    rng = _create_rng(

        seed

    )



    for _ in range(

        simulations

    ):


        simulation_seed = rng.randint(

            0,

            999999999,

        )



        results.append(

            run_simulation(

                trades,

                initial_balance,

                method,

                simulation_seed,

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

    seed=None,

):


    return run_monte_carlo(

        trades,

        simulations,

        initial_balance,

        method="bootstrap",

        seed=seed,

    )



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


            "best_balance": 0,


            "worst_balance": 0,


            "worst_drawdown": 0,


        }



    balances = [


        item["final_balance"]


        for item in results


    ]



    drawdowns = [


        item["max_drawdown"]


        for item in results


    ]



    equity_paths = [


        item["equity"]


        for item in results


        if "equity" in item


    ]



    return {


        "simulation_count":


            len(results),



        "average_balance":


            round(


                sum(balances)

                /

                len(balances),


                2,


            ),



        "average_drawdown":


            round(


                sum(drawdowns)

                /

                len(drawdowns),


                2,


            ),



        "best_balance":


            round(


                max(balances),


                2,


            ),



        "worst_balance":


            round(


                min(balances),


                2,


            ),



        "worst_drawdown":


            round(


                max(drawdowns),


                2,


            ),



        "equity_paths":


            len(equity_paths),



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

    print("MONTE CARLO ENGINE 6.1")

    print("=" * 60)



    print()


    print("SHUFFLE MODE")


    shuffle_results = run_monte_carlo(

        trades,

        simulations=5,

        seed=42,

    )



    for index, result in enumerate(


        shuffle_results,


        start=1,


    ):


        print()


        print(

            f"Simulation {index}"

        )


        print(

            f" Method        : {result['method']}"

        )


        print(

            f" Balance       : {result['final_balance']}"

        )


        print(

            f" Drawdown      : {result['max_drawdown']}"

        )



    print()

    print("=" * 60)

    print("SUMMARY")

    print("=" * 60)



    summary = summarize_results(

        shuffle_results

    )



    for key, value in summary.items():


        print(

            f"{key:25}: {value}"

        )