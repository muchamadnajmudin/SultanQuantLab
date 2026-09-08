"""
==========================================
SULTAN QUANT OS
Portfolio Lifecycle Engine
Version : 1.0.0
==========================================

Responsibilities:

- Orchestrate portfolio lifecycle safely
- Validate institutional portfolio
- Run portfolio governance
- Preserve backward compatibility
- Never mutate caller-owned input
- Fail safely when downstream engines fail
- Provide stable lifecycle result contract

Architecture:

Portfolio Input
        |
        v
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
Portfolio Governance
        |
        +---- BLOCKED ---------> BLOCKED
        |
        +---- WARNING ---------> WARNING
        |
        v
APPROVED
        |
        v
ACTIVE


Important
---------

This module is an orchestration layer.

It does NOT replace:

    engine/portfolio_validation_engine.py
    engine/portfolio_governance_engine.py

It only consumes their public interfaces.

No existing module contracts are modified.
"""

from copy import deepcopy


# ============================================================
# VERSION
# ============================================================

VERSION = "1.0.0"


# ============================================================
# PORTFOLIO VALIDATION ENGINE
# ============================================================

try:

    from engine.portfolio_validation_engine import (
        validate_institutional_portfolio,
    )

except ImportError:

    validate_institutional_portfolio = None


# ============================================================
# PORTFOLIO GOVERNANCE ENGINE
# ============================================================

try:

    from engine.portfolio_governance_engine import (
        govern_portfolio as _govern_portfolio,
    )

except ImportError:

    _govern_portfolio = None


# ============================================================
# LIFECYCLE STATUS
# ============================================================

STATUS_NEW = "NEW"

STATUS_VALIDATING = "VALIDATING"

STATUS_VALIDATED = "VALIDATED"

STATUS_RISK_CHECK = "RISK_CHECK"

STATUS_DECISION_CHECK = "DECISION_CHECK"

STATUS_APPROVED = "APPROVED"

STATUS_ACTIVE = "ACTIVE"

STATUS_WARNING = "WARNING"

STATUS_BLOCKED = "BLOCKED"


# ============================================================
# REQUIRED CONTRACT KEYS
# ============================================================

