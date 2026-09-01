"""
==========================================
SULTAN QUANT OS
Monte Carlo Simulation Engine
Version : 6.2.0
==========================================

Responsibilities:

- Randomize trade sequence
- Bootstrap trade sequence
- Simulate equity paths
- Measure sequence risk
- Measure distribution robustness
- Reproducible simulation with seed
- Support institutional Monte Carlo workflows

Compatible with:

- list[Trade]
- list[float]
- list[dict]
- Previous run_monte_carlo()

Backward Compatible:
- Existing function names preserved
- Existing parameter counts preserved
- Existing parameter order preserved
- Existing return keys preserved
- Existing shuffle behavior preserved
- Existing bootstrap behavior preserved

Simulation Methods:

- shuffle
    Randomizes the order of the historical trades.
    The trade composition remains unchanged.

- bootstrap
    Resamples historical trades with replacement.
    The trade composition can therefore vary between
    simulations.

Important:

Shuffle is useful for sequence/path risk.

Bootstrap is useful for distribution/robustness risk.

The default method remains "shuffle" to preserve
backward compatibility.
"""

import random


# ==================================================
# CONSTANTS
# ==================================================

DEFAULT_SIMULATIONS = 1000
DEFAULT_INITIAL_BALANCE = 10000.0
DEFAULT_METHOD = "shuffle"

SUPPORTED_METHODS = (
    "shuffle",
    "bootstrap",
)

MAX_SEED = 999999999


# ==================================================
# PROFIT EXTRACTION
# ==================================================

def _extract_profit(trade):
    """
    Extract profit from supported trade representations.

    Supported:

    1. Trade-like object
       trade.profit

    2. Dictionary
       {"profit": value}

    3. Numeric value
       10
       -5
       2.5
    """

    if hasattr(trade, "profit"):

        return float(
            trade.profit
        )

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
    """
    Normalize trade history into a list of profits.

    Input is not modified.
    """

    if trades is None:

        return []

    return [
        _extract_profit(trade)
        for trade in trades
    ]


# ==================================================
# RANDOM GENERATOR
# ==================================================

def _create_rng(
    seed=None,
):
    """
    Create an isolated random generator.

    Using random.Random instead of the global random
    generator guarantees that Monte Carlo simulations
    do not modify global random state.
    """

    return random.Random(
        seed
    )


# ==================================================
# METHOD VALIDATION
# ==================================================

def _normalize_method(
    method,
):
    """
    Normalize Monte Carlo method.

    Supported methods:

        shuffle
        bootstrap

    For backward compatibility, unknown or invalid
    methods fall back to shuffle, matching the previous
    implementation behavior.
    """

    if not isinstance(
        method,
        str,
    ):

        return DEFAULT_METHOD

    normalized = method.strip().lower()

    if normalized in SUPPORTED_METHODS:

        return normalized

    return DEFAULT_METHOD


# ==================================================
# SHUFFLE
# ==================================================

def shuffle_trades(
    profits,
    rng=None,
):
    """
    Randomize trade order without changing trade
    composition.

    Example:

        [10, -5, 20]

    may become:

        [20, 10, -5]

    but all original trades remain present.
    """

    if rng is None:

        rng = _create_rng()

    shuffled = list(
        profits
    )

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
    """
    Bootstrap historical trades with replacement.

    The resulting sequence has the same length as the
    original trade history but individual trades may
    appear multiple times or not appear at all.

    This produces variation in final balance and is
    therefore useful for distribution robustness.
    """

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
    initial_balance=DEFAULT_INITIAL_BALANCE,
):
    """
    Simulate account equity from a sequence of profits.

    The returned equity curve always contains the
    initial balance as its first element.
    """

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
    """
    Calculate maximum absolute drawdown.

    Drawdown is measured from the highest historical
    equity point to a subsequent equity point.

    Returns:
        Absolute maximum drawdown.
    """

    if not equity:

        return 0.0

    peak = equity[0]

    max_drawdown = 0.0

    for value in equity:

        if value > peak:

            peak = value

        drawdown = (
            peak - value
        )

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
    method=DEFAULT_METHOD,
    rng=None,
):
    """
    Randomize a normalized profit sequence.

    Supported:

        shuffle
        bootstrap

    Unknown methods preserve the historical fallback
    behavior and use shuffle.
    """

    normalized_method = _normalize_method(
        method
    )

    if normalized_method == "bootstrap":

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
    initial_balance=DEFAULT_INITIAL_BALANCE,
    method=DEFAULT_METHOD,
    seed=None,
):
    """
    Execute one Monte Carlo simulation.

    Parameters
    ----------
    trades:
        Trade history, numeric profits, or dictionaries.

    initial_balance:
        Starting account balance.

    method:
        "shuffle" or "bootstrap".

    seed:
        Optional deterministic seed.

    Returns
    -------
    dict
        Existing return keys are preserved:

        - final_balance
        - max_drawdown
        - equity
        - trade_count
        - method

        Additional metadata:

        - seed
    """

    rng = _create_rng(
        seed
    )

    profits = normalize_trades(
        trades
    )

    normalized_method = _normalize_method(
        method
    )

    randomized = _randomize(
        profits,
        normalized_method,
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
        "final_balance": round(
            equity[-1],
            2,
        ),

        "max_drawdown": drawdown,

        "equity": equity,

        "trade_count": len(
            randomized
        ),

        "method": normalized_method,

        "seed": seed,
    }


