"""
==========================================
SULTAN QUANT OS
Strategy Candidate Validation Engine
Version : 1.0.0
==========================================

Responsibilities:

- Validate discovered strategy candidates
- Check candidate structure
- Evaluate score and confidence thresholds
- Evaluate optional evaluation/backtest data
- Decide whether a candidate is qualified
- Decide whether more data is required

This engine DOES NOT:

- Generate strategies
- Modify strategies
- Promote strategies to the registry
- Execute trades

It only answers:

"Is this strategy candidate sufficiently qualified
to proceed to the promotion stage?"
"""

from copy import deepcopy


STATUS_QUALIFIED = "QUALIFIED"
STATUS_REJECTED = "REJECTED"
STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


REQUIRED_RESULT_KEYS = (
    "status",
    "qualified",
    "promotion_allowed",
    "candidate",
    "reasons",
    "evaluation",
)


def required_result_keys():
    """
    Return the stable Strategy Candidate Validation
    Engine result contract.
    """

    return REQUIRED_RESULT_KEYS


def _safe_dict(value):
    """
    Return a safe independent dictionary copy.
    """

    if not isinstance(value, dict):
        return {}

    return deepcopy(value)


def _safe_list(value):
    """
    Return a safe independent list copy.
    """

    if not isinstance(value, list):
        return []

    return deepcopy(value)


