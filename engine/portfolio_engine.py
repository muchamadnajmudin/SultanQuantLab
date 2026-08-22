"""
==========================================
SULTAN QUANT OS
Portfolio Engine
Version : 3.3.1
==========================================

Responsibilities:

- Execute all registered strategies
- Detect market regime
- Normalize regime vocabulary
- Route recommended strategy
- Run strategy backtests
- Calculate strategy statistics
- Rank successful strategies
- Update regime-specific strategy memory
- Provide legacy portfolio operations
- Preserve backward compatibility

IMPORTANT:

Institutional portfolio orchestration is owned by:

    engine.institutional_portfolio_engine

This module remains responsible for strategy
evaluation and legacy portfolio operations.
"""

from copy import deepcopy


# ==================================================
# MARKET REGIME
# ==================================================

from engine.market_regime import (
    detect_regime,
    strategy_bias,
)


# ==================================================
# STRATEGY REGISTRY
# ==================================================

from strategies.registry import (
    list_strategies,
)


# ==================================================
# STRATEGY EXECUTION
# ==================================================

from engine.strategy_engine import (
    run_strategy,
)


# ==================================================
# BACKTEST
# ==================================================

from engine.backtest_engine import (
    run_backtest,
)


# ==================================================
# STATISTICS
# ==================================================

from engine.statistics_engine import (
    calculate_statistics,
)


# ==================================================
# STRATEGY RANKING
# ==================================================