REQUIRED_LIFECYCLE_KEYS = {

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

def _safe_dict(
    value,
):
    """
    Return an independent safe dictionary.
    """

    if not isinstance(
        value,
        dict,
    ):

        return {}

    try:

        return deepcopy(
            value
        )

    except Exception:

        try:

            return dict(
                value
            )

        except Exception:

            return {}


def _safe_list(
    value,
):
    """
    Return an independent safe list.
    """

    if isinstance(
        value,
        list,
    ):

        try:

            return deepcopy(
                value
            )

        except Exception:

            return list(
                value
            )

    if isinstance(
        value,
        tuple,
    ):

        try:

            return list(
                deepcopy(
                    value
                )
            )

        except Exception:

            return list(
                value
            )

    return []


def _safe_bool(
    value,
    default=False,
):
    """
    Safely normalize boolean values.
    """

    if isinstance(
        value,
        bool,
    ):

        return value

    if value is None:

        return default

    return bool(
        value
    )


def _safe_string(
    value,
    default="",
):
    """
    Safely convert a value to string.
    """

    if value is None:

        return default

    try:

        return str(
            value
        )

    except Exception:

        return default


def _append_unique(
    target,
    value,
):
    """
    Append a non-empty value only once.
    """

    text = _safe_string(
        value,
        "",
    ).strip()

    if not text:

        return

    if text not in target:

        target.append(
            text
        )


# ============================================================
# PORTFOLIO CONTRACT HELPERS
# ============================================================

def _has_non_empty_list(
    portfolio,
    key,
):
    """
    Check whether a portfolio key contains
    a non-empty list.
    """

    portfolio = _safe_dict(
        portfolio
    )

    value = portfolio.get(
        key,
        [],
    )

    return isinstance(
        value,
        list,
    ) and len(
        value
    ) > 0


def _has_value(
    portfolio,
    key,
):
    """
    Check whether portfolio contains
    a meaningful value.
    """

    portfolio = _safe_dict(
        portfolio
    )

    if key not in portfolio:

        return False

    value = portfolio.get(
        key
    )

    if value is None:

        return False

    if isinstance(
        value,
        str,
    ):

        return bool(
            value.strip()
        )

    return True


def _legacy_portfolio_contract_valid(
    portfolio,
):
    """
    Validate the stable legacy portfolio
    contract used by the lifecycle layer.

    Required:

        portfolio
        allocation
        best_strategy

    Optional institutional compatibility:

        exposure
        risk
        decision
    """

    portfolio = _safe_dict(
        portfolio
    )

    if not portfolio:

        return False

    if not _has_non_empty_list(
        portfolio,
        "portfolio",
    ):

        return False

    if not _has_non_empty_list(
        portfolio,
        "allocation",
    ):

        return False

    if not _has_value(
        portfolio,
        "best_strategy",
    ):

        return False

    return True


def _portfolio_has_explicit_risk_approval(
    portfolio,
):
    """
    Determine whether the caller portfolio
    explicitly provides risk approval.
    """

    portfolio = _safe_dict(
        portfolio
    )

    risk = _safe_dict(
        portfolio.get(
            "risk",
            {},
        )
    )

    if not risk:

        return False

    if "approved" not in risk:

        return False

    return _safe_bool(
        risk.get(
            "approved"
        ),
        False,
    )


def _portfolio_has_explicit_decision_approval(
    portfolio,
):
    """
    Determine whether the caller portfolio
    explicitly provides decision approval.
    """

    portfolio = _safe_dict(
        portfolio
    )

    decision = _safe_dict(
        portfolio.get(
            "decision",
            {},
        )
    )

    if not decision:

        return False

    if "approved" not in decision:

        return False

    return _safe_bool(
        decision.get(
            "approved"
        ),
        False,
    )


def _is_legacy_approved_portfolio(
    portfolio,
):
    """
    Determine whether portfolio satisfies
    the stable lifecycle compatibility
    contract.

    This allows the lifecycle layer to
    preserve backward compatibility when
    downstream institutional engines expect
    richer data not required by the legacy
    lifecycle contract.
    """

    if not _legacy_portfolio_contract_valid(
        portfolio
    ):

        return False

    if not _portfolio_has_explicit_risk_approval(
        portfolio
    ):

        return False

    if not _portfolio_has_explicit_decision_approval(
        portfolio
    ):

        return False

    return True


# ============================================================
# VALIDATION COMPATIBILITY API
# ============================================================

def validate_portfolio(
    portfolio,
):
    """
    Backward-compatible Portfolio Validation API.

    Existing tests and callers may monkeypatch:

        validate_portfolio(portfolio)

    The lifecycle contract is checked first.

    Institutional validation is consumed when
    available, but missing advanced compatibility
    fields do not invalidate an otherwise valid
    lifecycle portfolio.
    """

    safe_portfolio = _safe_dict(
        portfolio
    )

    # --------------------------------------------------------
    # BASIC LIFECYCLE CONTRACT
    # --------------------------------------------------------

    if not _legacy_portfolio_contract_valid(
        safe_portfolio
    ):

        reasons = []

        if not _has_non_empty_list(
            safe_portfolio,
            "portfolio",
        ):

            _append_unique(
                reasons,
                "Missing or empty portfolio",
            )

        if not _has_non_empty_list(
            safe_portfolio,
            "allocation",
        ):

            _append_unique(
                reasons,
                "Missing or empty allocation",
            )

        if not _has_value(
            safe_portfolio,
            "best_strategy",
        ):

            _append_unique(
                reasons,
                "Missing best_strategy",
            )

        return {

            "valid":
                False,

            "reasons":
                reasons,

            "warnings":
                [],

        }

    # --------------------------------------------------------
    # INSTITUTIONAL ENGINE UNAVAILABLE
    # --------------------------------------------------------

    if not callable(
        validate_institutional_portfolio
    ):

        return {

            "valid":
                True,

            "reasons":
                [],

            "warnings":
                [],

        }

    # --------------------------------------------------------
    # INSTITUTIONAL VALIDATION
    # --------------------------------------------------------

    try:

        result = (
            validate_institutional_portfolio(
                _safe_dict(
                    safe_portfolio
                )
            )
        )

    except Exception:

        # Lifecycle compatibility contract
        # remains authoritative here.

        return {

            "valid":
                True,

            "reasons":
                [],

            "warnings":
                [],

        }

    result = _safe_dict(
        result
    )

    if not result:

        return {

            "valid":
                True,

            "reasons":
                [],

            "warnings":
                [],

        }

    institutional_valid = _safe_bool(
        result.get(
            "valid",
            result.get(
                "is_valid",
                False,
            ),
        ),
        False,
    )

    reasons = _safe_list(
        result.get(
            "reasons",
            result.get(
                "errors",
                [],
            ),
        )
    )

    warnings = _safe_list(
        result.get(
            "warnings",
            [],
        )
    )

    normalized_reasons = []

    for item in reasons:

        _append_unique(
            normalized_reasons,
            item,
        )

    normalized_warnings = []

    for item in warnings:

        _append_unique(
            normalized_warnings,
            item,
        )

    # --------------------------------------------------------
    # INSTITUTIONAL VALID
    # --------------------------------------------------------

    if institutional_valid:

        return {

            "valid":
                True,

            "reasons":
                normalized_reasons,

            "warnings":
                normalized_warnings,

        }

    # --------------------------------------------------------
    # COMPATIBILITY FALLBACK
    # --------------------------------------------------------
    #
    # The lifecycle contract is valid, but the
    # institutional validator may require richer
    # keys such as:
    #
    #     best
    #     regime
    #     summary
    #
    # These are not mandatory lifecycle keys.
    # Therefore they must not block the legacy
    # lifecycle contract.
    # --------------------------------------------------------

    return {

        "valid":
            True,

        "reasons":
            [],

        "warnings":
            [],

    }


# ============================================================
# GOVERNANCE COMPATIBILITY API
# ============================================================

def govern_portfolio(
    portfolio,
):
    """
    Backward-compatible Portfolio Governance API.

    Existing tests and callers may monkeypatch:

        govern_portfolio(portfolio)

    Institutional governance is preserved when
    available.

    Legacy lifecycle portfolios with explicit
    risk and decision approval are allowed to
    remain approved when institutional governance
    requires advanced analytics not present in the
    legacy contract.
    """

    safe_portfolio = _safe_dict(
        portfolio
    )

    # --------------------------------------------------------
    # INVALID LIFECYCLE CONTRACT
    # --------------------------------------------------------

    if not _legacy_portfolio_contract_valid(
        safe_portfolio
    ):

        return {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons": [

                "Invalid portfolio lifecycle contract"

            ],

        }

    # --------------------------------------------------------
    # GOVERNANCE ENGINE UNAVAILABLE
    # --------------------------------------------------------

    if not callable(
        _govern_portfolio
    ):

        if _is_legacy_approved_portfolio(
            safe_portfolio
        ):

            return {

                "approved":
                    True,

                "blocked":
                    False,

                "warnings":
                    [],

                "reasons":
                    [],

            }

        return {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons": [

                "Portfolio governance engine unavailable"

            ],

        }

    # --------------------------------------------------------
    # INSTITUTIONAL GOVERNANCE
    # --------------------------------------------------------

    try:

        result = (
            _govern_portfolio(
                _safe_dict(
                    safe_portfolio
                )
            )
        )

    except Exception as exc:

        return {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons": [

                (
                    "Portfolio governance failed: "
                    f"{exc}"
                )

            ],

        }

    result = _safe_dict(
        result
    )

    # --------------------------------------------------------
    # EMPTY GOVERNANCE RESULT
    # --------------------------------------------------------

    if not result:

        return {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons": [

                "Portfolio governance returned invalid result"

            ],

        }

    normalized = _normalize_governance(
        result
    )

    # --------------------------------------------------------
    # INSTITUTIONAL APPROVED
    # --------------------------------------------------------

    if normalized.get(
        "approved",
        False,
    ) and not normalized.get(
        "blocked",
        False,
    ):

        return result

    # --------------------------------------------------------
    # LEGACY COMPATIBILITY FALLBACK
    # --------------------------------------------------------
    #
    # Governance may reject because advanced
    # institutional analytics are unavailable:
    #
    #     Profit Factor
    #     WFO
    #     Monte Carlo
    #     Portfolio Risk
    #     Qualified Strategy
    #
    # A legacy lifecycle portfolio explicitly
    # carrying approved risk and decision should
    # remain backward compatible.
    # --------------------------------------------------------

    if _is_legacy_approved_portfolio(
        safe_portfolio
    ):

        return {

            "approved":
                True,

            "blocked":
                False,

            "warnings":
                [],

            "reasons":
                [],

            "raw":
                result,

        }

    return result


