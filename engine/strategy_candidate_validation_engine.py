"""
==========================================
SULTAN QUANT OS
Strategy Candidate Validation Engine
Version : 1.3.0
==========================================

Responsibilities:

- Validate strategy candidate structure
- Validate strategy score
- Validate confidence
- Validate sample or trade count
- Support embedded evaluation data
- Support explicit evaluation overrides
- Preserve input immutability
- Produce a stable validation contract

Validation outcomes:

QUALIFIED
    Candidate passed all validation rules.

REJECTED
    Candidate is structurally invalid or
    available metrics failed the required
    thresholds.

INSUFFICIENT_DATA
    Required validation data is missing.

Important distinction:

Missing sample data:
    INSUFFICIENT_DATA

Sample data exists but is below minimum:
    REJECTED

The Strategy Lifecycle Engine may interpret
an insufficient_sample_count rejection as
HOLD according to lifecycle policy.
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
    Return the stable Strategy Candidate
    Validation result contract.
    """

    return REQUIRED_RESULT_KEYS


def _safe_dict(value):
    """
    Return an independent dictionary copy.

    Non-dictionary values return an empty
    dictionary.
    """

    if not isinstance(value, dict):
        return {}

    return deepcopy(value)


def _safe_number(value):
    """
    Return a numeric value safely.

    Boolean values are not treated as numbers.
    Invalid values return None.
    """

    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)):
        return value

    return None


def _get_numeric_value(
    source,
    keys,
):
    """
    Resolve the first valid numeric value from
    a dictionary using a list of supported keys.
    """

    if not isinstance(source, dict):
        return None

    for key in keys:

        if key not in source:
            continue

        value = _safe_number(
            source.get(key)
        )

        if value is not None:
            return value

    return None


def _merge_evaluation(
    candidate,
    evaluation,
):
    """
    Merge candidate embedded evaluation with
    explicit evaluation.

    Explicit evaluation has priority.

    The returned dictionary is independent from
    both input objects.
    """

    merged = {}

    if isinstance(candidate, dict):

        embedded_evaluation = candidate.get(
            "evaluation"
        )

        if isinstance(
            embedded_evaluation,
            dict,
        ):

            merged.update(
                deepcopy(
                    embedded_evaluation
                )
            )

    if isinstance(evaluation, dict):

        merged.update(
            deepcopy(
                evaluation
            )
        )

    return merged


def _validate_candidate_structure(
    candidate,
):
    """
    Validate the minimum candidate structure.

    Supported candidate identifiers:

    - strategy
    - name
    - candidate
    """

    if not isinstance(candidate, dict):

        return (
            False,
            [
                "invalid_candidate",
            ],
        )

    identifier_keys = (
        "strategy",
        "name",
        "candidate",
    )

    for key in identifier_keys:

        value = candidate.get(
            key
        )

        if isinstance(value, str):

            if value.strip():

                return (
                    True,
                    [],
                )

    return (
        False,
        [
            "missing_candidate_name",
        ],
    )


