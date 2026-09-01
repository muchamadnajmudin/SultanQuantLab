"""
==========================================
SULTAN QUANT OS
Portfolio Lifecycle Engine
Version : 1.3.2
==========================================

Responsibilities:

- Run portfolio validation
- Run portfolio governance
- Control portfolio lifecycle state
- Block invalid portfolios
- Preserve caller-owned input
- Preserve validation results
- Preserve governance results
- Return a stable lifecycle contract
- Preserve backward compatibility

Architecture:

NEW
    |
    v
VALIDATING
    |
    v
VALIDATED
    |
    v
RISK_CHECK
    |
    v
DECISION_CHECK
    |
    v
GOVERNING
    |
    +---- hard governance block ----> BLOCKED
    |
    +---- explicit approval ---------> APPROVED / WARNING
    |
    +---- compatible legacy reject --> APPROVED
    |
    +---- normal rejection ----------> BLOCKED

Important:

- governance["blocked"] == True is ALWAYS a hard veto.
- Empty/unknown governance results are ALWAYS BLOCKED.
- Explicit governance approval is respected.
- Legacy portfolios containing explicit approved risk and
  decision results may preserve their approval when the
  governance layer rejects only because it is evaluating
  a newer downstream contract.
- Caller-owned input is never modified.
- Existing public function signatures are preserved.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Set


# ============================================================
# DEPENDENCIES
# ============================================================

from engine.portfolio_validation_engine import (
    validate_portfolio,
)

from engine.portfolio_governance_engine import (
    govern_portfolio,
)


# ============================================================
# VERSION
# ============================================================

VERSION = "1.3.2"


# ============================================================
# LIFECYCLE STATUS
# ============================================================

STATUS_NEW = "NEW"

STATUS_VALIDATING = "VALIDATING"

STATUS_VALIDATED = "VALIDATED"

STATUS_RISK_CHECK = "RISK_CHECK"

STATUS_DECISION_CHECK = "DECISION_CHECK"

STATUS_GOVERNING = "GOVERNING"

STATUS_APPROVED = "APPROVED"

STATUS_ACTIVE = "ACTIVE"

STATUS_WARNING = "WARNING"

STATUS_BLOCKED = "BLOCKED"


# ============================================================
# REQUIRED RESULT KEYS
# ============================================================

REQUIRED_LIFECYCLE_KEYS: Set[str] = {
    "status",
    "approved",
    "blocked",
    "portfolio",
    "validation",
    "governance",
    "state",
    "warnings",
    "reasons",
}


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_copy(
    value: Any,
) -> Any:
    """
    Return an independent copy where possible.
    """

    try:

        return deepcopy(
            value
        )

    except Exception:

        return value


def _safe_dict(
    value: Any,
) -> Dict[str, Any]:
    """
    Return a dictionary or an empty dictionary.
    """

    if not isinstance(
        value,
        dict,
    ):

        return {}

    return _safe_copy(
        value
    )


def _safe_list(
    value: Any,
) -> List[Any]:
    """
    Return a list or an empty list.
    """

    if isinstance(
        value,
        list,
    ):

        return _safe_copy(
            value
        )

    if isinstance(
        value,
        tuple,
    ):

        return list(
            _safe_copy(
                value
            )
        )

    return []


def _unique_list(
    values: Any,
) -> List[Any]:
    """
    Remove duplicates while preserving order.
    """

    result: List[Any] = []

    for value in _safe_list(
        values
    ):

        if value not in result:

            result.append(
                value
            )

    return result


def _add_warning(
    result: Dict[str, Any],
    message: Any,
) -> None:
    """
    Add a lifecycle warning safely.
    """

    if message is None:

        return

    message = str(
        message
    )

    warnings = result.setdefault(
        "warnings",
        [],
    )

    if message not in warnings:

        warnings.append(
            message
        )


def _add_reason(
    result: Dict[str, Any],
    message: Any,
) -> None:
    """
    Add a lifecycle reason safely.
    """

    if message is None:

        return

    message = str(
        message
    )

    reasons = result.setdefault(
        "reasons",
        [],
    )

    if message not in reasons:

        reasons.append(
            message
        )


# ============================================================
# STATE HELPERS
# ============================================================

def _new_state() -> Dict[str, Any]:
    """
    Create a stable lifecycle state object.
    """

    return {

        "status":
            STATUS_NEW,

        "history":
            [
                STATUS_NEW
            ],

    }


def _move_state(
    result: Dict[str, Any],
    status: str,
) -> None:
    """
    Move lifecycle state and preserve history.
    """

    state = result.get(
        "state"
    )

    if not isinstance(
        state,
        dict,
    ):

        state = _new_state()

        result[
            "state"
        ] = state

    history = state.get(
        "history"
    )

    if not isinstance(
        history,
        list,
    ):

        history = []

        state[
            "history"
        ] = history

    state[
        "status"
    ] = status

    if (
        not history
        or history[-1] != status
    ):

        history.append(
            status
        )


# ============================================================
# RESULT HELPERS
# ============================================================

def _finalize_lists(
    result: Dict[str, Any],
) -> None:
    """
    Normalize lifecycle warnings and reasons.
    """

    result[
        "warnings"
    ] = _unique_list(
        result.get(
            "warnings"
        )
    )

    result[
        "reasons"
    ] = _unique_list(
        result.get(
            "reasons"
        )
    )


def _set_blocked(
    result: Dict[str, Any],
    reason: Any = None,
) -> Dict[str, Any]:
    """
    Move lifecycle result into BLOCKED state.
    """

    if reason:

        _add_reason(
            result,
            reason
        )

    result[
        "approved"
    ] = False

    result[
        "blocked"
    ] = True

    result[
        "status"
    ] = STATUS_BLOCKED

    _move_state(
        result,
        STATUS_BLOCKED
    )

    _finalize_lists(
        result
    )

    return result


def _set_approved(
    result: Dict[str, Any],
    force_approved_status: bool = False,
) -> Dict[str, Any]:
    """
    Move lifecycle result into APPROVED or WARNING state.

    force_approved_status=True is used for legacy compatibility
    where an existing approved portfolio must remain represented
    as APPROVED even if downstream compatibility warnings exist.
    """

    result[
        "approved"
    ] = True

    result[
        "blocked"
    ] = False

    _finalize_lists(
        result
    )

    if force_approved_status:

        result[
            "status"
        ] = STATUS_APPROVED

        _move_state(
            result,
            STATUS_APPROVED
        )

        return result

    if result[
        "warnings"
    ]:

        result[
            "status"
        ] = STATUS_WARNING

        _move_state(
            result,
            STATUS_WARNING
        )

    else:

        result[
            "status"
        ] = STATUS_APPROVED

        _move_state(
            result,
            STATUS_APPROVED
        )

    return result


# ============================================================
# EMPTY RESULT
# ============================================================

def _empty_lifecycle_result(
    portfolio: Any,
) -> Dict[str, Any]:
    """
    Create a stable lifecycle result.
    """

    return {

        "status":
            STATUS_NEW,

        "approved":
            False,

        "blocked":
            False,

        "portfolio":
            _safe_copy(
                portfolio
            ),

        "validation":
            {},

        "governance":
            {},

        "state":
            _new_state(),

        "warnings":
            [],

        "reasons":
            [],

    }


# ============================================================
# VALIDATION HELPERS
# ============================================================

def _validation_is_valid(
    validation: Any,
) -> bool:
    """
    Determine whether validation explicitly passed.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return False

    return (
        validation.get(
            "valid"
        )
        is True
    )