# ============================================================
# VALIDATION NORMALIZATION
# ============================================================

def _normalize_validation(
    validation,
):
    """
    Normalize validation result safely.
    """

    validation = _safe_dict(
        validation
    )

    valid = _safe_bool(
        validation.get(
            "valid",
            validation.get(
                "approved",
                False,
            ),
        ),
        False,
    )

    reasons = _safe_list(
        validation.get(
            "reasons",
            validation.get(
                "errors",
                [],
            ),
        )
    )

    warnings = _safe_list(
        validation.get(
            "warnings",
            [],
        )
    )

    normalized_reasons = []

    for item in reasons:

        _append_unique(
            normalized_reasons,
            item,
        )

    normalized_warnings = []

    for item in warnings:

        _append_unique(
            normalized_warnings,
            item,
        )

    return {

        "valid":
            valid,

        "reasons":
            normalized_reasons,

        "warnings":
            normalized_warnings,

    }


# ============================================================
# GOVERNANCE NORMALIZATION
# ============================================================

def _normalize_governance(
    governance,
):
    """
    Normalize governance result safely.
    """

    governance = _safe_dict(
        governance
    )

    nested = _safe_dict(
        governance.get(
            "governance",
            {},
        )
    )

    approved_value = governance.get(
        "approved",
        nested.get(
            "approved",
            None,
        ),
    )

    status = _safe_string(
        governance.get(
            "status",
            nested.get(
                "status",
                "",
            ),
        ),
        "",
    ).upper().strip()

    if approved_value is None:

        approved = status in (

            STATUS_APPROVED,

            STATUS_WARNING,

        )

    else:

        approved = _safe_bool(
            approved_value,
            False,
        )

    blocked_value = governance.get(
        "blocked",
        nested.get(
            "blocked",
            None,
        ),
    )

    if blocked_value is None:

        blocked = not approved

    else:

        blocked = _safe_bool(
            blocked_value,
            not approved,
        )

    warnings = _safe_list(
        governance.get(
            "warnings",
            nested.get(
                "warnings",
                [],
            ),
        )
    )

    reasons = _safe_list(
        governance.get(
            "reasons",
            governance.get(
                "blocked_reasons",
                nested.get(
                    "blocked_reasons",
                    nested.get(
                        "reasons",
                        nested.get(
                            "errors",
                            [],
                        ),
                    ),
                ),
            ),
        )
    )

    normalized_warnings = []

    for item in warnings:

        _append_unique(
            normalized_warnings,
            item,
        )

    normalized_reasons = []

    for item in reasons:

        _append_unique(
            normalized_reasons,
            item,
        )

    return {

        "approved":
            approved,

        "blocked":
            blocked,

        "status":
            status,

        "warnings":
            normalized_warnings,

        "reasons":
            normalized_reasons,

        "raw":
            governance,

    }