def _get_numeric_value(
    data,
    keys,
    default=None,
):
    """
    Return the first valid numeric value found.

    Boolean values are not accepted as numeric values.
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


def _merge_evaluation(
    candidate,
    evaluation,
):
    """
    Build a safe evaluation context.

    Explicit evaluation data overrides values from
    the candidate.
    """

    merged = {}

    if isinstance(candidate, dict):

        candidate_evaluation = (
            candidate.get("evaluation")
        )

        if isinstance(candidate_evaluation, dict):

            merged.update(
                deepcopy(candidate_evaluation)
            )

    if isinstance(evaluation, dict):

        merged.update(
            deepcopy(evaluation)
        )

    return merged


def _candidate_name(candidate):
    """
    Extract a stable candidate identifier.
    """

    if not isinstance(candidate, dict):
        return ""

    name = candidate.get("strategy")

    if not isinstance(name, str) or not name.strip():

        name = candidate.get("name")

    if not isinstance(name, str) or not name.strip():

        name = candidate.get(
            "candidate"
        )

    if not isinstance(name, str):

        return ""

    return name.strip()


def _validate_candidate_structure(
    candidate,
):
    """
    Validate the minimum candidate structure.

    A valid candidate requires a stable identifier.
    """

    reasons = []

    if not isinstance(candidate, dict):

        return False, [
            "invalid_candidate"
        ]

    name = _candidate_name(candidate)

    if not name:

        reasons.append(
            "missing_candidate_name"
        )

    valid = len(reasons) == 0

    return valid, reasons


def _resolve_score(
    candidate,
    evaluation,
):
    """
    Resolve score from candidate and evaluation data.

    Evaluation data has priority because it represents
    the latest validation result.
    """

    score = _get_numeric_value(
        evaluation,
        (
            "score",
            "adaptive_score",
            "setup_score",
        ),
    )

    if score is not None:

        return score

    return _get_numeric_value(
        candidate,
        (
            "score",
            "adaptive_score",
            "setup_score",
        ),
    )


def _resolve_confidence(
    candidate,
    evaluation,
):
    """
    Resolve confidence from candidate and evaluation data.

    Evaluation data has priority.
    """

    confidence = _get_numeric_value(
        evaluation,
        (
            "confidence",
            "selection_confidence",
        ),
    )

    if confidence is not None:

        return confidence

    return _get_numeric_value(
        candidate,
        (
            "confidence",
            "selection_confidence",
        ),
    )


def _resolve_trade_count(
    candidate,
    evaluation,
):
    """
    Resolve optional trade/sample count.

    This is used when minimum_samples is required.
    """

    sample_count = _get_numeric_value(
        evaluation,
        (
            "trade_count",
            "trades",
            "sample_count",
            "samples",
        ),
    )

    if sample_count is not None:

        return sample_count

    return _get_numeric_value(
        candidate,
        (
            "trade_count",
            "trades",
            "sample_count",
            "samples",
        ),
    )


def validate_strategy_candidate(
    candidate,
    evaluation=None,
    minimum_score=0.0,
    minimum_confidence=0.0,
    minimum_samples=0,
):
    """
    Validate a discovered strategy candidate.

    Parameters
    ----------
    candidate : dict
        Strategy candidate generated by the discovery
        stage.

    evaluation : dict, optional
        Validation or backtest metrics.

        Explicit evaluation data takes priority over
        candidate evaluation data.

    minimum_score : float
        Minimum acceptable score.

    minimum_confidence : float
        Minimum acceptable confidence.

    minimum_samples : int
        Minimum required trade/sample count.

        If greater than zero and sample data is missing,
        the result becomes INSUFFICIENT_DATA.

    Returns
    -------
    dict
        Stable Strategy Candidate Validation contract.
    """

    candidate_is_valid_type = isinstance(
        candidate,
        dict,
    )

    safe_candidate = _safe_dict(
        candidate
    )

    safe_evaluation = _merge_evaluation(
        candidate if candidate_is_valid_type else {},
        evaluation,
    )

    if not candidate_is_valid_type:

        return {
            "status": STATUS_REJECTED,
            "qualified": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": [
                "invalid_candidate"
            ],
            "evaluation": safe_evaluation,
        }

    structure_valid, structure_reasons = (
        _validate_candidate_structure(
            safe_candidate
        )
    )

    reasons = list(
        structure_reasons
    )

    if not structure_valid:

        return {
            "status": STATUS_REJECTED,
            "qualified": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": reasons,
            "evaluation": safe_evaluation,
        }

    score = _resolve_score(
        safe_candidate,
        safe_evaluation,
    )

    confidence = _resolve_confidence(
        safe_candidate,
        safe_evaluation,
    )

    sample_count = _resolve_trade_count(
        safe_candidate,
        safe_evaluation,
    )

    missing_data = False
    rejection_reasons = []

    if score is None:

        missing_data = True

        reasons.append(
            "missing_score"
        )

    elif score < minimum_score:

        rejection_reasons.append(
            "score_below_threshold"
        )

    if confidence is None:

        if minimum_confidence > 0:

            missing_data = True

            reasons.append(
                "missing_confidence"
            )

    elif confidence < minimum_confidence:

        rejection_reasons.append(
            "confidence_below_threshold"
        )

    if minimum_samples > 0:

        if sample_count is None:

            missing_data = True

            reasons.append(
                "missing_sample_count"
            )

        elif sample_count < minimum_samples:

            rejection_reasons.append(
                "insufficient_sample_count"
            )

    if missing_data:

        return {
            "status": STATUS_INSUFFICIENT_DATA,
            "qualified": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": reasons,
            "evaluation": safe_evaluation,
        }

    if rejection_reasons:

        reasons.extend(
            rejection_reasons
        )

        return {
            "status": STATUS_REJECTED,
            "qualified": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": reasons,
            "evaluation": safe_evaluation,
        }

    return {
        "status": STATUS_QUALIFIED,
        "qualified": True,
        "promotion_allowed": True,
        "candidate": safe_candidate,
        "reasons": [
            "candidate_qualified"
        ],
        "evaluation": safe_evaluation,
    }


class StrategyCandidateValidationEngine:
    """
    Object-oriented wrapper.

    Keeps the functional API available while allowing
    integration with the institutional pipeline.
    """

    def __init__(
        self,
        minimum_score=0.0,
        minimum_confidence=0.0,
        minimum_samples=0,
    ):

        self.minimum_score = (
            minimum_score
        )

        self.minimum_confidence = (
            minimum_confidence
        )

        self.minimum_samples = (
            minimum_samples
        )

    def validate(
        self,
        candidate,
        evaluation=None,
    ):

        return validate_strategy_candidate(
            candidate=candidate,
            evaluation=evaluation,
            minimum_score=self.minimum_score,
            minimum_confidence=(
                self.minimum_confidence
            ),
            minimum_samples=(
                self.minimum_samples
            ),
        )

    def run(
        self,
        candidate,
        evaluation=None,
    ):

        return self.validate(
            candidate=candidate,
            evaluation=evaluation,
        )


def analyze_strategy_candidate(
    candidate,
    evaluation=None,
    minimum_score=0.0,
    minimum_confidence=0.0,
    minimum_samples=0,
):
    """
    Backward-friendly functional alias.
    """

    return validate_strategy_candidate(
        candidate=candidate,
        evaluation=evaluation,
        minimum_score=minimum_score,
        minimum_confidence=minimum_confidence,
        minimum_samples=minimum_samples,
    )