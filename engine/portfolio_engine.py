"""
==========================================
SULTAN QUANT OS
Portfolio Engine
Version : 3.3.2
==========================================

Responsibilities:

- Execute all registered strategies
- Detect market regime
- Normalize regime vocabulary
- Route recommended strategy
- Run strategy backtests
- Calculate strategy statistics
- Classify evaluation status
- Rank successful strategies
- Update regime-specific strategy memory
- Provide legacy portfolio operations
- Preserve backward compatibility

IMPORTANT:

Institutional portfolio orchestration is owned by:

    engine.institutional_portfolio_engine

This module remains responsible for:

    - Strategy evaluation
    - Strategy ranking
    - Strategy memory
    - Legacy portfolio operations

The institutional portfolio contract is owned by:

    engine.institutional_portfolio_engine
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
# CONSTANTS
# ==================================================

STATUS_SUCCESS = "SUCCESS"

STATUS_FAILED = "FAILED"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

UNKNOWN_REGIME = "UNKNOWN"


# ==================================================
# SAFE TRADE COUNT
# ==================================================

def _get_total_trades(
    statistics,
    trades=None,
):
    """
    Safely determine total trade count.

    Priority:

        1. statistics.total_trade
        2. statistics.total_trades
        3. len(trades)

    Returns
    -------
    int
    """

    if isinstance(
        statistics,
        dict,
    ):

        value = statistics.get(
            "total_trade",
            statistics.get(
                "total_trades",
                None,
            ),
        )

        if value is not None:

            try:

                return max(
                    int(
                        float(
                            value
                        )
                    ),
                    0,
                )

            except (
                TypeError,
                ValueError,
            ):

                pass

    if trades is not None:

        try:

            return max(
                len(
                    trades
                ),
                0,
            )

        except TypeError:

            pass

    return 0


# ==================================================
# EVALUATION STATUS
# ==================================================

def _determine_evaluation_status(
    statistics,
    trades,
):
    """
    Determine strategy evaluation status.

    Rules:

        Error handling is performed by the caller.

        Successful execution with:

            total trades > 0
                -> SUCCESS

            total trades == 0
                -> INSUFFICIENT_DATA
    """

    total_trades = _get_total_trades(
        statistics,
        trades,
    )

    if total_trades > 0:

        return STATUS_SUCCESS

    return STATUS_INSUFFICIENT


# ==================================================
# MARKET REGIME NORMALIZATION
# ==================================================

def _normalize_market_regime(
    regime,
):

    """
    Normalize market regime vocabulary.

    Legacy vocabulary:

        TRENDING
        RANGING
        HIGH_VOLATILITY

    Institutional vocabulary:

        STRONG_TREND
        TRENDING
        RANGE
        VOLATILE
        TRANSITION
    """

    if regime is None:

        return UNKNOWN_REGIME

    normalized = str(
        regime
    ).strip().upper()

    aliases = {

        "TRENDING":
            "TRENDING",

        "STRONG_TREND":
            "TRENDING",

        "UPTREND":
            "TRENDING",

        "DOWNTREND":
            "TRENDING",

        "RANGING":
            "RANGING",

        "RANGE":
            "RANGING",

        "QUIET_RANGE":
            "RANGING",

        "SIDEWAYS":
            "RANGING",

        "HIGH_VOLATILITY":
            "HIGH_VOLATILITY",

        "VOLATILE":
            "HIGH_VOLATILITY",

        "TRANSITION":
            UNKNOWN_REGIME,

        "UNCLEAR":
            UNKNOWN_REGIME,

        "UNKNOWN":
            UNKNOWN_REGIME,

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
    """

    if df is None:

        return UNKNOWN_REGIME

    try:

        if len(
            df
        ) == 0:

            return UNKNOWN_REGIME

    except TypeError:

        return UNKNOWN_REGIME

    try:

        regime = detect_regime(
            df.iloc[-1]
        )

        return _normalize_market_regime(
            regime
        )

    except Exception:

        return UNKNOWN_REGIME


# ==================================================
# RECOMMENDED STRATEGY
# ==================================================

