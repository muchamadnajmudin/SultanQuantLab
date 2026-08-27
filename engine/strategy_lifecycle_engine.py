"""
==========================================
SULTAN QUANT OS
Strategy Lifecycle Engine
Version : 1.2.2
==========================================

Responsibilities:

- Coordinate the lifecycle of a strategy candidate
- Preserve candidate data safely
- Forward evaluation data to validation
- Validate strategy candidates
- Promote qualified candidates
- Hold candidates with insufficient data
- Reject invalid or failed candidates
- Produce a stable lifecycle contract

Lifecycle:

DISCOVERED
    ->
VALIDATING
    ->
QUALIFIED
    ->
PROMOTED

or

DISCOVERED
    ->
VALIDATING
    ->
HOLD

or

DISCOVERED
    ->
VALIDATING
    ->
REJECTED

This engine coordinates:

Strategy Candidate
        ->
Strategy Candidate Validation Engine
        ->
Strategy Promotion Engine

This engine DOES NOT:

- Generate strategies
- Modify strategy registry
- Execute backtests
- Execute live trades
- Manage portfolio allocation

The StrategyLifecycleEngine operates at the
individual strategy candidate level.

PortfolioLifecycleEngine operates at the
portfolio level.

Therefore both engines have different
responsibilities and should not conflict.
"""

from copy import deepcopy

from engine.strategy_candidate_validation_engine import (
    validate_strategy_candidate,
)

from engine.strategy_promotion_engine import (
    promote_strategy_candidate,
)


STATUS_DISCOVERED = "DISCOVERED"
STATUS_VALIDATING = "VALIDATING"
STATUS_QUALIFIED = "QUALIFIED"
STATUS_PROMOTED = "PROMOTED"
STATUS_HOLD = "HOLD"
STATUS_REJECTED = "REJECTED"

STATUS_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


REQUIRED_RESULT_KEYS = (
    "status",
    "candidate",
    "evaluation",
    "validation",
    "promotion",
    "reasons",
    "state_history",
)


def required_result_keys():
    """
    Return the stable Strategy Lifecycle
    Engine result contract.
    """

    return REQUIRED_RESULT_KEYS


def _safe_dict(value):
    """
    Return a safe independent dictionary copy.

    Non-dictionary values return an empty
    dictionary.
    """

    if not isinstance(value, dict):
        return {}

    return deepcopy(value)


def _safe_list(value):
    """
    Return a safe independent list copy.

    Non-list values return an empty list.
    """

    if not isinstance(value, list):
        return []

    return deepcopy(value)


def _safe_number(value, default=0.0):
    """
    Convert numeric values safely.

    Boolean values are not treated as numbers.
    """

    if isinstance(value, bool):
        return default

    if isinstance(value, (int, float)):
        return value

    return default


def _normalized_status(value):
    """
    Normalize a status value safely.
    """

    if not isinstance(value, str):
        return ""

    return value.strip().upper()


def _validation_has_reason(
    validation,
    expected_reason,
):
    """
    Return True when validation contains
    the specified reason.
    """

    if not isinstance(validation, dict):
        return False

    reasons = validation.get(
        "reasons"
    )

    if not isinstance(reasons, list):
        return False

    return expected_reason in reasons


def _build_result(
    status,
    candidate,
    evaluation,
    validation,
    promotion,
    reasons,
    state_history,
):
    """
    Build a stable lifecycle result.

    All nested structures are copied so that
    callers cannot mutate the original inputs
    through the returned result.
    """

    return {
        "status": status,
        "candidate": _safe_dict(candidate),
        "evaluation": _safe_dict(evaluation),
        "validation": _safe_dict(validation),
        "promotion": _safe_dict(promotion),
        "reasons": _safe_list(reasons),
        "state_history": _safe_list(state_history),
    }


def _invalid_candidate_result(
    candidate,
    evaluation,
):
    """
    Build a rejected lifecycle result for an
    invalid candidate.
    """

    validation = {
        "status": STATUS_REJECTED,
        "qualified": False,
        "promotion_allowed": False,
        "candidate": _safe_dict(candidate),
        "evaluation": _safe_dict(evaluation),
        "reasons": [
            "invalid_candidate",
        ],
    }

    promotion = {
        "status": STATUS_REJECTED,
        "promoted": False,
        "promotion_allowed": False,
        "candidate": _safe_dict(candidate),
        "reasons": [
            "candidate_rejected",
            "invalid_candidate",
        ],
        "validation": _safe_dict(validation),
    }

    return _build_result(
        status=STATUS_REJECTED,
        candidate=candidate,
        evaluation=evaluation,
        validation=validation,
        promotion=promotion,
        reasons=[
            "invalid_candidate",
        ],
        state_history=[
            STATUS_DISCOVERED,
            STATUS_VALIDATING,
            STATUS_REJECTED,
        ],
    )


