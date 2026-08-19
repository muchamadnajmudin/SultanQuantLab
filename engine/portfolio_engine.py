"""
==========================================
SULTAN QUANT OS
Institutional Portfolio Engine
Version : 4.2.0
==========================================

Responsibilities:

- Detect Market Regime
- Load All Registered Strategies
- Execute Strategy Evaluation
- Calculate Strategy Statistics
- Rank Strategies
- Update Strategy Memory
- Build Portfolio Candidates
- Portfolio Summary
- Portfolio Filtering
- Portfolio Allocation
- Portfolio Risk
- Return Portfolio Results

Architecture:

Strategy Registry
        ↓
All Strategy Evaluation
        ↓
Backtest
        ↓
Statistics
        ↓
Strategy Ranking
        ↓
Strategy Memory
        ↓
Portfolio Results

IMPORTANT:

The Portfolio Engine evaluates ALL strategies registered
in strategies.registry by default.

Market regime and router information are preserved as
metadata and are NOT allowed to silently remove registered
strategies from institutional evaluation.
"""

from copy import deepcopy


# ==================================================
# STRATEGY REGISTRY
# ==================================================

from strategies.registry import (
    list_strategies,
)


# ==================================================
# STRATEGY ENGINE
# ==================================================

from engine.strategy_engine import (
    run_strategy,
)


# ==================================================
# BACKTEST ENGINE
# ==================================================

from engine.backtest_engine import (
    run_backtest,
)


# ==================================================
# STATISTICS ENGINE
# ==================================================

from engine.statistics_engine import (
    calculate_statistics,
)


# ==================================================
# STRATEGY RANKER
# ==================================================

from strategies.intelligence.strategy_ranker import (
    rank_strategies,
)


# ==================================================
# MARKET REGIME
# ==================================================

from strategies.regime.market_regime import (
    detect_market_regime,
)


# ==================================================
# STRATEGY ROUTER
# ==================================================

from strategies.router.strategy_router import (
    recommended_strategy,
)


# ==================================================
# STRATEGY MEMORY
# ==================================================

from strategies.intelligence.strategy_memory import (
    update_memory,
)


# ==================================================
# STRATEGY WEIGHT
# ==================================================

from strategies.intelligence.strategy_weight import (
    calculate_weight,
)


# ==================================================
# DEFAULT ALLOCATION
# ==================================================

from strategies.allocation import (
    default_allocation,
)


# ==================================================
# PORTFOLIO RISK
# ==================================================

from risk.portfolio_risk import (
    calculate_portfolio_risk,
)


# ==================================================
# RUN PORTFOLIO
# ==================================================

def run_portfolio(df):

    """
    Execute institutional evaluation for ALL registered
    strategies.

    Parameters
    ----------
    df : pandas.DataFrame
        Market OHLCV data.

    Returns
    -------
    list
        Ranked strategy results.
    """

    results = []

    # ==================================================
    # MARKET REGIME
    # ==================================================

    if len(df):

        regime = detect_market_regime(
            df.iloc[-1]
        )

        router_strategy = recommended_strategy(
            df.iloc[-1]
        )

    else:

        regime = "UNKNOWN"

        router_strategy = None

    # ==================================================
    # LOAD ALL REGISTERED STRATEGIES
    # ==================================================

    registered_strategies = list_strategies()

    # --------------------------------------------------
    # Safety: remove duplicates while preserving order
    # --------------------------------------------------

    selected = list(
        dict.fromkeys(
            registered_strategies
        )
    )

    # ==================================================
    # FALLBACK
    # ==================================================

    if not selected:

        return []

    # ==================================================
    # EXECUTE EVERY REGISTERED STRATEGY
    # ==================================================

    for strategy in selected:

        try:

            # ------------------------------------------
            # Isolate DataFrame
            # ------------------------------------------

            strategy_df = deepcopy(
                df
            )

            # ------------------------------------------
            # Execute Strategy
            # ------------------------------------------

            strategy_df = run_strategy(
                strategy_df,
                strategy=strategy,
            )

            # ------------------------------------------
            # Backtest
            # ------------------------------------------

            trades = run_backtest(
                strategy_df
            )

            # ------------------------------------------
            # Statistics
            # ------------------------------------------

            statistics = calculate_statistics(
                trades
            )

            # ------------------------------------------
            # Strategy Weight
            # ------------------------------------------

            weight = calculate_weight(
                statistics
            )

            # ------------------------------------------
            # Router Flag
            # ------------------------------------------

            is_router_strategy = (
                strategy == router_strategy
            )

            # ------------------------------------------
            # Result
            # ------------------------------------------

            results.append(
                {

                    "name":
                        strategy,

                    "market_regime":
                        regime,

                    "statistics":
                        statistics,

                    "trades":
                        trades,

                    "weight":
                        weight,

                    "score":
                        0,

                    "rank":
                        0,

                    "router_recommended":
                        is_router_strategy,

                    "evaluation_status":
                        "SUCCESS",

                }
            )

        except Exception as exc:

            # --------------------------------------------------
            # One broken strategy must NOT crash the entire
            # institutional portfolio evaluation.
            #
            # It is recorded as FAILED and the other strategies
            # continue to be evaluated.
            # --------------------------------------------------

            results.append(
                {

                    "name":
                        strategy,

                    "market_regime":
                        regime,

                    "statistics":
                        {},

                    "trades":
                        [],

                    "weight":
                        0,

                    "score":
                        0,

                    "rank":
                        0,

                    "router_recommended":
                        strategy == router_strategy,

                    "evaluation_status":
                        "FAILED",

                    "error":
                        str(exc),

                }
            )

    # ==================================================
    # SEPARATE SUCCESSFUL STRATEGIES
    # ==================================================

    successful_results = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == "SUCCESS"

    ]

    failed_results = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == "FAILED"

    ]

    # ==================================================
    # RANK SUCCESSFUL STRATEGIES
    # ==================================================

    if successful_results:

        successful_results = rank_strategies(
            successful_results
        )

    # ==================================================
    # ASSIGN RANKS
    # ==================================================

    for index, item in enumerate(
        successful_results,
        start=1,
    ):

        item["rank"] = index

    # ==================================================
    # FAILED STRATEGIES
    # ==================================================

    for item in failed_results:

        item["rank"] = 0

    # ==================================================
    # FINAL RESULT
    # ==================================================

    results = (
        successful_results
        +
        failed_results
    )

    # ==================================================
    # UPDATE STRATEGY MEMORY
    # ==================================================

    for item in successful_results:

        update_memory(
            item["name"],
            item["statistics"],
        )

    # ==================================================
    # RETURN
    # ==================================================

    return results


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_strategy(results):

    """
    Return the highest ranked successful strategy.
    """

    if not results:

        return None

    for item in results:

        if item.get(
            "evaluation_status"
        ) == "SUCCESS":

            return item

    return None


