"""
==========================================
SULTAN QUANT OS
Portfolio Allocation Engine
Version : 3.0.0
==========================================

Responsibilities:

- Select qualified strategies
- Calculate dynamic allocation
- Normalize portfolio weights
- Prevent weak strategies from receiving capital
- Integrate Strategy Intelligence
- Integrate Strategy Memory
- Apply regime-aware historical confidence
- Preserve backward compatibility

Architecture:

Current Strategy Quality
        +
Historical Strategy Memory
        +
Market Regime
        ↓
Adaptive Allocation Score
        ↓
Portfolio Allocation
"""

from copy import deepcopy


# ============================================================
# STRATEGY MEMORY
# ============================================================

from strategies.intelligence.strategy_memory import (
    get_memory,
)


# ============================================================
# STRATEGY WEIGHT
# ============================================================

from strategies.intelligence.strategy_weight import (
    calculate_weight,
)


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

MIN_PROFIT_FACTOR = 1.0

MIN_SCORE = 25

MAX_STRATEGIES = 3


# ============================================================
# INTELLIGENCE CONFIGURATION
# ============================================================

# Current backtest quality remains dominant.

CURRENT_WEIGHT = 0.70

# Historical memory contributes confidence.

HISTORICAL_WEIGHT = 0.30

# Minimum historical observations before memory receives
# meaningful influence.

MIN_MEMORY_TRADES = 5


# ============================================================
# SAFE FLOAT
# ============================================================

def _safe_float(
    value,
    default=0.0,
):

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


# ============================================================
# SAFE MEMORY
# ============================================================

def _get_strategy_memory(
    strategy,
    regime,
):
    """
    Safely retrieve strategy memory.

    Memory failure must NEVER crash portfolio allocation.
    """

    try:

        memory = get_memory(
            strategy,
            regime,
        )

    except Exception:

        return {

            "trades": 0,

            "wins": 0,

            "profit": 0,

        }

    if not isinstance(
        memory,
        dict,
    ):

        return {

            "trades": 0,

            "wins": 0,

            "profit": 0,

        }

    return memory


# ============================================================
# HISTORICAL PERFORMANCE
# ============================================================

def _historical_performance(
    strategy,
    regime,
):
    """
    Convert Strategy Memory into performance metrics.

    Memory format:

        {
            "trades": ...,
            "wins": ...,
            "profit": ...
        }

    Returns a normalized performance dictionary suitable
    for Strategy Weight Engine.
    """

    memory = _get_strategy_memory(
        strategy,
        regime,
    )

    trades = max(
        0,
        int(
            _safe_float(
                memory.get(
                    "trades",
                    0,
                ),
                0,
            )
        ),
    )

    wins = max(
        0,
        int(
            _safe_float(
                memory.get(
                    "wins",
                    0,
                ),
                0,
            )
        ),
    )

    profit = _safe_float(
        memory.get(
            "profit",
            0,
        ),
        0,
    )

    if trades > 0:

        win_rate = (
            wins
            /
            trades
            *
            100
        )

    else:

        win_rate = 0.0

    return {

        "trades":
            trades,

        "wins":
            wins,

        "profit":
            profit,

        "win_rate":
            win_rate,

    }


# ============================================================
# HISTORICAL CONFIDENCE
# ============================================================

def _historical_confidence(
    strategy,
    regime,
):
    """
    Calculate historical confidence from Strategy Memory.

    Important:

    No memory means neutral confidence.

    This prevents a new strategy from being unfairly
    penalized simply because it has never traded before.
    """

    performance = _historical_performance(
        strategy,
        regime,
    )

    trades = performance["trades"]

    if trades <= 0:

        return 0.50

    win_rate = max(
        0,
        min(
            performance["win_rate"],
            100,
        ),
    )

    # --------------------------------------------------------
    # Base confidence from win rate.
    #
    # 50% win rate = neutral.
    # Above 50% = positive.
    # Below 50% = negative.
    # --------------------------------------------------------

    win_component = (
        win_rate
        /
        100
    )

    # --------------------------------------------------------
    # Reliability factor.
    #
    # 5 trades -> partial confidence
    # 100+ trades -> full confidence
    # --------------------------------------------------------

    reliability = min(
        trades / 100,
        1.0,
    )

    confidence = (

        0.50

        +

        (
            win_component
            -
            0.50
        )
        *
        reliability

    )

    return round(
        max(
            0.0,
            min(
                confidence,
                1.0,
            ),
        ),
        6,
    )


# ============================================================
# HISTORICAL WEIGHT
# ============================================================

def _historical_weight(
    strategy,
    regime,
):
    """
    Calculate Strategy Intelligence historical weight.

    Uses the existing Strategy Weight Engine rather than
    creating a second scoring methodology.
    """

    performance = _historical_performance(
        strategy,
        regime,
    )

    trades = performance.get(
        "trades",
        0,
    )

    if trades <= 0:

        return 0.0

    return max(
        0.0,
        _safe_float(
            calculate_weight(
                performance
            ),
            0,
        ),
    )