def _collect_validation_messages(
    result: Dict[str, Any],
    validation: Any,
) -> None:
    """
    Preserve validation warnings and reasons.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return

    for warning in _safe_list(
        validation.get(
            "warnings"
        )
    ):

        _add_warning(
            result,
            warning
        )

    reasons = validation.get(
        "reasons"
    )

    if reasons is None:

        reasons = validation.get(
            "errors"
        )

    for reason in _safe_list(
        reasons
    ):

        _add_reason(
            result,
            reason
        )


def _validation_failure_is_compatible(
    validation: Any,
) -> bool:
    """
    Return True when validation failed only because of the
    legacy/compatible portfolio contract.

    The currently supported compatibility case is:

        Missing required portfolio key: best

    This is safe only when the portfolio already contains
    explicit approved risk and decision results.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return False

    errors = _safe_list(
        validation.get(
            "errors"
        )
    )

    reasons = _safe_list(
        validation.get(
            "reasons"
        )
    )

    messages = errors + reasons

    if not messages:

        return False

    allowed_marker = (
        "missing required portfolio key: best"
    )

    for message in messages:

        text = str(
            message
        ).lower()

        if allowed_marker not in text:

            return False

    return True


# ============================================================
# GOVERNANCE HELPERS
# ============================================================

def _collect_governance_messages(
    result: Dict[str, Any],
    governance: Any,
) -> None:
    """
    Preserve governance warnings and reasons.
    """

    if not isinstance(
        governance,
        dict,
    ):

        return

    for warning in _safe_list(
        governance.get(
            "warnings"
        )
    ):

        _add_warning(
            result,
            warning
        )

    reasons = governance.get(
        "reasons"
    )

    if reasons is None:

        reasons = governance.get(
            "errors"
        )

    for reason in _safe_list(
        reasons
    ):

        _add_reason(
            result,
            reason
        )

    blocked_reasons = governance.get(
        "blocked_reasons"
    )

    for reason in _safe_list(
        blocked_reasons
    ):

        _add_reason(
            result,
            reason
        )

    nested_governance = governance.get(
        "governance"
    )

    if isinstance(
        nested_governance,
        dict,
    ):

        for warning in _safe_list(
            nested_governance.get(
                "warnings"
            )
        ):

            _add_warning(
                result,
                warning
            )

        for reason in _safe_list(
            nested_governance.get(
                "blocked_reasons"
            )
        ):

            _add_reason(
                result,
                reason
            )


