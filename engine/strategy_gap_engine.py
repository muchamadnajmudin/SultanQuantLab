"""
==========================================
SULTAN QUANT OS
Strategy Gap Engine
Version : 1.0.0
==========================================

Responsibilities:

- Evaluate existing strategy performance
- Detect strategy gaps
- Identify weak market coverage
- Decide whether strategy discovery is required

This engine DOES NOT generate or modify strategies.

It only answers:

"Are the currently available strategies sufficient
for the current market condition?"
"""

from copy import deepcopy


STATUS_COVERED = "COVERED"
STATUS_WEAK = "WEAK"
STATUS_GAP = "GAP"
STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


REQUIRED_RESULT_KEYS = (
    "status",
    "discovery_required",
    "qualified_strategies",
    "weak_strategies",
    "reasons",
    "market_context",
)


def required_result_keys():
    """
    Return the stable Strategy Gap Engine result contract.
    """

    return REQUIRED_RESULT_KEYS


def _safe_dict(value):
    """
    Return a safe dictionary copy.
    """

    if not isinstance(value, dict):
        return {}

    return deepcopy(value)


def _safe_list(value):
    """
    Return a safe list.
    """

    if not isinstance(value, list):
        return []

    return deepcopy(value)


def _get_strategy_name(strategy, index):
    """
    Extract a stable strategy identifier.
    """

    if not isinstance(strategy, dict):
        return f"strategy_{index}"

    name = strategy.get("strategy")

    if not isinstance(name, str) or not name.strip():
        name = strategy.get("name")

    if not isinstance(name, str) or not name.strip():
        return f"strategy_{index}"

    return name


def _get_numeric_value(data, keys, default=None):
    """
    Return the first valid numeric value found.
    """

    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if isinstance(value, bool):
            continue

        if isinstance(value, (int, float)):
            return float(value)

    return default


def _strategy_is_qualified(
    strategy,
    minimum_score,
    minimum_confidence,
):
    """
    Determine whether a strategy is sufficiently qualified.

    Supported score fields:

    - score
    - adaptive_score
    - setup_score

    Supported confidence fields:

    - confidence
    - selection_confidence

    If confidence is not supplied, only score is evaluated.
    """

    if not isinstance(strategy, dict):
        return False, [
            "invalid_strategy"
        ]

    reasons = []

    score = _get_numeric_value(
        strategy,
        (
            "score",
            "adaptive_score",
            "setup_score",
        ),
    )

    confidence = _get_numeric_value(
        strategy,
        (
            "confidence",
            "selection_confidence",
        ),
    )

    if score is None:
        reasons.append("missing_score")

    elif score < minimum_score:
        reasons.append("score_below_threshold")

    if confidence is not None:

        if confidence < minimum_confidence:
            reasons.append(
                "confidence_below_threshold"
            )

    qualified = len(reasons) == 0

    return qualified, reasons


def evaluate_strategy_gap(
    strategies,
    market_context=None,
    minimum_score=0.0,
    minimum_confidence=0.0,
):
    """
    Evaluate whether existing strategies adequately
    cover the current market condition.

    Parameters
    ----------
    strategies : list
        List of evaluated strategy dictionaries.

    market_context : dict, optional
        Current market/regime context.

    minimum_score : float
        Minimum acceptable strategy score.

    minimum_confidence : float
        Minimum acceptable strategy confidence.

    Returns
    -------
    dict
        Stable Strategy Gap Engine contract.
    """

    safe_strategies = _safe_list(
        strategies
    )

    safe_market_context = _safe_dict(
        market_context
    )

    qualified_strategies = []
    weak_strategies = []
    reasons = []

    if not safe_strategies:

        return {
            "status": STATUS_INSUFFICIENT_DATA,
            "discovery_required": True,
            "qualified_strategies": [],
            "weak_strategies": [],
            "reasons": [
                "no_strategies_available"
            ],
            "market_context": safe_market_context,
        }

    for index, strategy in enumerate(
        safe_strategies
    ):

        strategy_name = _get_strategy_name(
            strategy,
            index,
        )

        qualified, strategy_reasons = (
            _strategy_is_qualified(
                strategy,
                minimum_score,
                minimum_confidence,
            )
        )

        result_item = {
            "strategy": strategy_name,
            "qualified": qualified,
            "reasons": strategy_reasons,
        }

        if qualified:

            qualified_strategies.append(
                result_item
            )

        else:

            weak_strategies.append(
                result_item
            )

    if qualified_strategies:

        if weak_strategies:

            status = STATUS_WEAK

            reasons.append(
                "partial_strategy_coverage"
            )

        else:

            status = STATUS_COVERED

            reasons.append(
                "sufficient_strategy_coverage"
            )

        discovery_required = False

    else:

        status = STATUS_GAP

        discovery_required = True

        reasons.append(
            "no_qualified_strategy"
        )

    return {
        "status": status,
        "discovery_required": discovery_required,
        "qualified_strategies": qualified_strategies,
        "weak_strategies": weak_strategies,
        "reasons": reasons,
        "market_context": safe_market_context,
    }


class StrategyGapEngine:
    """
    Object-oriented wrapper.

    Keeps the functional API available while allowing
    integration with the institutional pipeline.
    """

    def __init__(
        self,
        minimum_score=0.0,
        minimum_confidence=0.0,
    ):

        self.minimum_score = (
            minimum_score
        )

        self.minimum_confidence = (
            minimum_confidence
        )

    def evaluate(
        self,
        strategies,
        market_context=None,
    ):

        return evaluate_strategy_gap(
            strategies=strategies,
            market_context=market_context,
            minimum_score=self.minimum_score,
            minimum_confidence=(
                self.minimum_confidence
            ),
        )

    def run(
        self,
        strategies,
        market_context=None,
    ):

        return self.evaluate(
            strategies=strategies,
            market_context=market_context,
        )


def analyze_strategy_gap(
    strategies,
    market_context=None,
    minimum_score=0.0,
    minimum_confidence=0.0,
):
    """
    Backward-friendly functional alias.
    """

    return evaluate_strategy_gap(
        strategies=strategies,
        market_context=market_context,
        minimum_score=minimum_score,
        minimum_confidence=minimum_confidence,
    )