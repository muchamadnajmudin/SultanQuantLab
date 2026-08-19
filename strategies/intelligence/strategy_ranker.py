"""
============================================================
SULTAN QUANT OS
Strategy Ranker
Version : 3.0.0
============================================================

Responsibilities:

- Rank multiple strategies
- Compare strategy quality
- Preserve complete strategy result
- Preserve evaluation status
- Preserve portfolio metadata
- Use Strategy Analyzer score
- Provide backward-compatible fallback scoring
- Detect insufficient strategy data
- Never silently rank invalid strategies as successful
- Never silently discard strategy metadata
============================================================
"""

from copy import deepcopy


# ============================================================
# STATUS
# ============================================================

STATUS_SUCCESS = "SUCCESS"
STATUS_FAILED = "FAILED"
STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


# ============================================================
# SAFE VALUE
# ============================================================

def _safe_float(value, default=0.0):

    try:
        return float(value)

    except (TypeError, ValueError):

        return default


# ============================================================
# TRADE COUNT
# ============================================================

def _trade_count(statistics, trades=None):

    """
    Determine number of trades.

    Priority:

    1. statistics['total_trade']
    2. statistics['total_trades']
    3. len(trades)
    """

    if not isinstance(statistics, dict):

        statistics = {}

    total_trade = statistics.get(
        "total_trade",
        None,
    )

    if total_trade is None:

        total_trade = statistics.get(
            "total_trades",
            None,
        )

    if total_trade is not None:

        return max(
            0,
            int(
                _safe_float(
                    total_trade,
                    0,
                )
            ),
        )

    if trades is not None:

        try:
            return len(trades)

        except TypeError:
            pass

    return 0

# ============================================================
# DATA SUFFICIENCY
# ============================================================

def _is_insufficient_data(
    statistics,
    trades=None,
):
    """
    Detect strategies that do not have enough evidence
    to be institutionally ranked.

    Important:

    - Explicit total_trade == 0 -> insufficient
    - Explicit total_trades == 0 -> insufficient
    - Explicit empty trades list -> insufficient
    - Missing trade-count information -> DO NOT automatically
      classify as insufficient.

    This preserves backward compatibility with strategy
    results that provide performance statistics without
    explicitly storing trade count.
    """

    if not isinstance(statistics, dict):
        statistics = {}

    # --------------------------------------------------------
    # Explicit trade count
    # --------------------------------------------------------

    if "total_trade" in statistics:

        return (
            _safe_float(
                statistics.get(
                    "total_trade",
                    0,
                ),
                0,
            )
            <= 0
        )

    if "total_trades" in statistics:

        return (
            _safe_float(
                statistics.get(
                    "total_trades",
                    0,
                ),
                0,
            )
            <= 0
        )

    # --------------------------------------------------------
    # Explicit trades collection
    # --------------------------------------------------------

    if trades is not None:

        try:
            return len(trades) <= 0

        except TypeError:
            pass

    # --------------------------------------------------------
    # Trade count unavailable
    #
    # Do NOT assume zero trades.
    # Statistics may still be sufficient for ranking.
    # --------------------------------------------------------

    return False

# ============================================================
# FALLBACK SCORE
# ============================================================

def _fallback_score(statistics):

    """
    Conservative fallback score.

    Used only when Strategy Analyzer has not produced
    a score.

    Maximum = 100.
    """

    if not isinstance(statistics, dict):

        return 0.0

    profit_factor = _safe_float(
        statistics.get(
            "profit_factor",
            0,
        )
    )

    win_rate = _safe_float(
        statistics.get(
            "win_rate",
            0,
        )
    )

    drawdown = _safe_float(
        statistics.get(
            "max_drawdown_percent",
            100,
        )
    )

    expectancy = _safe_float(
        statistics.get(
            "expectancy",
            0,
        )
    )

    score = 0.0

    # --------------------------------------------------------
    # Profit Factor
    # --------------------------------------------------------

    if profit_factor >= 2.0:

        score += 40

    elif profit_factor >= 1.5:

        score += 30

    elif profit_factor >= 1.2:

        score += 20

    elif profit_factor >= 1.0:

        score += 10

    # --------------------------------------------------------
    # Win Rate
    # --------------------------------------------------------

    if win_rate >= 50:

        score += 20

    elif win_rate >= 40:

        score += 15

    elif win_rate >= 30:

        score += 10

    # --------------------------------------------------------
    # Drawdown
    # --------------------------------------------------------

    if drawdown <= 10:

        score += 20

    elif drawdown <= 15:

        score += 15

    elif drawdown <= 20:

        score += 10

    elif drawdown <= 30:

        score += 5

    # --------------------------------------------------------
    # Expectancy
    # --------------------------------------------------------

    if expectancy > 0:

        score += 20

    return round(
        min(score, 100),
        2,
    )