from strategies.intelligence.strategy_ranker import (
    rank_strategies,
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
# REGIME NORMALIZATION
# ==================================================

def _normalize_market_regime(
    regime,
):

    """
    Normalize market regime vocabulary.

    The project currently contains two compatible
    regime vocabularies.

    Legacy regime engine:

        TRENDING
        RANGING
        HIGH_VOLATILITY

    Institutional market analyzer:

        STRONG_TREND
        TRENDING
        RANGE
        VOLATILE
        TRANSITION

    This helper converts alternative regime names into
    the legacy vocabulary expected by:

        - strategy_bias()
        - default_allocation()
        - existing strategy memory
        - existing portfolio callers

    Public function contracts are not changed.
    """

    if regime is None:

        return "UNKNOWN"

    normalized = str(
        regime
    ).strip().upper()

    aliases = {

        # ----------------------------------------------
        # TRENDING
        # ----------------------------------------------

        "TRENDING":
            "TRENDING",

        "STRONG_TREND":
            "TRENDING",

        "UPTREND":
            "TRENDING",

        "DOWNTREND":
            "TRENDING",


        # ----------------------------------------------
        # RANGING
        # ----------------------------------------------

        "RANGING":
            "RANGING",

        "RANGE":
            "RANGING",

        "QUIET_RANGE":
            "RANGING",

        "SIDEWAYS":
            "RANGING",


        # ----------------------------------------------
        # HIGH VOLATILITY
        # ----------------------------------------------

        "HIGH_VOLATILITY":
            "HIGH_VOLATILITY",

        "VOLATILE":
            "HIGH_VOLATILITY",


        # ----------------------------------------------
        # UNKNOWN / TRANSITION
        # ----------------------------------------------

        "TRANSITION":
            "UNKNOWN",

        "UNCLEAR":
            "UNKNOWN",

        "UNKNOWN":
            "UNKNOWN",

    }

    return aliases.get(
        normalized,
        normalized,
    )


# ==================================================
# MARKET REGIME HELPER
# ==================================================

def _detect_market_regime(
    df,
):

    """
    Detect market regime from the latest market row.

    This helper adapts the existing market_regime.py
    interface to the portfolio engine.

    The portfolio engine does not modify the market
    regime implementation and does not depend on
    exchange-specific APIs.
    """

    if df is None:

        return "UNKNOWN"

    if len(
        df
    ) == 0:

        return "UNKNOWN"

    try:

        regime = detect_regime(
            df.iloc[-1]
        )

        return _normalize_market_regime(
            regime
        )

    except Exception:

        return "UNKNOWN"


# ==================================================
# RECOMMENDED STRATEGY HELPER
# ==================================================

def _recommended_strategy(
    df,
    regime,
):

    """
    Determine the preferred strategy for the
    detected market regime.

    The existing market_regime.strategy_bias()
    returns a list of preferred strategies.

    This helper preserves the historical
    router_strategy concept expected by
    run_portfolio().
    """

    if df is None:

        return None

    if len(
        df
    ) == 0:

        return None

    try:

        regime = _normalize_market_regime(
            regime
        )

        preferred = strategy_bias(
            regime,
        )

        if not preferred:

            return None

        return preferred[0]

    except Exception:

        return None


# ==================================================
# RUN PORTFOLIO
# ==================================================

def run_portfolio(
    df,
):

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

    Notes
    -----
    This function intentionally preserves its historical
    return type.

    It returns a list rather than a portfolio dictionary
    so existing callers remain backward compatible.
    """

    results = []


    # ==================================================
    # MARKET REGIME
    # ==================================================

    regime = _detect_market_regime(
        df
    )

    router_strategy = _recommended_strategy(
        df,
        regime,
    )


    # ==================================================
    # LOAD ALL REGISTERED STRATEGIES
    # ==================================================

    registered_strategies = list_strategies()


    # --------------------------------------------------
    # Safety:
    # Remove duplicates while preserving order.
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
                        str(
                            exc
                        ),

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

        item[
            "rank"
        ] = index


    # ==================================================
    # FAILED STRATEGIES
    # ==================================================

    for item in failed_results:

        item[
            "rank"
        ] = 0


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
            item[
                "name"
            ],

            item[
                "statistics"
            ],

            regime=item.get(
                "market_regime",
                regime,
            ),
        )


    # ==================================================
    # RETURN
    # ==================================================

    return results


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_strategy(
    results,
):

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

def portfolio_summary(
    results,
):

    """
    Generate a compact portfolio summary.
    """

    if not results:

        return {

            "total":
                0,

            "evaluated":
                0,

            "failed":
                0,

            "best":
                None,

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
                len(
                    results
                ),

            "failed":
                len(
                    results
                ),

            "best":
                None,

        }


    best = successful[
        0
    ]


    statistics = best.get(
        "statistics",
        {},
    )


    return {

        "total":
            len(
                successful
            ),

        "evaluated":
            len(
                results
            ),

        "failed":

            len(
                results
            )

            -

            len(
                successful
            ),

        "best":

            best.get(
                "name"
            ),

        "profit_factor":

            statistics.get(
                "profit_factor",
                0,
            ),

        "win_rate":

            statistics.get(
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

    if not results:

        return []


    return [

        result

        for result in results

        if result.get(
            "evaluation_status"
        ) == "SUCCESS"

        and

        result.get(
            "statistics",
            {},
        ).get(
            "profit_factor",
            0,
        )

        >= minimum_pf

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

    if not results:

        return []


    successful = [

        result

        for result in results

        if result.get(
            "evaluation_status"
        ) == "SUCCESS"

    ]


    return successful[
        :n
    ]


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

        regime = _normalize_market_regime(
            data
        )


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


# ==================================================
# BUILD INSTITUTIONAL PORTFOLIO
# ==================================================

def build_institutional_portfolio(
    df,
):

    """
    Build complete institutional portfolio.

    This function is retained for backward
    compatibility.

    The primary institutional orchestration is owned
    by:

        engine.institutional_portfolio_engine

    This wrapper intentionally preserves the historical
    public interface of portfolio_engine.
    """


    # ==================================================
    # RUN ALL STRATEGIES
    # ==================================================

    results = run_portfolio(
        df
    )


    # ==================================================
    # EMPTY PORTFOLIO
    # ==================================================

    if not results:

        return {

            "strategies":
                [],

            "portfolio":

                {

                    "allocation":
                        [],

                    "risk":
                        {},

                },

            "summary":

                {

                    "total":
                        0,

                    "evaluated":
                        0,

                    "failed":
                        0,

                    "best":
                        None,

                },

            "regime":
                "UNKNOWN",

        }


    # ==================================================
    # BUILD DYNAMIC PORTFOLIO
    # ==================================================

    portfolio = build_portfolio(
        results
    )


    # ==================================================
    # SUMMARY
    # ==================================================

    summary = portfolio_summary(
        results
    )


    # ==================================================
    # MARKET REGIME
    # ==================================================

    regime = _normalize_market_regime(
        results[
            0
        ].get(
            "market_regime",
            "UNKNOWN",
        )
    )


    # ==================================================
    # RETURN COMPLETE OBJECT
    # ==================================================

    return {

        "strategies":
            results,

        "portfolio":
            portfolio,

        "summary":
            summary,

        "regime":
            regime,

    }