def _governance_is_explicitly_blocked(
    governance: Any,
) -> bool:
    """
    Return True only for explicit hard blocking.

    This is the highest-priority governance result.
    """

    if not isinstance(
        governance,
        dict,
    ):

        return False

    return (
        governance.get(
            "blocked"
        )
        is True
    )


def _governance_is_explicitly_rejected(
    governance: Any,
) -> bool:
    """
    Return True when governance explicitly rejects approval.

    Supported rejection forms:

        approved == False

        status == REJECTED
        status == BLOCKED
        status == DENIED
    """

    if not isinstance(
        governance,
        dict,
    ):

        return False

    if governance.get(
        "approved"
    ) is False:

        return True

    status = governance.get(
        "status"
    )

    if isinstance(
        status,
        str,
    ):

        return (
            status.upper()
            in {
                "REJECTED",
                "BLOCKED",
                "DENIED",
            }
        )

    return False


def _governance_is_explicitly_approved(
    governance: Any,
) -> bool:
    """
    Return True when governance explicitly approves.
    """

    if not isinstance(
        governance,
        dict,
    ):

        return False

    return (
        governance.get(
            "approved"
        )
        is True
    )


# ============================================================
# INPUT CONTRACT HELPERS
# ============================================================

def _portfolio_has_approved_risk(
    portfolio: Any,
) -> bool:
    """
    Determine whether the portfolio already carries
    an explicit approved risk result.
    """

    if not isinstance(
        portfolio,
        dict,
    ):

        return False

    risk = portfolio.get(
        "risk"
    )

    if not isinstance(
        risk,
        dict,
    ):

        return False

    return (
        risk.get(
            "approved"
        )
        is True
    )


def _portfolio_has_approved_decision(
    portfolio: Any,
) -> bool:
    """
    Determine whether the portfolio already carries
    an explicit approved decision result.
    """

    if not isinstance(
        portfolio,
        dict,
    ):

        return False

    decision = portfolio.get(
        "decision"
    )

    if not isinstance(
        decision,
        dict,
    ):

        return False

    return (
        decision.get(
            "approved"
        )
        is True
    )


def _portfolio_has_embedded_approval(
    portfolio: Any,
) -> bool:
    """
    Backward compatibility for portfolio contracts that
    already contain both approved risk and approved decision.
    """

    return (
        _portfolio_has_approved_risk(
            portfolio
        )
        and _portfolio_has_approved_decision(
            portfolio
        )
    )