def _recommended_strategy(
    df,
    regime,
):

    """
    Determine the preferred strategy for
    the detected market regime.
    """

    if df is None:

        return None

    try:

        if len(
            df
        ) == 0:

            return None

    except TypeError:

        return None

    try:

        regime = _normalize_market_regime(
            regime
        )

        preferred = strategy_bias(
            regime
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
    Execute evaluation for all registered strategies.

    Returns
    -------
    list

        Ranked successful strategies first.

        Followed by:

            INSUFFICIENT_DATA strategies

        Followed by:

            FAILED strategies.
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
    # LOAD STRATEGIES
    # ==================================================

    registered_strategies = list_strategies()


    # ==================================================
    # REMOVE DUPLICATES
    # ==================================================

    selected = list(
        dict.fromkeys(
            registered_strategies
        )
    )


    if not selected:

        return []


    # ==================================================
    # EXECUTE STRATEGIES
    # ==================================================

    for strategy in selected:

        try:

            strategy_df = deepcopy(
                df
            )


            # ------------------------------------------
            # STRATEGY
            # ------------------------------------------

            strategy_df = run_strategy(
                strategy_df,
                strategy=strategy,
            )


            # ------------------------------------------
            # BACKTEST
            # ------------------------------------------

            trades = run_backtest(
                strategy_df
            )


            # ------------------------------------------
            # STATISTICS
            # ------------------------------------------

            statistics = calculate_statistics(
                trades
            )


            # ------------------------------------------
            # STATUS
            # ------------------------------------------

            evaluation_status = (
                _determine_evaluation_status(
                    statistics,
                    trades,
                )
            )


            # ------------------------------------------
            # RESULT
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
                        0,

                    "score":
                        0,

                    "rank":
                        0,

                    "grade":
                        "N/A",

                    "router_recommended":
                        strategy == router_strategy,

                    "evaluation_status":
                        evaluation_status,

                }
            )


        except Exception as exc:

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

                    "grade":
                        "N/A",

                    "router_recommended":
                        strategy == router_strategy,

                    "evaluation_status":
                        STATUS_FAILED,

                    "error":
                        str(
                            exc
                        ),

                }
            )


    # ==================================================
    # SEPARATE RESULTS
    # ==================================================

    successful_results = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_SUCCESS

    ]


    insufficient_results = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_INSUFFICIENT

    ]


    failed_results = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_FAILED

    ]


    # ==================================================
    # RANK SUCCESSFUL STRATEGIES ONLY
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
    # ZERO RANK FOR NON-SUCCESS
    # ==================================================

    for item in insufficient_results:

        item[
            "rank"
        ] = 0


    for item in failed_results:

        item[
            "rank"
        ] = 0


    # ==================================================
    # UPDATE STRATEGY MEMORY
    #
    # Only real successful strategies update memory.
    # ==================================================

    for item in successful_results:

        try:

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

        except Exception:

            pass


    # ==================================================
    # FINAL ORDER
    # ==================================================

    return (

        successful_results

        +

        insufficient_results

        +

        failed_results

    )


# ==================================================
# BEST STRATEGY
# ==================================================

def get_best_strategy(
    results,
):

    """
    Return highest ranked successful strategy.
    """

    if not results:

        return None


    for item in results:

        if item.get(
            "evaluation_status"
        ) == STATUS_SUCCESS:

            return item


    return None


# ==================================================
# PORTFOLIO SUMMARY
# ==================================================

def portfolio_summary(
    results,
):

    """
    Generate compact portfolio summary.
    """

    if not results:

        return {

            "total":
                0,

            "evaluated":
                0,

            "failed":
                0,

            "insufficient":
                0,

            "best":
                None,

        }


    successful = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_SUCCESS

    ]


    insufficient = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_INSUFFICIENT

    ]


    failed = [

        item

        for item in results

        if item.get(
            "evaluation_status"
        ) == STATUS_FAILED

    ]


    best = get_best_strategy(
        results
    )


    if best is None:

        return {

            "total":
                0,

            "evaluated":
                len(
                    results
                ),

            "failed":
                len(
                    failed
                ),

            "insufficient":
                len(
                    insufficient
                ),

            "best":
                None,

        }


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
                failed
            ),

        "insufficient":
            len(
                insufficient
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
                UNKNOWN_REGIME,
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
    Return successful strategies whose Profit Factor
    meets the requested threshold.
    """

    if not results:

        return []


    return [

        result

        for result in results

        if result.get(
            "evaluation_status"
        ) == STATUS_SUCCESS

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
    Return top N successful strategies.
    """

    if not results:

        return []


    try:

        n = int(
            n
        )

    except (
        TypeError,
        ValueError,
    ):

        n = 3


    if n <= 0:

        return []


    successful = [

        result

        for result in results

        if result.get(
            "evaluation_status"
        ) == STATUS_SUCCESS

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
    Legacy portfolio operation.

    Supported modes:

    1. build_portfolio("TRENDING")

       Returns legacy regime allocation.

    2. build_portfolio(strategy_results)

       Returns allocation and risk.
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
            regime
        )


        risk = calculate_portfolio_risk(
            allocation
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
        results
    )


    risk = calculate_portfolio_risk(
        allocation
    )


    return {

        "allocation":
            allocation,

        "risk":
            risk,

    }


# ==================================================
# BACKWARD-COMPATIBLE INSTITUTIONAL PORTFOLIO
# ==================================================

def build_institutional_portfolio(
    df,
):

    """
    Backward-compatible wrapper.

    Institutional portfolio orchestration is owned by:

        engine.institutional_portfolio_engine

    This function intentionally delegates to the
    canonical institutional portfolio engine.

    The import is local to avoid circular imports.
    """

    from engine.institutional_portfolio_engine import (
        build_institutional_portfolio
        as _build_institutional_portfolio,
    )


    return _build_institutional_portfolio(
        df
    )