def _resolve_final_reasons(
    validation,
    promotion,
):
    """
    Resolve lifecycle reasons.

    Validation reasons are processed first because
    validation determines whether a candidate is
    qualified, insufficient, or rejected.

    Promotion reasons are appended without
    duplicate values.
    """

    reasons = []

    if isinstance(validation, dict):

        validation_reasons = (
            validation.get("reasons")
        )

        if isinstance(validation_reasons, list):

            for reason in validation_reasons:

                if reason not in reasons:

                    reasons.append(
                        deepcopy(reason)
                    )

    if isinstance(promotion, dict):

        promotion_reasons = (
            promotion.get("reasons")
        )

        if isinstance(promotion_reasons, list):

            for reason in promotion_reasons:

                if reason not in reasons:

                    reasons.append(
                        deepcopy(reason)
                    )

    return reasons


def _is_hold_validation_result(
    validation,
):
    """
    Determine whether a validation result should
    enter the HOLD lifecycle state.

    HOLD is used for candidates that may become
    valid after more data is collected.

    Cases:

    - Validation returns INSUFFICIENT_DATA
    - Validation rejects only because the sample
      count is below the required minimum

    A low sample count is not treated as a
    permanently invalid strategy at the lifecycle
    level. The candidate should be held until more
    samples are available.
    """

    validation_status = ""

    if isinstance(validation, dict):

        validation_status = _normalized_status(
            validation.get("status")
        )

    if validation_status == STATUS_INSUFFICIENT_DATA:

        return True

    if validation_status != STATUS_REJECTED:

        return False

    if _validation_has_reason(
        validation,
        "insufficient_sample_count",
    ):
        return True

    return False


def _resolve_final_status(
    validation,
    promotion,
):
    """
    Resolve the final lifecycle status.

    Validation is the authority for deciding
    whether the candidate is:

    - QUALIFIED
    - INSUFFICIENT_DATA
    - REJECTED

    Lifecycle adds one additional semantic rule:

    A candidate rejected only because its sample
    count is insufficient is placed into HOLD.

    This allows the validation engine to preserve
    its own contract while the lifecycle engine
    treats insufficient historical evidence as a
    temporary state rather than a permanent
    rejection.
    """

    validation_status = ""

    if isinstance(validation, dict):

        validation_status = _normalized_status(
            validation.get("status")
        )

    if _is_hold_validation_result(
        validation
    ):

        return STATUS_HOLD

    if validation_status == STATUS_REJECTED:

        return STATUS_REJECTED

    if validation_status == STATUS_QUALIFIED:

        promotion_status = ""

        if isinstance(promotion, dict):

            promotion_status = _normalized_status(
                promotion.get("status")
            )

        if promotion_status == STATUS_PROMOTED:

            return STATUS_PROMOTED

        if promotion_status == STATUS_HOLD:

            return STATUS_HOLD

        if promotion_status == STATUS_REJECTED:

            return STATUS_REJECTED

        return STATUS_QUALIFIED

    return STATUS_REJECTED


def _build_state_history(
    validation,
    final_status,
):
    """
    Build the lifecycle state history.

    Insufficient data or insufficient sample
    count goes directly to HOLD.

    Permanent validation failures go to REJECTED.
    """

    history = [
        STATUS_DISCOVERED,
        STATUS_VALIDATING,
    ]

    validation_status = ""

    if isinstance(validation, dict):

        validation_status = _normalized_status(
            validation.get("status")
        )

    if _is_hold_validation_result(
        validation
    ):

        history.append(
            STATUS_HOLD
        )

        return history

    if validation_status == STATUS_REJECTED:

        history.append(
            STATUS_REJECTED
        )

        return history

    if validation_status == STATUS_QUALIFIED:

        history.append(
            STATUS_QUALIFIED
        )

    if final_status == STATUS_PROMOTED:

        if STATUS_QUALIFIED not in history:

            history.append(
                STATUS_QUALIFIED
            )

        history.append(
            STATUS_PROMOTED
        )

        return history

    if final_status == STATUS_HOLD:

        history.append(
            STATUS_HOLD
        )

        return history

    if final_status == STATUS_QUALIFIED:

        if STATUS_QUALIFIED not in history:

            history.append(
                STATUS_QUALIFIED
            )

        return history

    history.append(
        STATUS_REJECTED
    )

    return history