# ==================================================
# MONTE CARLO
# ==================================================

def run_monte_carlo(
    trades,
    simulations=DEFAULT_SIMULATIONS,
    initial_balance=DEFAULT_INITIAL_BALANCE,
    method=DEFAULT_METHOD,
    seed=None,
):
    """
    Execute Monte Carlo simulations.

    The public signature is intentionally preserved.

    For shuffle:

        Every simulation contains exactly the same
        historical trades, but in a different order.

    For bootstrap:

        Every simulation samples the historical trades
        with replacement.

    Seed behavior:

        A master RNG is created from seed.

        Each simulation receives its own deterministic
        child seed.

    Therefore:

        same input + same seed
            ->
        identical simulation results

    while:

        different seed
            ->
        different simulation results.
    """

    # --------------------------------------------------
    # Normalize simulation count
    # --------------------------------------------------

    try:

        simulation_count = int(
            simulations
        )

    except (
        TypeError,
        ValueError,
    ):

        simulation_count = DEFAULT_SIMULATIONS

    if simulation_count < 0:

        simulation_count = 0

    # --------------------------------------------------
    # Normalize method
    # --------------------------------------------------

    normalized_method = _normalize_method(
        method
    )

    # --------------------------------------------------
    # Master random generator
    # --------------------------------------------------

    rng = _create_rng(
        seed
    )

    results = []

    # --------------------------------------------------
    # Execute simulations
    # --------------------------------------------------

    for simulation_id in range(
        simulation_count
    ):

        simulation_seed = rng.randint(
            0,
            MAX_SEED,
        )

        result = run_simulation(
            trades,
            initial_balance,
            normalized_method,
            simulation_seed,
        )

        # --------------------------------------------------
        # Additional metadata.
        #
        # These keys do not replace or modify any existing
        # return keys.
        # --------------------------------------------------

        result["simulation_id"] = (
            simulation_id + 1
        )

        results.append(
            result
        )

    return results


# ==================================================
# BOOTSTRAP MONTE CARLO
# ==================================================

def run_bootstrap_monte_carlo(
    trades,
    simulations=DEFAULT_SIMULATIONS,
    initial_balance=DEFAULT_INITIAL_BALANCE,
    seed=None,
):
    """
    Convenience wrapper for bootstrap Monte Carlo.

    Public contract is preserved.
    """

    return run_monte_carlo(
        trades,
        simulations,
        initial_balance,
        method="bootstrap",
        seed=seed,
    )


# ==================================================
# SHUFFLE MONTE CARLO
# ==================================================

def run_shuffle_monte_carlo(
    trades,
    simulations=DEFAULT_SIMULATIONS,
    initial_balance=DEFAULT_INITIAL_BALANCE,
    seed=None,
):
    """
    Convenience wrapper for sequence-risk Monte Carlo.

    This is equivalent to:

        run_monte_carlo(
            trades,
            simulations,
            initial_balance,
            method="shuffle",
            seed=seed,
        )
    """

    return run_monte_carlo(
        trades,
        simulations,
        initial_balance,
        method="shuffle",
        seed=seed,
    )


