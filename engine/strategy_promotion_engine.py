"""
==========================================
SULTAN QUANT OS
Strategy Promotion Engine
Version : 1.0.0
==========================================

Responsibilities:

- Evaluate validated strategy candidates
- Decide whether a candidate can be promoted
- Hold candidates that require more data
- Reject candidates that failed validation
- Preserve validation information
- Produce a stable promotion contract

This engine DOES NOT:

- Generate strategies
- Modify strategies
- Execute backtests
- Execute trades
- Modify the strategy registry

It only answers:

"What should happen to this validated
strategy candidate next?"
"""

from copy import deepcopy


STATUS_PROMOTED = "PROMOTED"
STATUS_HOLD = "HOLD"
STATUS_REJECTED = "REJECTED"


REQUIRED_RESULT_KEYS = (
    "status",
    "promoted",
    "promotion_allowed",
    "candidate",
    "reasons",
    "validation",
)


def required_result_keys():
    """
    Return the stable Strategy Promotion
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


def _get_validation_status(validation):
    """
    Resolve validation status safely.
    """

    if not isinstance(validation, dict):
        return ""

    status = validation.get("status")

    if not isinstance(status, str):
        return ""

    return status.strip().upper()


def _resolve_candidate(validation, candidate):
    """
    Resolve candidate data.

    Explicit candidate data has priority.
    """

    if isinstance(candidate, dict):
        return _safe_dict(candidate)

    if isinstance(validation, dict):

        validation_candidate = (
            validation.get("candidate")
        )

        if isinstance(
            validation_candidate,
            dict,
        ):

            return _safe_dict(
                validation_candidate
            )

    return {}


def _resolve_reasons(validation):
    """
    Extract validation reasons safely.
    """

    if not isinstance(validation, dict):
        return []

    return _safe_list(
        validation.get("reasons")
    )


def promote_strategy_candidate(
    validation,
    candidate=None,
):
    """
    Decide the next promotion state for a
    validated strategy candidate.

    Parameters
    ----------
    validation : dict
        Result from Strategy Candidate
        Validation Engine.

    candidate : dict, optional
        Explicit candidate data.

        When provided, this candidate takes
        priority over validation["candidate"].

    Returns
    -------
    dict
        Stable Strategy Promotion contract.
    """

    safe_validation = _safe_dict(
        validation
    )

    safe_candidate = _resolve_candidate(
        safe_validation,
        candidate,
    )

    validation_status = (
        _get_validation_status(
            safe_validation
        )
    )

    validation_reasons = (
        _resolve_reasons(
            safe_validation
        )
    )

    if not safe_validation:

        return {
            "status": STATUS_REJECTED,
            "promoted": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": [
                "invalid_validation_result"
            ],
            "validation": safe_validation,
        }

    if validation_status == "QUALIFIED":

        return {
            "status": STATUS_PROMOTED,
            "promoted": True,
            "promotion_allowed": True,
            "candidate": safe_candidate,
            "reasons": [
                "candidate_promoted"
            ],
            "validation": safe_validation,
        }

    if validation_status == (
        "INSUFFICIENT_DATA"
    ):

        reasons = [
            "promotion_on_hold",
        ]

        reasons.extend(
            validation_reasons
        )

        return {
            "status": STATUS_HOLD,
            "promoted": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": reasons,
            "validation": safe_validation,
        }

    if validation_status == "REJECTED":

        reasons = [
            "candidate_rejected",
        ]

        reasons.extend(
            validation_reasons
        )

        return {
            "status": STATUS_REJECTED,
            "promoted": False,
            "promotion_allowed": False,
            "candidate": safe_candidate,
            "reasons": reasons,
            "validation": safe_validation,
        }

    return {
        "status": STATUS_REJECTED,
        "promoted": False,
        "promotion_allowed": False,
        "candidate": safe_candidate,
        "reasons": [
            "unknown_validation_status"
        ],
        "validation": safe_validation,
    }


class StrategyPromotionEngine:
    """
    Object-oriented wrapper.

    Keeps the functional API available while
    allowing institutional pipeline integration.
    """

    def promote(
        self,
        validation,
        candidate=None,
    ):

        return promote_strategy_candidate(
            validation=validation,
            candidate=candidate,
        )

    def run(
        self,
        validation,
        candidate=None,
    ):

        return self.promote(
            validation=validation,
            candidate=candidate,
        )


def process_strategy_promotion(
    validation,
    candidate=None,
):
    """
    Backward-friendly functional alias.
    """

    return promote_strategy_candidate(
        validation=validation,
        candidate=candidate,
    )