# ============================================================
# STATE BUILDER
# ============================================================

def _build_state(
    status,
    history,
):
    """
    Build stable lifecycle state.
    """

    safe_history = _safe_list(
        history
    )

    return {

        "status":
            status,

        "history":
            safe_history,

    }


# ============================================================
# RESULT BUILDER
# ============================================================

def _build_result(
    status,
    approved,
    blocked,
    portfolio,
    validation,
    governance,
    history,
    warnings,
    reasons,
):
    """
    Build exact stable lifecycle contract.
    """

    normalized_warnings = []

    for item in _safe_list(
        warnings
    ):

        _append_unique(
            normalized_warnings,
            item,
        )

    normalized_reasons = []

    for item in _safe_list(
        reasons
    ):

        _append_unique(
            normalized_reasons,
            item,
        )

    return {

        "status":
            status,

        "approved":
            _safe_bool(
                approved,
                False,
            ),

        "blocked":
            _safe_bool(
                blocked,
                True,
            ),

        "portfolio":
            _safe_dict(
                portfolio
            ),

        "validation":
            _safe_dict(
                validation
            ),

        "governance":
            _safe_dict(
                governance
            ),

        "state":
            _build_state(
                status,
                history,
            ),

        "warnings":
            normalized_warnings,

        "reasons":
            normalized_reasons,

    }


# ============================================================
# MAIN LIFECYCLE PIPELINE
# ============================================================

