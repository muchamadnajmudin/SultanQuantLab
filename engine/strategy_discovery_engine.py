"""
==========================================
SULTAN QUANT OS
Strategy Discovery Engine
Version : 1.0.0
==========================================

Responsibilities:

- Receive strategy gap information
- Preserve market context
- Generate candidate trading methods
- Evaluate candidate quality
- Return stable discovery contract

This engine does not automatically activate strategies.
All discovered candidates must pass the existing validation
and institutional pipeline before they can become active.
"""

from copy import deepcopy


DISCOVERY_STATUS_NO_GAP = "NO_GAP"
DISCOVERY_STATUS_DISCOVERED = "DISCOVERED"
DISCOVERY_STATUS_NO_CANDIDATE = "NO_CANDIDATE"

DEFAULT_MIN_SCORE = 0.60


def _safe_dict(value):
    return deepcopy(value) if isinstance(value, dict) else {}


def _safe_list(value):
    return deepcopy(value) if isinstance(value, list) else []


def _normalize_score(value):
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    return max(0.0, min(1.0, score))


def _normalize_gap_result(gap_result):
    if not isinstance(gap_result, dict):
        return {
            "gap_detected": False,
            "qualified_strategies": [],
            "weak_strategies": [],
            "market_context": {},
        }

    return {
        "gap_detected": bool(gap_result.get("gap_detected", False)),
        "qualified_strategies": _safe_list(
            gap_result.get("qualified_strategies")
        ),
        "weak_strategies": _safe_list(
            gap_result.get("weak_strategies")
        ),
        "market_context": _safe_dict(
            gap_result.get("market_context")
        ),
    }


def _extract_market_context(gap_result, market_context):
    context = _safe_dict(
        gap_result.get("market_context")
    )

    if isinstance(market_context, dict):
        context.update(deepcopy(market_context))

    return context


def _infer_method_type(market_context):
    regime = str(
        market_context.get("regime", "")
    ).upper()

    trend_strength = _normalize_score(
        market_context.get("trend_strength", 0.0)
    )

    volatility = _normalize_score(
        market_context.get("volatility", 0.0)
    )

    if regime in {
        "TREND",
        "STRONG_TREND",
        "BULLISH",
        "BEARISH",
    }:
        return "TREND_FOLLOWING"

    if regime in {
        "RANGE",
        "SIDEWAYS",
        "MEAN_REVERSION",
    }:
        return "MEAN_REVERSION"

    if regime in {
        "VOLATILE",
        "VOLATILE_RANGE",
        "BREAKOUT",
    }:
        return "BREAKOUT"

    if trend_strength >= 0.70:
        return "TREND_FOLLOWING"

    if volatility >= 0.70:
        return "BREAKOUT"

    return "HYBRID"


def _build_candidate(market_context, gap_result):
    method_type = _infer_method_type(
        market_context
    )

    qualified_count = len(
        gap_result.get("qualified_strategies", [])
    )

    weak_count = len(
        gap_result.get("weak_strategies", [])
    )

    confidence = _normalize_score(
        market_context.get(
            "confidence",
            market_context.get(
                "regime_confidence",
                0.50,
            ),
        )
    )

    coverage_penalty = min(
        weak_count * 0.05,
        0.25,
    )

    qualified_bonus = min(
        qualified_count * 0.02,
        0.10,
    )

    discovery_score = _normalize_score(
        0.50
        + (confidence * 0.30)
        + qualified_bonus
        - coverage_penalty
    )

    return {
        "name": f"{method_type}_DISCOVERY_CANDIDATE",
        "method_type": method_type,
        "market_context": deepcopy(market_context),
        "source": "STRATEGY_DISCOVERY_ENGINE",
        "discovery_score": discovery_score,
        "status": (
            "QUALIFIED"
            if discovery_score >= DEFAULT_MIN_SCORE
            else "WEAK"
        ),
    }


def discover_strategies(
    gap_result,
    market_context=None,
):
    """
    Discover candidate trading methods from a strategy gap.

    Parameters
    ----------
    gap_result : dict
        Result from Strategy Gap Engine.

    market_context : dict, optional
        Additional current market information.

    Returns
    -------
    dict
        Stable strategy discovery result.
    """

    normalized_gap = _normalize_gap_result(
        gap_result
    )

    context = _extract_market_context(
        normalized_gap,
        market_context,
    )

    result = {
        "status": DISCOVERY_STATUS_NO_GAP,
        "gap_detected": normalized_gap[
            "gap_detected"
        ],
        "market_context": deepcopy(context),
        "candidates": [],
        "qualified_candidates": [],
        "rejected_candidates": [],
    }

    if not normalized_gap["gap_detected"]:
        return deepcopy(result)

    candidate = _build_candidate(
        context,
        normalized_gap,
    )

    result["candidates"].append(
        deepcopy(candidate)
    )

    if candidate["status"] == "QUALIFIED":
        result["qualified_candidates"].append(
            deepcopy(candidate)
        )
        result["status"] = (
            DISCOVERY_STATUS_DISCOVERED
        )
    else:
        result["rejected_candidates"].append(
            deepcopy(candidate)
        )
        result["status"] = (
            DISCOVERY_STATUS_NO_CANDIDATE
        )

    return deepcopy(result)


# Backward-friendly alias
discover_strategy = discover_strategies


class StrategyDiscoveryEngine:
    """
    Object-oriented wrapper for Strategy Discovery Engine.
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