def _resolve_score(
    candidate,
    evaluation,
):
    """
    Resolve score.

    Evaluation data has priority over the
    candidate itself.
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
    Resolve confidence.

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
    Resolve trade or sample count.

    Evaluation data has priority.
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


def _build_result(
    status,
    qualified,
    promotion_allowed,
    candidate,
    reasons,
    evaluation,
):
    """
    Build a stable independent validation result.
    """

    return {
        "status": status,
        "qualified": bool(
            qualified
        ),
        "promotion_allowed": bool(
            promotion_allowed
        ),
        "candidate": _safe_dict(
            candidate
        ),
        "reasons": deepcopy(
            list(reasons)
            if isinstance(
                reasons,
                list,
            )
            else []
        ),
        "evaluation": _safe_dict(
            evaluation
        ),
    }


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
        Strategy candidate.

    evaluation : dict, optional
        Validation or backtest metrics.

        Explicit evaluation data has priority.

    minimum_score : float
        Minimum acceptable score.

    minimum_confidence : float
        Minimum acceptable confidence.

    minimum_samples : int
        Minimum required trade or sample count.

    Returns
    -------
    dict
        Stable Strategy Candidate Validation
        result contract.
    """

    candidate_is_valid_type = isinstance(
        candidate,
        dict,
    )

    safe_candidate = _safe_dict(
        candidate
    )

    safe_evaluation = _merge_evaluation(
        candidate
        if candidate_is_valid_type
        else {},
        evaluation,
    )

    if not candidate_is_valid_type:

        return _build_result(
            status=STATUS_REJECTED,
            qualified=False,
            promotion_allowed=False,
            candidate=safe_candidate,
            reasons=[
                "invalid_candidate",
            ],
            evaluation=safe_evaluation,
        )

    structure_valid, structure_reasons = (
        _validate_candidate_structure(
            safe_candidate
        )
    )

    reasons = list(
        structure_reasons
    )

    if not structure_valid:

        return _build_result(
            status=STATUS_REJECTED,
            qualified=False,
            promotion_allowed=False,
            candidate=safe_candidate,
            reasons=reasons,
            evaluation=safe_evaluation,
        )

    minimum_score_value = _safe_number(
        minimum_score
    )

    if minimum_score_value is None:

        minimum_score_value = 0.0

    minimum_confidence_value = _safe_number(
        minimum_confidence
    )

    if minimum_confidence_value is None:

        minimum_confidence_value = 0.0

    minimum_samples_value = _safe_number(
        minimum_samples
    )

    if minimum_samples_value is None:

        minimum_samples_value = 0

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

    #
    # SCORE VALIDATION
    #

    if score is None:

        missing_data = True

        reasons.append(
            "missing_score"
        )

    elif score < minimum_score_value:

        rejection_reasons.append(
            "score_below_threshold"
        )

    #
    # CONFIDENCE VALIDATION
    #

    if confidence is None:

        if minimum_confidence_value > 0:

            missing_data = True

            reasons.append(
                "missing_confidence"
            )

    elif confidence < minimum_confidence_value:

        rejection_reasons.append(
            "confidence_below_threshold"
        )

    #
    # SAMPLE VALIDATION
    #
    # Important contract:
    #
    # Missing sample count:
    #     INSUFFICIENT_DATA
    #
    # Sample count exists but is below threshold:
    #     REJECTED
    #

    if minimum_samples_value > 0:

        if sample_count is None:

            missing_data = True

            reasons.append(
                "missing_sample_count"
            )

        elif sample_count < minimum_samples_value:

            rejection_reasons.append(
                "insufficient_sample_count"
            )

    #
    # MISSING REQUIRED DATA
    #

    if missing_data:

        return _build_result(
            status=STATUS_INSUFFICIENT_DATA,
            qualified=False,
            promotion_allowed=False,
            candidate=safe_candidate,
            reasons=reasons,
            evaluation=safe_evaluation,
        )

    #
    # AVAILABLE DATA FAILED VALIDATION
    #

    if rejection_reasons:

        reasons.extend(
            rejection_reasons
        )

        return _build_result(
            status=STATUS_REJECTED,
            qualified=False,
            promotion_allowed=False,
            candidate=safe_candidate,
            reasons=reasons,
            evaluation=safe_evaluation,
        )

    #
    # QUALIFIED
    #

    return _build_result(
        status=STATUS_QUALIFIED,
        qualified=True,
        promotion_allowed=True,
        candidate=safe_candidate,
        reasons=[
            "candidate_qualified",
        ],
        evaluation=safe_evaluation,
    )


def analyze_strategy_candidate(
    candidate,
    evaluation=None,
    minimum_score=0.0,
    minimum_confidence=0.0,
    minimum_samples=0,
):
    """
    Functional alias for
    validate_strategy_candidate().
    """

    return validate_strategy_candidate(
        candidate=candidate,
        evaluation=evaluation,
        minimum_score=minimum_score,
        minimum_confidence=minimum_confidence,
        minimum_samples=minimum_samples,
    )


class StrategyCandidateValidationEngine:
    """
    Object-oriented wrapper for the
    Strategy Candidate Validation Engine.
    """

    def __init__(
        self,
        minimum_score=0.0,
        minimum_confidence=0.0,
        minimum_samples=0,
    ):

        safe_minimum_score = _safe_number(
            minimum_score
        )

        safe_minimum_confidence = _safe_number(
            minimum_confidence
        )

        safe_minimum_samples = _safe_number(
            minimum_samples
        )

        self.minimum_score = (
            safe_minimum_score
            if safe_minimum_score is not None
            else 0.0
        )

        self.minimum_confidence = (
            safe_minimum_confidence
            if safe_minimum_confidence is not None
            else 0.0
        )

        self.minimum_samples = (
            safe_minimum_samples
            if safe_minimum_samples is not None
            else 0
        )

    def validate(
        self,
        candidate,
        evaluation=None,
    ):
        """
        Validate a strategy candidate using
        configured thresholds.
        """

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
        """
        Alias for validate().
        """

        return self.validate(
            candidate=candidate,
            evaluation=evaluation,
        )