def _validate_candidate(
    candidate,
    evaluation,
    min_score,
    min_confidence,
    min_samples,
):
    """
    Call the Strategy Candidate Validation
    Engine using its stable contract.

    This compatibility layer keeps the
    lifecycle engine isolated from minor
    implementation details while forwarding
    the evaluation data.
    """

    return validate_strategy_candidate(
        candidate=candidate,
        evaluation=evaluation,
        minimum_score=min_score,
        minimum_confidence=min_confidence,
        minimum_samples=min_samples,
    )


def process_strategy_lifecycle(
    candidate,
    evaluation=None,
    min_score=0.0,
    min_confidence=0.0,
    min_samples=0,
):
    """
    Process the complete lifecycle of a
    strategy candidate.
    """

    safe_candidate = _safe_dict(
        candidate
    )

    safe_evaluation = _safe_dict(
        evaluation
    )

    safe_min_score = _safe_number(
        min_score,
        default=0.0,
    )

    safe_min_confidence = _safe_number(
        min_confidence,
        default=0.0,
    )

    safe_min_samples = _safe_number(
        min_samples,
        default=0,
    )

    if not safe_candidate:

        return _invalid_candidate_result(
            candidate=safe_candidate,
            evaluation=safe_evaluation,
        )

    validation = _validate_candidate(
        candidate=safe_candidate,
        evaluation=safe_evaluation,
        min_score=safe_min_score,
        min_confidence=safe_min_confidence,
        min_samples=safe_min_samples,
    )

    validation = _safe_dict(
        validation
    )

    promotion = promote_strategy_candidate(
        validation=validation,
        candidate=safe_candidate,
    )

    promotion = _safe_dict(
        promotion
    )

    final_status = _resolve_final_status(
        validation=validation,
        promotion=promotion,
    )

    state_history = _build_state_history(
        validation=validation,
        final_status=final_status,
    )

    reasons = _resolve_final_reasons(
        validation=validation,
        promotion=promotion,
    )

    return _build_result(
        status=final_status,
        candidate=safe_candidate,
        evaluation=safe_evaluation,
        validation=validation,
        promotion=promotion,
        reasons=reasons,
        state_history=state_history,
    )


def run_strategy_lifecycle(
    candidate,
    evaluation=None,
    min_score=0.0,
    min_confidence=0.0,
    min_samples=0,
):
    """
    Functional alias for
    process_strategy_lifecycle().
    """

    return process_strategy_lifecycle(
        candidate=candidate,
        evaluation=evaluation,
        min_score=min_score,
        min_confidence=min_confidence,
        min_samples=min_samples,
    )


def execute_strategy_lifecycle(
    candidate,
    evaluation=None,
    min_score=0.0,
    min_confidence=0.0,
    min_samples=0,
):
    """
    Functional alias for
    process_strategy_lifecycle().
    """

    return process_strategy_lifecycle(
        candidate=candidate,
        evaluation=evaluation,
        min_score=min_score,
        min_confidence=min_confidence,
        min_samples=min_samples,
    )


class StrategyLifecycleEngine:
    """
    Object-oriented wrapper for the
    Strategy Lifecycle Engine.
    """

    def process(
        self,
        candidate,
        evaluation=None,
        min_score=0.0,
        min_confidence=0.0,
        min_samples=0,
    ):

        return process_strategy_lifecycle(
            candidate=candidate,
            evaluation=evaluation,
            min_score=min_score,
            min_confidence=min_confidence,
            min_samples=min_samples,
        )

    def run(
        self,
        candidate,
        evaluation=None,
        min_score=0.0,
        min_confidence=0.0,
        min_samples=0,
    ):

        return self.process(
            candidate=candidate,
            evaluation=evaluation,
            min_score=min_score,
            min_confidence=min_confidence,
            min_samples=min_samples,
        )

    def execute(
        self,
        candidate,
        evaluation=None,
        min_score=0.0,
        min_confidence=0.0,
        min_samples=0,
    ):

        return self.process(
            candidate=candidate,
            evaluation=evaluation,
            min_score=min_score,
            min_confidence=min_confidence,
            min_samples=min_samples,
        )