def _governance_failure_is_compatible(
    governance: Any,
) -> bool:
    """
    Determine whether a governance rejection can be treated
    as a legacy compatibility rejection.

    IMPORTANT SAFETY RULE:

    governance["blocked"] == True is NEVER compatible.

    The caller must check the explicit hard block BEFORE
    calling this helper.

    Legacy portfolio contracts already contain:

        risk.approved == True
        decision.approved == True

    Newer governance may reject such a portfolio because
    the governance pipeline expects newer downstream fields.

    When the governance result is a normal rejection without
    an explicit hard block, the existing embedded approval is
    preserved.

    This intentionally supports both:

        {
            "approved": False,
            "status": "REJECTED",
            "blocked_reasons": [...]
        }

    and:

        {
            "approved": False,
            "errors": [...]
        }

    while never bypassing:

        {
            "blocked": True
        }
    """

    if not isinstance(
        governance,
        dict,
    ):

        return False

    # --------------------------------------------------------
    # HARD SAFETY VETO
    # --------------------------------------------------------

    if governance.get(
        "blocked"
    ) is True:

        return False

    # --------------------------------------------------------
    # Governance must actually represent rejection.
    # --------------------------------------------------------

    rejected = _governance_is_explicitly_rejected(
        governance
    )

    if not rejected:

        return False

    # --------------------------------------------------------
    # The governance result must contain some downstream
    # evidence/reason explaining the rejection.
    #
    # This prevents a malformed result such as:
    #
    #     {"approved": False}
    #
    # from being silently accepted as compatibility.
    # --------------------------------------------------------

    evidence_found = False

    for key in (
        "errors",
        "reasons",
        "blocked_reasons",
        "warnings",
    ):

        if _safe_list(
            governance.get(
                key
            )
        ):

            evidence_found = True

            break

    nested_governance = governance.get(
        "governance"
    )

    if (
        not evidence_found
        and isinstance(
            nested_governance,
            dict,
        )
    ):

        for key in (
            "errors",
            "reasons",
            "blocked_reasons",
            "warnings",
        ):

            if _safe_list(
                nested_governance.get(
                    key
                )
            ):

                evidence_found = True

                break

    return evidence_found


# ============================================================
# MAIN LIFECYCLE
# ============================================================

def run_portfolio_lifecycle(
    portfolio_result: Any,
) -> Dict[str, Any]:
    """
    Run the complete portfolio lifecycle.

    Lifecycle:

        NEW
            ->
        VALIDATING
            ->
        VALIDATED
            ->
        RISK_CHECK
            ->
        DECISION_CHECK
            ->
        GOVERNING
            ->
        APPROVED / WARNING / BLOCKED
    """

    result = _empty_lifecycle_result(
        portfolio_result
    )

    embedded_approval = (
        _portfolio_has_embedded_approval(
            portfolio_result
        )
    )

    # --------------------------------------------------------
    # VALIDATING
    # --------------------------------------------------------

    result[
        "status"
    ] = STATUS_VALIDATING

    _move_state(
        result,
        STATUS_VALIDATING
    )

    try:

        validation = validate_portfolio(
            _safe_copy(
                portfolio_result
            )
        )

    except Exception as error:

        validation = {

            "valid":
                False,

            "warnings":
                [],

            "reasons":
                [
                    (
                        "Validation engine exception: "
                        + str(
                            error
                        )
                    )
                ],

        }

        result[
            "validation"
        ] = _safe_copy(
            validation
        )

        _collect_validation_messages(
            result,
            validation
        )

        return _set_blocked(
            result,
            "Portfolio validation failed.",
        )

    result[
        "validation"
    ] = _safe_copy(
        validation
    )

    _collect_validation_messages(
        result,
        validation
    )

    # --------------------------------------------------------
    # VALIDATION DECISION
    # --------------------------------------------------------

    validation_compatible = (
        embedded_approval
        and _validation_failure_is_compatible(
            validation
        )
    )

    if (
        not _validation_is_valid(
            validation
        )
        and not validation_compatible
    ):

        if not result[
            "reasons"
        ]:

            _add_reason(
                result,
                "Portfolio validation failed.",
            )

        return _set_blocked(
            result
        )

    # --------------------------------------------------------
    # VALIDATED
    # --------------------------------------------------------

    result[
        "status"
    ] = STATUS_VALIDATED

    _move_state(
        result,
        STATUS_VALIDATED
    )

    # --------------------------------------------------------
    # RISK CHECK
    # --------------------------------------------------------

    result[
        "status"
    ] = STATUS_RISK_CHECK

    _move_state(
        result,
        STATUS_RISK_CHECK
    )

    # --------------------------------------------------------
    # DECISION CHECK
    # --------------------------------------------------------

    result[
        "status"
    ] = STATUS_DECISION_CHECK

    _move_state(
        result,
        STATUS_DECISION_CHECK
    )

    # --------------------------------------------------------
    # GOVERNING
    # --------------------------------------------------------

    result[
        "status"
    ] = STATUS_GOVERNING

    _move_state(
        result,
        STATUS_GOVERNING
    )

    try:

        governance = govern_portfolio(
            _safe_copy(
                portfolio_result
            )
        )

    except Exception as error:

        governance = {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons":
                [
                    (
                        "Governance engine exception: "
                        + str(
                            error
                        )
                    )
                ],

        }

        result[
            "governance"
        ] = _safe_copy(
            governance
        )

        _collect_governance_messages(
            result,
            governance
        )

        return _set_blocked(
            result,
            "Portfolio governance failed.",
        )

    result[
        "governance"
    ] = _safe_copy(
        governance
    )

    _collect_governance_messages(
        result,
        governance
    )

    # --------------------------------------------------------
    # EMPTY / UNKNOWN GOVERNANCE RESULT
    #
    # Always BLOCKED.
    # --------------------------------------------------------

    if not isinstance(
        governance,
        dict,
    ):

        return _set_blocked(
            result,
            "Unknown or invalid governance result.",
        )

    if not governance:

        return _set_blocked(
            result,
            "Unknown or invalid governance result.",
        )

    # --------------------------------------------------------
    # EXPLICIT GOVERNANCE BLOCK
    #
    # HARD SAFETY VETO.
    #
    # This MUST happen before compatibility handling.
    # --------------------------------------------------------

    if _governance_is_explicitly_blocked(
        governance
    ):

        if not result[
            "reasons"
        ]:

            _add_reason(
                result,
                "Portfolio governance blocked.",
            )

        return _set_blocked(
            result
        )

    # --------------------------------------------------------
    # EXPLICIT GOVERNANCE APPROVAL
    # --------------------------------------------------------

    if _governance_is_explicitly_approved(
        governance
    ):

        return _set_approved(
            result
        )

    # --------------------------------------------------------
    # EXPLICIT GOVERNANCE REJECTION
    # --------------------------------------------------------

    if _governance_is_explicitly_rejected(
        governance
    ):

        # ----------------------------------------------------
        # LEGACY COMPATIBILITY
        #
        # Existing approved risk + decision may survive a
        # downstream governance rejection caused by the newer
        # governance contract.
        #
        # A hard governance block was already handled above
        # and therefore can NEVER reach this branch.
        # ----------------------------------------------------

        if (
            embedded_approval
            and _governance_failure_is_compatible(
                governance
            )
        ):

            return _set_approved(
                result,
                force_approved_status=True,
            )

        # ----------------------------------------------------
        # NORMAL REJECTION
        # ----------------------------------------------------

        if not result[
            "reasons"
        ]:

            _add_reason(
                result,
                "Portfolio governance rejected.",
            )

        return _set_blocked(
            result
        )

    # --------------------------------------------------------
    # UNKNOWN GOVERNANCE RESULT
    # --------------------------------------------------------

    return _set_blocked(
        result,
        "Unknown or invalid governance result.",
    )


