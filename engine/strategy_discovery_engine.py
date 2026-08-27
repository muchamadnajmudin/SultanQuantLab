"""
==========================================
SULTAN QUANT OS
Strategy Discovery Engine
Version : 1.1.0
==========================================

Responsibilities:

- Receive strategy gap results
- Normalize compatible gap contracts
- Analyze current market context
- Infer candidate strategy method
- Generate strategy discovery candidates
- Score discovery candidates
- Preserve stable discovery contracts

IMPORTANT:

This engine DOES NOT activate, register,
or execute discovered strategies.

Discovered candidates must pass validation,
backtesting, and institutional approval before
they can become active.
"""

from copy import deepcopy


# ==================================================
# DISCOVERY STATUS
# ==================================================

DISCOVERY_STATUS_NO_GAP = "NO_GAP"

DISCOVERY_STATUS_DISCOVERED = "DISCOVERED"

DISCOVERY_STATUS_NO_CANDIDATE = "NO_CANDIDATE"


# ==================================================
# DEFAULTS
# ==================================================

DEFAULT_MIN_SCORE = 0.60


# ==================================================
# SAFE DICTIONARY
# ==================================================

def _safe_dict(
    value,
):
    """
    Return a safe dictionary copy.
    """

    if not isinstance(
        value,
        dict,
    ):

        return {}

    return deepcopy(
        value
    )


# ==================================================
# SAFE LIST
# ==================================================

def _safe_list(
    value,
):
    """
    Return a safe list copy.
    """

    if not isinstance(
        value,
        list,
    ):

        return []

    return deepcopy(
        value
    )


# ==================================================
# NORMALIZE SCORE
# ==================================================

def _normalize_score(
    value,
):
    """
    Normalize numeric score into range:

        0.0 -> 1.0

    Invalid values return 0.0.
    """

    try:

        score = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0


    if score != score:

        return 0.0


    if score < 0.0:

        return 0.0


    if score > 1.0:

        return 1.0


    return score


# ==================================================
# NORMALIZE GAP RESULT
# ==================================================

def _normalize_gap_result(
    gap_result,
):
    """
    Normalize Strategy Gap Engine output into the
    stable Strategy Discovery input contract.

    Supported input contracts
    -------------------------

    Legacy discovery contract:

        {
            "gap_detected": bool,
            "qualified_strategies": list,
            "weak_strategies": list,
            "market_context": dict,
        }

    Strategy Gap Engine contract:

        {
            "discovery_required": bool,
            "qualified_strategies": list,
            "weak_strategies": list,
            "market_context": dict,
        }

    Canonical normalized field:

        gap_detected
    """

    if not isinstance(
        gap_result,
        dict,
    ):

        return {

            "gap_detected":

                False,


            "qualified_strategies":

                [],


            "weak_strategies":

                [],


            "market_context":

                {},

        }


    # ==============================================
    # GAP DETECTION
    #
    # Priority:
    #
    # 1. Explicit gap_detected
    # 2. Strategy Gap Engine discovery_required
    # 3. False
    # ==============================================

    if "gap_detected" in gap_result:

        gap_detected = bool(

            gap_result.get(
                "gap_detected"
            )

        )

    else:

        gap_detected = bool(

            gap_result.get(
                "discovery_required",
                False,
            )

        )


    # ==============================================
    # NORMALIZED RESULT
    # ==============================================

    return {

        "gap_detected":

            gap_detected,


        "qualified_strategies":

            _safe_list(

                gap_result.get(
                    "qualified_strategies"
                )

            ),


        "weak_strategies":

            _safe_list(

                gap_result.get(
                    "weak_strategies"
                )

            ),


        "market_context":

            _safe_dict(

                gap_result.get(
                    "market_context"
                )

            ),

    }


# ==================================================
# EXTRACT MARKET CONTEXT
# ==================================================

def _extract_market_context(
    gap_result,
    market_context,
):
    """
    Merge market context from Strategy Gap Engine
    with optional external market context.

    Explicit market_context argument has priority.
    """

    context = _safe_dict(

        gap_result.get(
            "market_context"
        )

    )


    external_context = _safe_dict(
        market_context
    )


    context.update(
        external_context
    )


    return context


# ==================================================
# INFER METHOD TYPE
# ==================================================

def _infer_method_type(
    market_context,
):
    """
    Infer the most suitable candidate strategy
    method from current market conditions.
    """

    context = _safe_dict(
        market_context
    )


    regime = str(

        context.get(
            "regime",

            context.get(
                "market_regime",
                "",
            ),

        )

    ).strip().upper()


    trend_strength = _normalize_score(

        context.get(
            "trend_strength",
            0.0,
        )

    )


    volatility = _normalize_score(

        context.get(
            "volatility",
            0.0,
        )

    )


    # ==============================================
    # TREND
    # ==============================================

    if regime in {

        "TREND",

        "TRENDING",

        "STRONG_TREND",

        "UPTREND",

        "DOWNTREND",

    }:

        return "TREND_FOLLOWING"


    # ==============================================
    # RANGE
    # ==============================================

    if regime in {

        "RANGE",

        "RANGING",

        "QUIET_RANGE",

        "SIDEWAYS",

    }:

        return "MEAN_REVERSION"


    # ==============================================
    # VOLATILITY
    # ==============================================

    if regime in {

        "VOLATILE",

        "VOLATILE_RANGE",

        "HIGH_VOLATILITY",

        "BREAKOUT",

    }:

        return "BREAKOUT"


    # ==============================================
    # CONTEXT FALLBACK
    # ==============================================

    if trend_strength >= 0.70:

        return "TREND_FOLLOWING"


    if volatility >= 0.70:

        return "BREAKOUT"


    return "HYBRID"