# ============================================================
# CURRENT QUALITY SCORE
# ============================================================

def _current_quality_score(
    item,
):
    """
    Convert current Strategy Ranker score into normalized
    quality between 0 and 1.

    Strategy Ranker score is normally 0-100.
    """

    score = _safe_float(
        item.get(
            "score",
            0,
        ),
        0,
    )

    return max(
        0.0,
        min(
            score / 100,
            1.0,
        ),
    )


# ============================================================
# ADAPTIVE ALLOCATION SCORE
# ============================================================

def calculate_adaptive_allocation_score(
    item,
    regime="UNKNOWN",
):
    """
    Combine current strategy quality and historical memory.

    Formula:

        Current Quality × 70%
        +
        Historical Intelligence × 30%

    Historical intelligence is only meaningful when memory
    exists.

    The current strategy evaluation remains dominant.
    """

    strategy = item.get(
        "name",
        item.get(
            "id",
            "",
        ),
    )

    current_quality = _current_quality_score(
        item
    )

    historical_weight = _historical_weight(
        strategy,
        regime,
    )

    confidence = _historical_confidence(
        strategy,
        regime,
    )

    # --------------------------------------------------------
    # Normalize historical weight.
    #
    # Strategy Weight Engine does not guarantee a fixed
    # maximum, therefore use a conservative saturation.
    # --------------------------------------------------------

    historical_quality = min(
        historical_weight / 100,
        1.0,
    )

    # --------------------------------------------------------
    # Confidence adjustment.
    #
    # Historical quality is blended with confidence so that
    # weak evidence cannot dominate.
    # --------------------------------------------------------

    historical_quality *= confidence

    # --------------------------------------------------------
    # Adaptive score
    # --------------------------------------------------------

    score = (

        current_quality
        *
        CURRENT_WEIGHT

        +

        historical_quality
        *
        HISTORICAL_WEIGHT

    )

    return round(
        max(
            score,
            0.0,
        ),
        6,
    )


# ============================================================
# BUILD ALLOCATION
# ============================================================