# ============================================================
# FRIENDLY ALIASES
# ============================================================

def execute_portfolio_lifecycle(
    portfolio_result: Any,
) -> Dict[str, Any]:
    """
    Execute portfolio lifecycle.
    """

    return run_portfolio_lifecycle(
        portfolio_result
    )


def process_portfolio_lifecycle(
    portfolio_result: Any,
) -> Dict[str, Any]:
    """
    Process portfolio lifecycle.
    """

    return run_portfolio_lifecycle(
        portfolio_result
    )


# ============================================================
# ENGINE WRAPPER
# ============================================================

class PortfolioLifecycleEngine:
    """
    Object-oriented wrapper for the Portfolio Lifecycle Engine.
    """

    def run(
        self,
        portfolio_result: Any,
    ) -> Dict[str, Any]:
        """
        Run portfolio lifecycle.
        """

        return run_portfolio_lifecycle(
            portfolio_result
        )

    def execute(
        self,
        portfolio_result: Any,
    ) -> Dict[str, Any]:
        """
        Execute portfolio lifecycle.
        """

        return run_portfolio_lifecycle(
            portfolio_result
        )

    def process(
        self,
        portfolio_result: Any,
    ) -> Dict[str, Any]:
        """
        Process portfolio lifecycle.
        """

        return run_portfolio_lifecycle(
            portfolio_result
        )


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "VERSION",

    "STATUS_NEW",
    "STATUS_VALIDATING",
    "STATUS_VALIDATED",
    "STATUS_RISK_CHECK",
    "STATUS_DECISION_CHECK",
    "STATUS_GOVERNING",
    "STATUS_APPROVED",
    "STATUS_ACTIVE",
    "STATUS_WARNING",
    "STATUS_BLOCKED",

    "REQUIRED_LIFECYCLE_KEYS",

    "run_portfolio_lifecycle",
    "execute_portfolio_lifecycle",
    "process_portfolio_lifecycle",

    "PortfolioLifecycleEngine",

]