"""
==========================================
SULTAN QUANT OS
Module : Grid Strategy Ranker
Version: 1.0.0
==========================================

Responsibilities
----------------
- Rank grid strategy analysis results.
- Combine performance and risk metrics.
- Produce deterministic strategy scores.
- Preserve original input data.
- Support partial failures.
- Preserve backward-compatible run/process/execute APIs.

Design
------
This module is analysis/ranking only.

It does NOT:
- execute trades
- modify grid plans
- modify simulations
- connect to exchanges
- fetch market data
"""

from __future__ import annotations

from copy import deepcopy
from numbers import Real
from typing import Any, Dict, Iterable, List, Tuple


VERSION = "1.0.0"

DEFAULT_PERFORMANCE_WEIGHT = 0.60
DEFAULT_RISK_WEIGHT = 0.40

REQUIRED_RESULT_KEYS = {
    "success",
    "processed_count",
    "valid_count",
    "invalid_count",
    "ranked_strategies",
    "selected_strategies",
    "invalid_strategies",
    "errors",
}

REQUIRED_STRATEGY_KEYS = {
    "rank",
    "symbol",
    "score",
    "performance_score",
    "risk_score",
    "performance",
    "risk",
    "analysis",
}


# ============================================================
# VALIDATION HELPERS
# ============================================================