def build_allocation(
    results,
    max_strategies=MAX_STRATEGIES,
    minimum_pf=MIN_PROFIT_FACTOR,
    minimum_score=MIN_SCORE,
    regime=None,
):
    """
    Build dynamic institutional portfolio allocation.

    Parameters
    ----------
    results:
        Ranked strategy results.

    max_strategies:
        Maximum strategies receiving capital.

    minimum_pf:
        Minimum Profit Factor.

    minimum_score:
        Minimum Strategy Ranker score.

    regime:
        Market regime used for regime-specific Strategy Memory.

        If omitted, the function attempts to obtain the regime
        from the first result.

    Selection priority:

        1. Profit Factor
        2. Strategy Score
        3. Positive Expectancy
        4. Historical Strategy Intelligence

    Allocation:

        Current strategy quality
                +
        Historical regime-specific confidence
    """

    if not results:

        return []

    # ========================================================
    # VALIDATE LIMIT
    # ========================================================

    try:

        max_strategies = int(
            max_strategies
        )

    except (
        TypeError,
        ValueError,
    ):

        max_strategies = MAX_STRATEGIES

    if max_strategies <= 0:

        return []

    # ========================================================
    # DETERMINE REGIME
    # ========================================================

    if regime is None:

        regime = "UNKNOWN"

        for item in results:

            if isinstance(
                item,
                dict,
            ):

                detected_regime = item.get(
                    "market_regime",
                    None,
                )

                if detected_regime:

                    regime = detected_regime

                    break

    if regime is None:

        regime = "UNKNOWN"

    # ========================================================
    # PRIMARY CANDIDATES
    # ========================================================

    candidates = []

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue

        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        status = item.get(
            "evaluation_status",
            "SUCCESS",
        )

        if status != "SUCCESS":

            continue

        statistics = item.get(
            "statistics",
            {},
        )

        if not isinstance(
            statistics,
            dict,
        ):

            continue

        # ----------------------------------------------------
        # Metrics
        # ----------------------------------------------------

        pf = _safe_float(
            statistics.get(
                "profit_factor",
                0,
            ),
            0,
        )

        score = _safe_float(
            item.get(
                "score",
                0,
            ),
            0,
        )

        expectancy = _safe_float(
            statistics.get(
                "expectancy",
                0,
            ),
            0,
        )

        # ----------------------------------------------------
        # QUALITY FILTER
        # ----------------------------------------------------

        if pf < minimum_pf:

            continue

        if score < minimum_score:

            continue

        if expectancy <= 0:

            continue

        # ----------------------------------------------------
        # COPY
        # ----------------------------------------------------

        candidate = deepcopy(
            item
        )

        # ----------------------------------------------------
        # Intelligence
        # ----------------------------------------------------

        strategy = candidate.get(
            "name",
            "",
        )

        memory = _historical_performance(
            strategy,
            regime,
        )

        historical_confidence = (
            _historical_confidence(
                strategy,
                regime,
            )
        )

        historical_weight = (
            _historical_weight(
                strategy,
                regime,
            )
        )

        adaptive_score = (
            calculate_adaptive_allocation_score(
                candidate,
                regime=regime,
            )
        )

        # ----------------------------------------------------
        # Weight
        # ----------------------------------------------------

        candidate["weight"] = max(
            adaptive_score,
            0.0,
        )

        # ----------------------------------------------------
        # Intelligence metadata
        # ----------------------------------------------------

        candidate["adaptive_score"] = (
            adaptive_score
        )

        candidate["historical_weight"] = (
            historical_weight
        )

        candidate["historical_confidence"] = (
            historical_confidence
        )

        candidate["memory_trades"] = (
            memory.get(
                "trades",
                0,
            )
        )

        candidate["memory_wins"] = (
            memory.get(
                "wins",
                0,
            )
        )

        candidate["memory_profit"] = (
            memory.get(
                "profit",
                0,
            )
        )

        candidate["allocation_regime"] = (
            regime
        )

        candidates.append(
            candidate
        )

    # ========================================================
    # FALLBACK
    # ========================================================

    if not candidates:

        for item in results:

            if not isinstance(
                item,
                dict,
            ):

                continue

            status = item.get(
                "evaluation_status",
                "SUCCESS",
            )

            if status != "SUCCESS":

                continue

            statistics = item.get(
                "statistics",
                {},
            )

            if not isinstance(
                statistics,
                dict,
            ):

                continue

            pf = _safe_float(
                statistics.get(
                    "profit_factor",
                    0,
                ),
                0,
            )

            if pf <= 0:

                continue

            candidate = deepcopy(
                item
            )

            strategy = candidate.get(
                "name",
                "",
            )

            adaptive_score = (
                calculate_adaptive_allocation_score(
                    candidate,
                    regime=regime,
                )
            )

            # ------------------------------------------------
            # Fallback must still give a positive weight.
            # ------------------------------------------------

            candidate["weight"] = max(
                adaptive_score,
                0.01,
            )

            candidate["adaptive_score"] = (
                adaptive_score
            )

            candidate["historical_weight"] = (
                _historical_weight(
                    strategy,
                    regime,
                )
            )

            candidate["historical_confidence"] = (
                _historical_confidence(
                    strategy,
                    regime,
                )
            )

            candidate["allocation_regime"] = (
                regime
            )

            candidates.append(
                candidate
            )

    # ========================================================
    # NO CANDIDATE
    # ========================================================

    if not candidates:

        return []

    # ========================================================
    # SORT
    # ========================================================

    candidates.sort(
        key=lambda x: (
            x.get(
                "weight",
                0,
            ),

            x.get(
                "score",
                0,
            ),

            _safe_float(
                x.get(
                    "statistics",
                    {},
                ).get(
                    "profit_factor",
                    0,
                ),
                0,
            ),

            _safe_float(
                x.get(
                    "statistics",
                    {},
                ).get(
                    "expectancy",
                    0,
                ),
                0,
            ),

        ),
        reverse=True,
    )

    # ========================================================
    # LIMIT STRATEGIES
    # ========================================================

    candidates = candidates[
        :max_strategies
    ]

    if not candidates:

        return []

    # ========================================================
    # NORMALIZE WEIGHTS
    # ========================================================

    total_weight = sum(
        max(
            _safe_float(
                item.get(
                    "weight",
                    0,
                ),
                0,
            ),
            0,
        )

        for item in candidates
    )

    # ========================================================
    # EQUAL WEIGHT FALLBACK
    # ========================================================

    if total_weight <= 0:

        equal_weight = (
            1.0
            /
            len(candidates)
        )

        for item in candidates:

            item["allocation"] = round(
                equal_weight,
                4,
            )

    else:

        for item in candidates:

            item["allocation"] = round(
                max(
                    _safe_float(
                        item.get(
                            "weight",
                            0,
                        ),
                        0,
                    ),
                    0,
                )
                /
                total_weight,
                4,
            )

    # ========================================================
    # FLOATING POINT CORRECTION
    # ========================================================

    allocation_sum = round(
        sum(
            item.get(
                "allocation",
                0,
            )

            for item in candidates
        ),
        4,
    )

    difference = round(
        1.0
        -
        allocation_sum,
        4,
    )

    if difference != 0:

        best = max(
            candidates,
            key=lambda x: x.get(
                "allocation",
                0,
            ),
        )

        best["allocation"] = round(
            best.get(
                "allocation",
                0,
            )
            +
            difference,
            4,
        )

    return candidates