# ============================================================
# GRADE
# ============================================================

def _grade_from_score(score):

    score = _safe_float(
        score,
        0,
    )

    if score >= 90:

        return "A"

    if score >= 80:

        return "B"

    if score >= 70:

        return "C"

    if score >= 60:

        return "D"

    return "F"


# ============================================================
# RANK STRATEGIES
# ============================================================

def rank_strategies(
    strategy_results: list[dict],
):

    """
    Rank strategies from best to worst.

    Priority:

    1. Strategy Analyzer score
    2. Profit Factor
    3. Lower Drawdown
    4. Win Rate
    5. Expectancy

    Important:

    - SUCCESS strategies are ranked.
    - INSUFFICIENT_DATA strategies are preserved but
      placed after successful strategies.
    - FAILED strategies are preserved but placed last.
    - Original metadata is preserved.
    """

    if not strategy_results:

        return []

    ranking = deepcopy(
        strategy_results
    )

    prepared = []

    # ========================================================
    # PREPARE RESULTS
    # ========================================================

    for strategy in ranking:

        if not isinstance(
            strategy,
            dict,
        ):

            continue

        statistics = strategy.get(
            "statistics",
            {},
        )

        if not isinstance(
            statistics,
            dict,
        ):

            statistics = {}

        analysis = strategy.get(
            "analysis",
            {},
        )

        if not isinstance(
            analysis,
            dict,
        ):

            analysis = {}

        trades = strategy.get(
            "trades",
            None,
        )

        # ----------------------------------------------------
        # Preserve original status
        # ----------------------------------------------------

        evaluation_status = strategy.get(
            "evaluation_status",
            None,
        )

        # ----------------------------------------------------
        # Detect insufficient data
        # ----------------------------------------------------

        if evaluation_status == STATUS_SUCCESS:

            if _is_insufficient_data(
                statistics,
                trades,
            ):

                evaluation_status = (
                    STATUS_INSUFFICIENT_DATA
                )

        elif evaluation_status is None:

            if strategy.get(
                "error",
                None,
            ):

                evaluation_status = (
                    STATUS_FAILED
                )

            elif _is_insufficient_data(
                statistics,
                trades,
            ):

                evaluation_status = (
                    STATUS_INSUFFICIENT_DATA
                )

            else:

                evaluation_status = (
                    STATUS_SUCCESS
                )

        # ----------------------------------------------------
        # Analyzer score
        # ----------------------------------------------------

        analyzer_score = analysis.get(
            "score",
            None,
        )

        if analyzer_score is None:

            if (
                evaluation_status
                ==
                STATUS_SUCCESS
            ):

                analyzer_score = _fallback_score(
                    statistics
                )

            else:

                analyzer_score = 0.0

        else:

            analyzer_score = _safe_float(
                analyzer_score,
                0,
            )

        # ----------------------------------------------------
        # Grade
        # ----------------------------------------------------

        grade = analysis.get(
            "grade",
            None,
        )

        if not grade:

            if (
                evaluation_status
                ==
                STATUS_INSUFFICIENT_DATA
            ):

                grade = "N/A"

            elif (
                evaluation_status
                ==
                STATUS_FAILED
            ):

                grade = "N/A"

            else:

                grade = _grade_from_score(
                    analyzer_score
                )

        # ----------------------------------------------------
        # Normalize metrics
        # ----------------------------------------------------

        profit_factor = _safe_float(
            statistics.get(
                "profit_factor",
                0,
            )
        )

        drawdown = _safe_float(
            statistics.get(
                "max_drawdown_percent",
                100,
            ),
            100,
        )

        win_rate = _safe_float(
            statistics.get(
                "win_rate",
                0,
            )
        )

        expectancy = _safe_float(
            statistics.get(
                "expectancy",
                0,
            )
        )

        # ----------------------------------------------------
        # Preserve ALL original strategy metadata
        # ----------------------------------------------------

        strategy["analysis"] = analysis

        strategy["statistics"] = statistics

        strategy["evaluation_status"] = (
            evaluation_status
        )

        strategy["score"] = round(
            analyzer_score,
            2,
        )

        strategy["grade"] = grade

        strategy["_profit_factor"] = (
            profit_factor
        )

        strategy["_drawdown"] = (
            drawdown
        )

        strategy["_win_rate"] = (
            win_rate
        )

        strategy["_expectancy"] = (
            expectancy
        )

        strategy["_trade_count"] = (
            _trade_count(
                statistics,
                trades,
            )
        )

        prepared.append(
            strategy
        )

    # ========================================================
    # SORT
    # ========================================================

    def ranking_key(item):

        status = item.get(
            "evaluation_status",
            STATUS_FAILED,
        )

        # SUCCESS first
        if status == STATUS_SUCCESS:

            status_priority = 2

        # Insufficient data second
        elif (
            status
            ==
            STATUS_INSUFFICIENT_DATA
        ):

            status_priority = 1

        # Failed last
        else:

            status_priority = 0

        return (

            status_priority,

            item.get(
                "score",
                0,
            ),

            item.get(
                "_profit_factor",
                0,
            ),

            -item.get(
                "_drawdown",
                100,
            ),

            item.get(
                "_win_rate",
                0,
            ),

            item.get(
                "_expectancy",
                0,
            ),

        )

    prepared.sort(
        key=ranking_key,
        reverse=True,
    )

    # ========================================================
    # BUILD FINAL RESULTS
    # ========================================================

    results = []

    success_rank = 0

    for strategy in prepared:

        status = strategy.get(
            "evaluation_status",
            STATUS_FAILED,
        )

        if status == STATUS_SUCCESS:

            success_rank += 1

            rank = success_rank

        else:

            rank = 0

        # ----------------------------------------------------
        # Copy complete object
        # ----------------------------------------------------

        result = deepcopy(
            strategy
        )

        # ----------------------------------------------------
        # Institutional ranking fields
        # ----------------------------------------------------

        result["rank"] = rank

        result["name"] = strategy.get(
            "name",
        )

        result["score"] = strategy.get(
            "score",
            0,
        )

        result["grade"] = strategy.get(
            "grade",
            "N/A",
        )

        result["analysis"] = strategy.get(
            "analysis",
            {},
        )

        result["statistics"] = strategy.get(
            "statistics",
            {},
        )

        result["evaluation_status"] = (
            status
        )

        # ----------------------------------------------------
        # Preserve optional objects
        # ----------------------------------------------------

        result["dataframe"] = strategy.get(
            "dataframe",
            None,
        )

        result["trades"] = strategy.get(
            "trades",
            None,
        )

        # ----------------------------------------------------
        # Preserve portfolio metadata
        # ----------------------------------------------------

        result["weight"] = strategy.get(
            "weight",
            0,
        )

        result["market_regime"] = strategy.get(
            "market_regime",
            "UNKNOWN",
        )

        result["router_recommended"] = (
            strategy.get(
                "router_recommended",
                False,
            )
        )

        # ----------------------------------------------------
        # Preserve failure information
        # ----------------------------------------------------

        if "error" in strategy:

            result["error"] = strategy[
                "error"
            ]

        # ----------------------------------------------------
        # Quick metrics
        # ----------------------------------------------------

        result["profit_factor"] = (
            strategy["statistics"].get(
                "profit_factor",
                0,
            )
        )

        result["drawdown"] = (
            strategy["statistics"].get(
                "max_drawdown_percent",
                0,
            )
        )

        result["win_rate"] = (
            strategy["statistics"].get(
                "win_rate",
                0,
            )
        )

        result["expectancy"] = (
            strategy["statistics"].get(
                "expectancy",
                0,
            )
        )

        # ----------------------------------------------------
        # Internal fields must not leak
        # ----------------------------------------------------

        result.pop(
            "_profit_factor",
            None,
        )

        result.pop(
            "_drawdown",
            None,
        )

        result.pop(
            "_win_rate",
            None,
        )

        result.pop(
            "_expectancy",
            None,
        )

        result.pop(
            "_trade_count",
            None,
        )

        results.append(
            result
        )

    return results