# ==================================================
# PORTFOLIO SUMMARY
# ==================================================

def portfolio_summary(results):

    """
    Generate a compact portfolio summary.
    """

    if not results:

        return {

            "total": 0,

            "best": None,

        }

    successful = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == "SUCCESS"

    ]

    if not successful:

        return {

            "total":
                0,

            "evaluated":
                len(results),

            "best":
                None,

        }

    best = successful[0]

    return {

        "total":
            len(successful),

        "evaluated":
            len(results),

        "failed":
            len(results)
            -
            len(successful),

        "best":
            best["name"],

        "profit_factor":
            best["statistics"].get(
                "profit_factor",
                0,
            ),

        "win_rate":
            best["statistics"].get(
                "win_rate",
                0,
            ),

        "market_regime":
            best.get(
                "market_regime",
                "UNKNOWN",
            ),

    }


# ==================================================
# FILTER PROFITABLE
# ==================================================

def profitable_strategies(
    results,
    minimum_pf=1.2,
):

    """
    Return strategies whose Profit Factor is at
    or above the requested threshold.
    """

    return [

        r

        for r in results

        if r.get(
            "evaluation_status"
        ) == "SUCCESS"

        and r["statistics"].get(
            "profit_factor",
            0,
        ) >= minimum_pf

    ]


# ==================================================
# TOP N
# ==================================================

def top_strategies(
    results,
    n=3,
):

    """
    Return top N ranked successful strategies.
    """

    successful = [

        r

        for r in results

        if r.get(
            "evaluation_status"
        ) == "SUCCESS"

    ]

    return successful[:n]


# ==================================================
# QUALIFIED STRATEGIES
# ==================================================

def qualified_strategies(
    results,
    minimum_pf=1.2,
):

    """
    Alias for institutional portfolio filtering.

    This keeps filtering logic explicit for later
    portfolio construction stages.
    """

    return profitable_strategies(
        results,
        minimum_pf=minimum_pf,
    )

# ==================================================
# BUILD PORTFOLIO
# ==================================================

def build_portfolio(
    data,
):
    """
    Build institutional portfolio.

    Backward compatibility:

    1. Legacy mode
       build_portfolio("TRENDING")

       Uses default allocation based on market regime.

    2. Portfolio mode
       build_portfolio(strategy_results)

       Uses dynamic allocation based on ranked
       strategy results.
    """

    # ==================================================
    # LEGACY REGIME MODE
    # ==================================================

    if isinstance(
        data,
        str,
    ):

        regime = data

        allocation = default_allocation(
            regime,
        )

        risk = calculate_portfolio_risk(
            allocation,
        )

        return {

            "regime":
                regime,

            "allocation":
                allocation,

            "risk":
                risk,

        }

    # ==================================================
    # STRATEGY RESULTS MODE
    # ==================================================

    results = data

    if results is None:

        results = []

    if not isinstance(
        results,
        list,
    ):

        raise TypeError(
            "build_portfolio() expects "
            "a market regime string or "
            "a list of strategy results."
        )

    from engine.allocation_engine import (
        build_allocation,
    )

    allocation = build_allocation(
        results,
    )

    risk = calculate_portfolio_risk(
        allocation,
    )

    return {

        "allocation":
            allocation,

        "risk":
            risk,

    }