# ==================================================
# BUILD CANDIDATE
# ==================================================

def _build_candidate(
    market_context,
    gap_result,
):
    """
    Build one candidate trading method based on
    current market context and strategy coverage.
    """

    method_type = _infer_method_type(
        market_context
    )


    qualified_count = len(

        gap_result.get(
            "qualified_strategies",
            [],
        )

    )


    weak_count = len(

        gap_result.get(
            "weak_strategies",
            [],
        )

    )


    # ==============================================
    # CONFIDENCE
    # ==============================================

    confidence = _normalize_score(

        market_context.get(

            "confidence",

            market_context.get(
                "regime_confidence",
                0.50,
            ),

        )

    )


    # ==============================================
    # COVERAGE PENALTY
    # ==============================================

    coverage_penalty = min(

        weak_count * 0.05,

        0.25,

    )


    # ==============================================
    # QUALIFIED BONUS
    # ==============================================

    qualified_bonus = min(

        qualified_count * 0.02,

        0.10,

    )


    # ==============================================
    # DISCOVERY SCORE
    # ==============================================

    discovery_score = _normalize_score(

        0.50

        + (
            confidence * 0.30
        )

        + qualified_bonus

        - coverage_penalty

    )


    # ==============================================
    # RESULT
    # ==============================================

    return {

        "name":

            f"{method_type}_DISCOVERY_CANDIDATE",


        "method_type":

            method_type,


        "market_context":

            deepcopy(
                market_context
            ),


        "source":

            "STRATEGY_DISCOVERY_ENGINE",


        "discovery_score":

            discovery_score,


        "status":

            (

                "QUALIFIED"

                if discovery_score
                >= DEFAULT_MIN_SCORE

                else "WEAK"

            ),

    }


# ==================================================
# DISCOVER STRATEGIES
# ==================================================

def discover_strategies(
    gap_result,
    market_context=None,
):
    """
    Discover candidate trading methods from a
    strategy gap.

    Parameters
    ----------

    gap_result : dict
        Result from Strategy Gap Engine or compatible
        legacy discovery contract.

    market_context : dict, optional
        Additional current market information.

    Returns
    -------

    dict
        Stable strategy discovery result.
    """

    # ==============================================
    # NORMALIZE INPUT
    # ==============================================

    normalized_gap = _normalize_gap_result(
        gap_result
    )


    # ==============================================
    # MARKET CONTEXT
    # ==============================================

    context = _extract_market_context(

        normalized_gap,

        market_context,

    )


    # ==============================================
    # DEFAULT RESULT CONTRACT
    # ==============================================

    result = {

        "status":

            DISCOVERY_STATUS_NO_GAP,


        "gap_detected":

            normalized_gap[
                "gap_detected"
            ],


        "market_context":

            deepcopy(
                context
            ),


        "candidates":

            [],


        "qualified_candidates":

            [],


        "rejected_candidates":

            [],

    }


    # ==============================================
    # NO GAP
    # ==============================================

    if not normalized_gap[
        "gap_detected"
    ]:

        return deepcopy(
            result
        )


    # ==============================================
    # BUILD CANDIDATE
    # ==============================================

    candidate = _build_candidate(

        context,

        normalized_gap,

    )


    result[
        "candidates"
    ].append(

        deepcopy(
            candidate
        )

    )


    # ==============================================
    # QUALIFIED CANDIDATE
    # ==============================================

    if candidate[
        "status"
    ] == "QUALIFIED":

        result[
            "qualified_candidates"
        ].append(

            deepcopy(
                candidate
            )

        )


        result[
            "status"
        ] = (

            DISCOVERY_STATUS_DISCOVERED

        )


    # ==============================================
    # REJECTED CANDIDATE
    # ==============================================

    else:

        result[
            "rejected_candidates"
        ].append(

            deepcopy(
                candidate
            )

        )


        result[
            "status"
        ] = (

            DISCOVERY_STATUS_NO_CANDIDATE

        )


    return deepcopy(
        result
    )


# ==================================================
# BACKWARD-FRIENDLY ALIAS
# ==================================================

discover_strategy = discover_strategies


# ==================================================
# STRATEGY DISCOVERY ENGINE
# ==================================================

class StrategyDiscoveryEngine:
    """
    Object-oriented wrapper for Strategy Discovery
    Engine.
    """

    def discover(
        self,
        gap_result,
        market_context=None,
    ):

        return discover_strategies(

            gap_result,

            market_context,

        )


    def run(
        self,
        gap_result,
        market_context=None,
    ):

        return self.discover(

            gap_result,

            market_context,

        )