def _is_number(value: Any) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _normalize_symbol(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    return value.strip().upper()


def _safe_float(value: Any, default: float = 0.0) -> float:
    if _is_number(value):
        return float(value)

    return default


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


# ============================================================
# METRIC EXTRACTION
# ============================================================

def _extract_analysis(simulation: Dict[str, Any]) -> Dict[str, Any]:
    analysis = simulation.get("analysis")

    if isinstance(analysis, dict):
        return deepcopy(analysis)

    return {}


def _extract_performance(simulation: Dict[str, Any]) -> Dict[str, Any]:
    performance = simulation.get("performance")

    if isinstance(performance, dict):
        return deepcopy(performance)

    analysis = simulation.get("analysis")

    if isinstance(analysis, dict):
        nested = analysis.get("performance")

        if isinstance(nested, dict):
            return deepcopy(nested)

    return {}


def _extract_risk(simulation: Dict[str, Any]) -> Dict[str, Any]:
    risk = simulation.get("risk")

    if isinstance(risk, dict):
        return deepcopy(risk)

    analysis = simulation.get("analysis")

    if isinstance(analysis, dict):
        nested = analysis.get("risk")

        if isinstance(nested, dict):
            return deepcopy(nested)

    return {}


# ============================================================
# PERFORMANCE SCORE
# ============================================================

def _calculate_performance_score(
    performance: Dict[str, Any],
) -> float:
    """
    Convert performance metrics into a normalized 0..1 score.

    Primary metrics:
    - total_return
    - realized_return
    - completion_rate
    - profit_per_completed_layer
    """

    total_return = _safe_float(
        performance.get("total_return")
    )

    realized_return = _safe_float(
        performance.get("realized_return")
    )

    completion_rate = _safe_float(
        performance.get("completion_rate")
    )

    profit_per_completed_layer = _safe_float(
        performance.get("profit_per_completed_layer")
    )

    if completion_rate > 1.0:
        completion_rate /= 100.0

    completion_rate = _clamp(completion_rate)

    # Returns are normalized conservatively.
    #
    # 100% return => full contribution.
    # Negative return => zero contribution.
    total_return_score = _clamp(
        total_return / 100.0
    )

    realized_return_score = _clamp(
        realized_return / 100.0
    )

    # Profit per completed layer is converted into a
    # bounded contribution. Positive profit contributes.
    profit_layer_score = _clamp(
        profit_per_completed_layer / 100.0
    )

    score = (
        total_return_score * 0.40
        + realized_return_score * 0.30
        + completion_rate * 0.20
        + profit_layer_score * 0.10
    )

    return round(
        _clamp(score) * 100.0,
        10,
    )


# ============================================================
# RISK SCORE
# ============================================================

def _calculate_risk_score(
    risk: Dict[str, Any],
) -> float:
    """
    Convert risk metrics into a normalized 0..100 score.

    IMPORTANT:
    Higher risk produces a lower score.
    Therefore this is a risk-adjusted quality score,
    not raw exposure.
    """

    raw_risk_score = risk.get("risk_score")

    if _is_number(raw_risk_score):
        value = float(raw_risk_score)

        if value <= 1.0:
            value *= 100.0

        return round(
            100.0 - _clamp(value, 0.0, 100.0),
            10,
        )

    exposure_ratio = _safe_float(
        risk.get("capital_exposure_ratio")
    )

    utilization = _safe_float(
        risk.get("capital_utilization")
    )

    if exposure_ratio > 1.0:
        exposure_ratio /= 100.0

    if utilization > 1.0:
        utilization /= 100.0

    exposure_ratio = _clamp(exposure_ratio)
    utilization = _clamp(utilization)

    risk_penalty = (
        exposure_ratio * 0.60
        + utilization * 0.40
    )

    return round(
        (1.0 - risk_penalty) * 100.0,
        10,
    )


# ============================================================
# STRATEGY SCORE
# ============================================================

def _calculate_strategy_score(
    performance_score: float,
    risk_score: float,
    performance_weight: float,
    risk_weight: float,
) -> float:
    score = (
        performance_score * performance_weight
        + risk_score * risk_weight
    )

    return round(
        _clamp(score, 0.0, 100.0),
        10,
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

def _validate_strategy(
    strategy: Any,
    index: int,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    if not isinstance(strategy, dict):
        return (
            False,
            [
                f"Strategy at index {index} must be a dictionary."
            ],
        )

    symbol = strategy.get("symbol")

    if not isinstance(symbol, str):
        errors.append(
            f"Strategy at index {index} has invalid symbol."
        )
    elif not symbol.strip():
        errors.append(
            f"Strategy at index {index} has empty symbol."
        )

    performance = _extract_performance(strategy)

    if not isinstance(performance, dict):
        errors.append(
            f"Strategy at index {index} has invalid performance."
        )

    risk = _extract_risk(strategy)

    if not isinstance(risk, dict):
        errors.append(
            f"Strategy at index {index} has invalid risk."
        )

    return (
        len(errors) == 0,
        errors,
    )


# ============================================================
# SORTING
# ============================================================

def _ranking_key(strategy: Dict[str, Any]):
    """
    Deterministic ranking.

    Priority:
    1. overall score
    2. performance score
    3. risk score
    4. completion rate
    5. symbol
    """

    performance = strategy.get("performance", {})

    completion_rate = _safe_float(
        performance.get("completion_rate")
    )

    return (
        -_safe_float(strategy.get("score")),
        -_safe_float(strategy.get("performance_score")),
        -_safe_float(strategy.get("risk_score")),
        -completion_rate,
        str(strategy.get("symbol", "")),
    )


# ============================================================
# MAIN FUNCTION
# ============================================================

def rank_grid_strategies(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = None,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    """
    Rank grid strategy simulations.

    Parameters
    ----------
    simulations:
        Iterable of simulation/analysis dictionaries.

    top_n:
        Maximum number of selected strategies.
        None selects all valid strategies.

    performance_weight:
        Weight applied to performance score.

    risk_weight:
        Weight applied to risk score.
    """

    original_input = deepcopy(simulations)

    result: Dict[str, Any] = {
        "success": True,
        "processed_count": 0,
        "valid_count": 0,
        "invalid_count": 0,
        "ranked_strategies": [],
        "selected_strategies": [],
        "invalid_strategies": [],
        "errors": [],
    }

    # --------------------------------------------------------
    # INPUT CONTAINER
    # --------------------------------------------------------

    if simulations is None:
        return result

    if isinstance(simulations, (str, bytes)):
        result["success"] = False
        result["errors"].append(
            "Simulations must be a list, tuple, or iterable."
        )
        return result

    try:
        items = list(simulations)
    except (TypeError, ValueError):
        result["success"] = False
        result["errors"].append(
            "Simulations must be an iterable collection."
        )
        return result

    # --------------------------------------------------------
    # WEIGHTS
    # --------------------------------------------------------

    if not _is_number(performance_weight):
        result["success"] = False
        result["errors"].append(
            "Performance weight must be numeric."
        )
        return result

    if not _is_number(risk_weight):
        result["success"] = False
        result["errors"].append(
            "Risk weight must be numeric."
        )
        return result

    performance_weight = float(performance_weight)
    risk_weight = float(risk_weight)

    if performance_weight < 0:
        result["success"] = False
        result["errors"].append(
            "Performance weight must not be negative."
        )
        return result

    if risk_weight < 0:
        result["success"] = False
        result["errors"].append(
            "Risk weight must not be negative."
        )
        return result

    weight_total = (
        performance_weight
        + risk_weight
    )

    if weight_total <= 0:
        result["success"] = False
        result["errors"].append(
            "Performance and risk weights must have a positive total."
        )
        return result

    # Normalize weights.
    performance_weight /= weight_total
    risk_weight /= weight_total

    # --------------------------------------------------------
    # TOP N
    # --------------------------------------------------------

    if top_n is not None:

        if isinstance(top_n, bool):
            result["success"] = False
            result["errors"].append(
                "top_n must be an integer."
            )
            return result

        if not isinstance(top_n, int):
            result["success"] = False
            result["errors"].append(
                "top_n must be an integer."
            )
            return result

        if top_n < 1:
            result["success"] = False
            result["errors"].append(
                "top_n must be greater than zero."
            )
            return result

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    for index, simulation in enumerate(items):

        result["processed_count"] += 1

        valid, validation_errors = _validate_strategy(
            simulation,
            index,
        )

        if not valid:

            result["invalid_count"] += 1

            invalid_entry = {
                "index": index,
                "strategy": deepcopy(simulation),
                "errors": list(validation_errors),
            }

            result["invalid_strategies"].append(
                invalid_entry
            )

            result["errors"].extend(
                validation_errors
            )

            continue

        try:

            symbol = _normalize_symbol(
                simulation.get("symbol")
            )

            performance = _extract_performance(
                simulation
            )

            risk = _extract_risk(
                simulation
            )

            analysis = _extract_analysis(
                simulation
            )

            performance_score = (
                _calculate_performance_score(
                    performance
                )
            )

            risk_score = (
                _calculate_risk_score(
                    risk
                )
            )

            score = _calculate_strategy_score(
                performance_score,
                risk_score,
                performance_weight,
                risk_weight,
            )

            ranked_strategy = {
                "rank": 0,
                "symbol": symbol,
                "score": score,
                "performance_score": performance_score,
                "risk_score": risk_score,
                "performance": deepcopy(performance),
                "risk": deepcopy(risk),
                "analysis": deepcopy(analysis),
            }

            result["ranked_strategies"].append(
                ranked_strategy
            )

            result["valid_count"] += 1

        except Exception as exc:

            result["invalid_count"] += 1

            error_message = (
                f"Strategy at index {index} failed during ranking: "
                f"{exc}"
            )

            result["errors"].append(
                error_message
            )

            result["invalid_strategies"].append(
                {
                    "index": index,
                    "strategy": deepcopy(simulation),
                    "errors": [error_message],
                }
            )

    # --------------------------------------------------------
    # RANK
    # --------------------------------------------------------

    ranked = sorted(
        result["ranked_strategies"],
        key=_ranking_key,
    )

    for rank, strategy in enumerate(
        ranked,
        start=1,
    ):
        strategy["rank"] = rank

    result["ranked_strategies"] = ranked

    # --------------------------------------------------------
    # SELECT
    # --------------------------------------------------------

    if top_n is None:
        selected = ranked
    else:
        selected = ranked[:top_n]

    result["selected_strategies"] = deepcopy(
        selected
    )

    # --------------------------------------------------------
    # FINAL STATUS
    # --------------------------------------------------------

    if result["invalid_count"] > 0:
        result["success"] = (
            result["valid_count"] > 0
        )

    # Preserve an independent snapshot of the
    # original input for downstream diagnostics.
    result["input"] = deepcopy(
        original_input
    )

    return result


# ============================================================
# ALIASES
# ============================================================

def process_grid_strategy_rankings(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = None,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    return rank_grid_strategies(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


def execute_grid_strategy_rankings(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = None,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    return rank_grid_strategies(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


# ============================================================
# ENGINE WRAPPER
# ============================================================

class GridStrategyRanker:
    """
    Object-oriented wrapper for Grid Strategy Ranker.
    """

    def __init__(
        self,
        performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
        risk_weight: float = DEFAULT_RISK_WEIGHT,
        top_n: int | None = None,
    ) -> None:

        self.performance_weight = (
            performance_weight
        )

        self.risk_weight = (
            risk_weight
        )

        self.top_n = top_n

    def run(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:

        effective_top_n = (
            self.top_n
            if top_n is None
            else top_n
        )

        return rank_grid_strategies(
            simulations,
            top_n=effective_top_n,
            performance_weight=self.performance_weight,
            risk_weight=self.risk_weight,
        )

    def process(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:

        return self.run(
            simulations,
            top_n=top_n,
        )

    def execute(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:

        return self.run(
            simulations,
            top_n=top_n,
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def rank_grid_strategies_function(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = None,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:

    return rank_grid_strategies(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [
    "VERSION",
    "DEFAULT_PERFORMANCE_WEIGHT",
    "DEFAULT_RISK_WEIGHT",
    "REQUIRED_RESULT_KEYS",
    "REQUIRED_STRATEGY_KEYS",
    "rank_grid_strategies",
    "process_grid_strategy_rankings",
    "execute_grid_strategy_rankings",
    "rank_grid_strategies_function",
    "GridStrategyRanker",
]