# ==================================================
# SUMMARY
# ==================================================

def summarize_results(
    results,
):
    """
    Summarize Monte Carlo simulation results.

    Existing summary keys are preserved.
    """

    if not results:

        return {
            "simulation_count": 0,
            "average_balance": 0,
            "average_drawdown": 0,
            "best_balance": 0,
            "worst_balance": 0,
            "worst_drawdown": 0,
            "equity_paths": 0,
        }

    balances = [
        item["final_balance"]
        for item in results
        if isinstance(
            item,
            dict,
        )
        and "final_balance" in item
    ]

    drawdowns = [
        item["max_drawdown"]
        for item in results
        if isinstance(
            item,
            dict,
        )
        and "max_drawdown" in item
    ]

    equity_paths = [
        item["equity"]
        for item in results
        if isinstance(
            item,
            dict,
        )
        and "equity" in item
    ]

    if not balances:

        return {
            "simulation_count": len(
                results
            ),
            "average_balance": 0,
            "average_drawdown": 0,
            "best_balance": 0,
            "worst_balance": 0,
            "worst_drawdown": 0,
            "equity_paths": len(
                equity_paths
            ),
        }

    average_balance = (
        sum(balances)
        /
        len(balances)
    )

    average_drawdown = (
        sum(drawdowns)
        /
        len(drawdowns)
        if drawdowns
        else 0
    )

    return {
        "simulation_count": len(
            results
        ),

        "average_balance": round(
            average_balance,
            2,
        ),

        "average_drawdown": round(
            average_drawdown,
            2,
        ),

        "best_balance": round(
            max(balances),
            2,
        ),

        "worst_balance": round(
            min(balances),
            2,
        ),

        "worst_drawdown": round(
            max(drawdowns),
            2,
        )
        if drawdowns
        else 0,

        "equity_paths": len(
            equity_paths
        ),
    }


# ==================================================
# TEST / MANUAL EXECUTION
# ==================================================

if __name__ == "__main__":

    class DummyTrade:

        def __init__(
            self,
            profit,
        ):

            self.profit = profit

    trades = [
        DummyTrade(5),
        DummyTrade(-3),
        DummyTrade(8),
        DummyTrade(-1),
        DummyTrade(10),
        DummyTrade(-6),
    ]

    print(
        "=" * 60
    )

    print(
        "SULTAN QUANT OS"
    )

    print(
        "MONTE CARLO ENGINE 6.2"
    )

    print(
        "=" * 60
    )

    # ==================================================
    # SHUFFLE
    # ==================================================

    print()

    print(
        "SHUFFLE MODE"
    )

    shuffle_results = run_monte_carlo(
        trades,
        simulations=5,
        seed=42,
        method="shuffle",
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
            f" Seed          : {result['seed']}"
        )

        print(
            f" Balance       : {result['final_balance']}"
        )

        print(
            f" Drawdown      : {result['max_drawdown']}"
        )

    # ==================================================
    # BOOTSTRAP
    # ==================================================

    print()

    print(
        "=" * 60
    )

    print(
        "BOOTSTRAP MODE"
    )

    bootstrap_results = run_bootstrap_monte_carlo(
        trades,
        simulations=5,
        seed=42,
    )

    for index, result in enumerate(
        bootstrap_results,
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
            f" Seed          : {result['seed']}"
        )

        print(
            f" Balance       : {result['final_balance']}"
        )

        print(
            f" Drawdown      : {result['max_drawdown']}"
        )

    # ==================================================
    # SUMMARY
    # ==================================================

    print()

    print(
        "=" * 60
    )

    print(
        "SHUFFLE SUMMARY"
    )

    print(
        "=" * 60
    )

    shuffle_summary = summarize_results(
        shuffle_results
    )

    for key, value in shuffle_summary.items():

        print(
            f"{key:25}: {value}"
        )

    print()

    print(
        "=" * 60
    )

    print(
        "BOOTSTRAP SUMMARY"
    )

    print(
        "=" * 60
    )

    bootstrap_summary = summarize_results(
        bootstrap_results
    )

    for key, value in bootstrap_summary.items():

        print(
            f"{key:25}: {value}"
        )

    print()

    print(
        "MONTE CARLO ENGINE COMPLETE"
    )