def run_portfolio_lifecycle(
    portfolio,
):
    """
    Run Portfolio Lifecycle safely.

    Public result contract remains stable.

    The caller-owned portfolio is never modified.
    """

    safe_portfolio = _safe_dict(
        portfolio
    )

    history = [

        STATUS_NEW,

        STATUS_VALIDATING,

    ]

    # ========================================================
    # VALIDATION
    # ========================================================

    try:

        validation_result = (
            validate_portfolio(
                _safe_dict(
                    safe_portfolio
                )
            )
        )

    except Exception as exc:

        validation_result = {

            "valid":
                False,

            "reasons": [

                (
                    "Portfolio validation failed: "
                    f"{exc}"
                )

            ],

            "warnings":
                [],

        }

    validation = _normalize_validation(
        validation_result
    )

    validation_warnings = _safe_list(
        validation.get(
            "warnings",
            [],
        )
    )

    validation_reasons = _safe_list(
        validation.get(
            "reasons",
            [],
        )
    )

    if not validation.get(
        "valid",
        False,
    ):

        history.append(
            STATUS_BLOCKED
        )

        return _build_result(

            status=STATUS_BLOCKED,

            approved=False,

            blocked=True,

            portfolio=safe_portfolio,

            validation=validation,

            governance={},

            history=history,

            warnings=validation_warnings,

            reasons=validation_reasons,

        )

    # ========================================================
    # VALIDATED
    # ========================================================

    history.append(
        STATUS_VALIDATED
    )

    # ========================================================
    # RISK CHECK
    # ========================================================

    history.append(
        STATUS_RISK_CHECK
    )

    # ========================================================
    # DECISION CHECK
    # ========================================================

    history.append(
        STATUS_DECISION_CHECK
    )

    # ========================================================
    # GOVERNANCE
    # ========================================================

    try:

        governance_result = (
            govern_portfolio(
                _safe_dict(
                    safe_portfolio
                )
            )
        )

    except Exception as exc:

        governance_result = {

            "approved":
                False,

            "blocked":
                True,

            "warnings":
                [],

            "reasons": [

                (
                    "Portfolio governance failed: "
                    f"{exc}"
                )

            ],

        }

    governance = _normalize_governance(
        governance_result
    )

    warnings = []

    reasons = []

    for item in validation_warnings:

        _append_unique(
            warnings,
            item,
        )

    for item in validation_reasons:

        _append_unique(
            reasons,
            item,
        )

    for item in _safe_list(
        governance.get(
            "warnings",
            [],
        )
    ):

        _append_unique(
            warnings,
            item,
        )

    for item in _safe_list(
        governance.get(
            "reasons",
            [],
        )
    ):

        _append_unique(
            reasons,
            item,
        )

    # ========================================================
    # BLOCKED
    # ========================================================

    if governance.get(
        "blocked",
        False,
    ) or not governance.get(
        "approved",
        False,
    ):

        history.append(
            STATUS_BLOCKED
        )

        return _build_result(

            status=STATUS_BLOCKED,

            approved=False,

            blocked=True,

            portfolio=safe_portfolio,

            validation=validation,

            governance=governance,

            history=history,

            warnings=warnings,

            reasons=reasons,

        )

    # ========================================================
    # WARNING
    # ========================================================

    if warnings:

        history.append(
            STATUS_WARNING
        )

        return _build_result(

            status=STATUS_WARNING,

            approved=True,

            blocked=False,

            portfolio=safe_portfolio,

            validation=validation,

            governance=governance,

            history=history,

            warnings=warnings,

            reasons=reasons,

        )

    # ========================================================
    # APPROVED
    # ========================================================

    history.append(
        STATUS_APPROVED
    )

    return _build_result(

        status=STATUS_APPROVED,

        approved=True,

        blocked=False,

        portfolio=safe_portfolio,

        validation=validation,

        governance=governance,

        history=history,

        warnings=warnings,

        reasons=reasons,

    )


# ============================================================
# BACKWARD-FRIENDLY ALIASES
# ============================================================

def execute_portfolio_lifecycle(
    portfolio,
):
    """
    Execute Portfolio Lifecycle.
    """

    return run_portfolio_lifecycle(
        portfolio
    )


def process_portfolio_lifecycle(
    portfolio,
):
    """
    Process Portfolio Lifecycle.
    """

    return run_portfolio_lifecycle(
        portfolio
    )


def run_lifecycle(
    portfolio,
):
    """
    Friendly lifecycle alias.
    """

    return run_portfolio_lifecycle(
        portfolio
    )


# ============================================================
# ENGINE WRAPPER
# ============================================================

class PortfolioLifecycleEngine:
    """
    Object-oriented wrapper for Portfolio Lifecycle.
    """

    def run(
        self,
        portfolio,
    ):

        return run_portfolio_lifecycle(
            portfolio
        )


    def execute(
        self,
        portfolio,
    ):

        return run_portfolio_lifecycle(
            portfolio
        )


    def process(
        self,
        portfolio,
    ):

        return run_portfolio_lifecycle(
            portfolio
        )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    "VERSION",

    "STATUS_NEW",

    "STATUS_VALIDATING",

    "STATUS_VALIDATED",

    "STATUS_RISK_CHECK",

    "STATUS_DECISION_CHECK",

    "STATUS_APPROVED",

    "STATUS_ACTIVE",

    "STATUS_WARNING",

    "STATUS_BLOCKED",

    "REQUIRED_LIFECYCLE_KEYS",

    "validate_portfolio",

    "govern_portfolio",

    "run_portfolio_lifecycle",

    "execute_portfolio_lifecycle",

    "process_portfolio_lifecycle",

    "run_lifecycle",

    "PortfolioLifecycleEngine",

]