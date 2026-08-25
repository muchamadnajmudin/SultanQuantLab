"""
==========================================
SULTAN QUANT OS
Portfolio Governance Engine
Version : 1.2.0
==========================================

Responsibilities:

- Validate institutional portfolio contracts
- Evaluate portfolio risk safely
- Evaluate institutional decision safely
- Combine validation, risk, and decision results
- Produce a single governance result
- Preserve strict backward compatibility
- Never mutate caller-owned input
- Fail safely when optional downstream engines fail

Architecture:

Institutional Portfolio
        +
Portfolio Validation
        +
Portfolio Risk
        +
Decision Engine
        ↓
Portfolio Governance
        ↓
APPROVED / WARNING / REJECTED


Important
---------

This module is an orchestration layer.

It does NOT replace:

    engine/portfolio_validation_engine.py
    risk/portfolio_risk.py
    engine/decision_engine.py

It only consumes their outputs or calls their
public interfaces when available.

No existing module contracts are modified.
"""

from copy import deepcopy


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
# PORTFOLIO RISK ENGINE
# ============================================================

try:

    from risk.portfolio_risk import (
        calculate_portfolio_risk,
    )

except ImportError:

    calculate_portfolio_risk = None


# ============================================================
# DECISION ENGINE
# ============================================================

try:

    from engine.decision_engine import (
        evaluate_decision,
    )

except ImportError:

    evaluate_decision = None


# ============================================================
# GOVERNANCE STATUS
# ============================================================

STATUS_APPROVED = "APPROVED"

STATUS_WARNING = "WARNING"

STATUS_REJECTED = "REJECTED"


# ============================================================
# GOVERNANCE CONTRACT
# ============================================================

REQUIRED_GOVERNANCE_KEYS = (

    "status",

    "approved",

    "portfolio",

    "validation",

    "risk",

    "decision",

    "governance",

)


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_dict(
    value,
):
    """
    Return a safe dictionary.
    """

    if isinstance(
        value,
        dict,
    ):

        return deepcopy(
            value
        )

    return {}


def _safe_list(
    value,
):
    """
    Return a safe list.
    """

    if isinstance(
        value,
        list,
    ):

        return deepcopy(
            value
        )

    if isinstance(
        value,
        tuple,
    ):

        return list(
            deepcopy(
                value
            )
        )

    return []


def _safe_bool(
    value,
    default=False,
):
    """
    Normalize boolean-like values safely.
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


def _safe_float(
    value,
    default=0.0,
):
    """
    Safely convert a value to float.
    """

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


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

    value = _safe_string(
        value,
        "",
    ).strip()

    if not value:

        return

    if value not in target:

        target.append(
            value
        )


# ============================================================
# VALIDATION NORMALIZATION
# ============================================================

def _normalize_validation_result(
    validation,
):
    """
    Normalize Portfolio Validation Engine output.
    """

    validation = _safe_dict(
        validation
    )

    valid = _safe_bool(
        validation.get(
            "valid",
            validation.get(
                "is_valid",
                False,
            ),
        ),
        False,
    )

    errors = _safe_list(
        validation.get(
            "errors",
            validation.get(
                "reasons",
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

    normalized_errors = []

    for item in errors:

        _append_unique(
            normalized_errors,
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

        "errors":
            normalized_errors,

        "warnings":
            normalized_warnings,

    }


# ============================================================
# RISK NORMALIZATION
# ============================================================

def _normalize_risk_result(
    risk,
):
    """
    Normalize Portfolio Risk Engine output.
    """

    risk = _safe_dict(
        risk
    )

    risk_score = _safe_float(
        risk.get(
            "risk_score",
            risk.get(
                "score",
                0.0,
            ),
        ),
        0.0,
    )

    risk_valid = risk.get(
        "valid",
        risk.get(
            "approved",
            None,
        ),
    )

    if risk_valid is None:

        risk_valid = True

    risk_valid = _safe_bool(
        risk_valid,
        True,
    )

    warnings = _safe_list(
        risk.get(
            "warnings",
            [],
        )
    )

    errors = _safe_list(
        risk.get(
            "errors",
            risk.get(
                "reasons",
                [],
            ),
        )
    )

    normalized_warnings = []

    for item in warnings:

        _append_unique(
            normalized_warnings,
            item,
        )

    normalized_errors = []

    for item in errors:

        _append_unique(
            normalized_errors,
            item,
        )

    return {

        "valid":
            risk_valid,

        "risk_score":
            risk_score,

        "warnings":
            normalized_warnings,

        "errors":
            normalized_errors,

        "raw":
            risk,

    }


# ============================================================
# DECISION NORMALIZATION
# ============================================================

def _normalize_decision_result(
    decision,
):
    """
    Normalize Decision Engine output.
    """

    decision = _safe_dict(
        decision
    )

    decision_value = decision.get(
        "decision",
        decision.get(
            "status",
            "",
        ),
    )

    decision_text = _safe_string(
        decision_value,
        "",
    ).upper().strip()

    explicit_approved = decision.get(
        "approved",
        None,
    )

    live_ready = decision.get(
        "live_ready",
        None,
    )

    if live_ready is not None:

        approved = _safe_bool(
            live_ready,
            False,
        )

    elif explicit_approved is not None:

        approved = _safe_bool(
            explicit_approved,
            False,
        )

    else:

        approved = (
            decision_text
            ==
            STATUS_APPROVED
        )

    if not decision_text:

        if approved:

            decision_text = STATUS_APPROVED

        else:

            decision_text = STATUS_REJECTED

    warnings = _safe_list(
        decision.get(
            "warnings",
            [],
        )
    )

    errors = _safe_list(
        decision.get(
            "errors",
            decision.get(
                "blocked_reasons",
                decision.get(
                    "failed_gates",
                    [],
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

    normalized_errors = []

    for item in errors:

        _append_unique(
            normalized_errors,
            item,
        )

    return {

        "status":
            decision_text,

        "approved":
            approved,

        "warnings":
            normalized_warnings,

        "errors":
            normalized_errors,

        "raw":
            decision,

    }


# ============================================================
# SAFE VALIDATION EXECUTION
# ============================================================

def _run_validation(
    portfolio,
):
    """
    Execute Portfolio Validation Engine safely.
    """

    if validate_institutional_portfolio is None:

        return {

            "valid": False,

            "errors": [
                "Portfolio validation engine unavailable"
            ],

            "warnings": [],

        }

    try:

        result = (
            validate_institutional_portfolio(
                portfolio
            )
        )

    except Exception as exc:

        return {

            "valid": False,

            "errors": [
                (
                    "Portfolio validation failed: "
                    f"{exc}"
                )
            ],

            "warnings": [],

        }

    return _normalize_validation_result(
        result
    )


# ============================================================
# SAFE RISK EXECUTION
# ============================================================

def _run_risk(
    portfolio,
):
    """
    Execute Portfolio Risk Engine safely.
    """

    if calculate_portfolio_risk is None:

        return {

            "valid": False,

            "risk_score": 0.0,

            "warnings": [],

            "errors": [
                "Portfolio risk engine unavailable"
            ],

            "raw": {},

        }

    try:

        result = (
            calculate_portfolio_risk(
                portfolio
            )
        )

    except Exception as exc:

        return {

            "valid": False,

            "risk_score": 0.0,

            "warnings": [],

            "errors": [
                (
                    "Portfolio risk evaluation failed: "
                    f"{exc}"
                )
            ],

            "raw": {},

        }

    return _normalize_risk_result(
        result
    )


# ============================================================
# INSTITUTIONAL DECISION COMPATIBILITY API
# ============================================================

def make_institutional_decision(
    portfolio,
):
    """
    Backward-compatible public decision wrapper.

    Existing callers and tests expect:

        make_institutional_decision(
            portfolio
        )

    The current Decision Engine uses:

        evaluate_decision(
            risk,
            results,
        )

    This adapter preserves the old governance-facing
    contract without changing engine/decision_engine.py.
    """

    portfolio = _safe_dict(
        portfolio
    )

    if evaluate_decision is None:

        return {

            "decision":
                STATUS_REJECTED,

            "approved":
                False,

            "warnings":
                [],

            "errors": [
                "Decision engine unavailable"
            ],

        }

    risk = _safe_dict(
        portfolio.get(
            "risk",
            {},
        )
    )

    results = _safe_list(
        portfolio.get(
            "portfolio",
            [],
        )
    )

    try:

        result = (
            evaluate_decision(
                risk,
                results,
            )
        )

    except Exception as exc:

        return {

            "decision":
                STATUS_REJECTED,

            "approved":
                False,

            "warnings":
                [],

            "errors": [
                (
                    "Institutional decision failed: "
                    f"{exc}"
                )
            ],

        }

    return _safe_dict(
        result
    )


# ============================================================
# SAFE DECISION EXECUTION
# ============================================================

def _run_decision(
    portfolio,
):
    """
    Execute Institutional Decision Engine safely.

    This function intentionally calls the public
    make_institutional_decision() compatibility API.

    This preserves backward compatibility with
    existing callers and allows downstream tests
    to monkeypatch the public decision interface.
    """

    try:

        result = (
            make_institutional_decision(
                portfolio
            )
        )

    except Exception as exc:

        return {

            "status":
                STATUS_REJECTED,

            "approved":
                False,

            "warnings":
                [],

            "errors": [
                (
                    "Institutional decision failed: "
                    f"{exc}"
                )
            ],

            "raw":
                {},

        }

    return _normalize_decision_result(
        result
    )


# ============================================================
# GOVERNANCE EVALUATION
# ============================================================

def _evaluate_governance(
    validation,
    risk,
    decision,
):
    """
    Combine all institutional governance gates.

    Priority:

        1. Validation failure -> REJECTED
        2. Risk failure       -> REJECTED
        3. Decision rejection -> REJECTED
        4. Warnings           -> WARNING
        5. Otherwise          -> APPROVED
    """

    blocked_reasons = []

    warnings = []

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not validation.get(
        "valid",
        False,
    ):

        errors = _safe_list(
            validation.get(
                "errors",
                [],
            )
        )

        if errors:

            for error in errors:

                _append_unique(
                    blocked_reasons,
                    error,
                )

        else:

            _append_unique(
                blocked_reasons,
                "Portfolio validation failed",
            )

    for warning in _safe_list(
        validation.get(
            "warnings",
            [],
        )
    ):

        _append_unique(
            warnings,
            warning,
        )

    # --------------------------------------------------------
    # RISK
    # --------------------------------------------------------

    if not risk.get(
        "valid",
        False,
    ):

        errors = _safe_list(
            risk.get(
                "errors",
                [],
            )
        )

        if errors:

            for error in errors:

                _append_unique(
                    blocked_reasons,
                    error,
                )

        else:

            _append_unique(
                blocked_reasons,
                "Portfolio risk validation failed",
            )

    for warning in _safe_list(
        risk.get(
            "warnings",
            [],
        )
    ):

        _append_unique(
            warnings,
            warning,
        )

    # --------------------------------------------------------
    # DECISION
    # --------------------------------------------------------

    if not decision.get(
        "approved",
        False,
    ):

        errors = _safe_list(
            decision.get(
                "errors",
                [],
            )
        )

        if errors:

            for error in errors:

                _append_unique(
                    blocked_reasons,
                    error,
                )

        else:

            status = _safe_string(
                decision.get(
                    "status",
                    STATUS_REJECTED,
                ),
                STATUS_REJECTED,
            )

            _append_unique(
                blocked_reasons,
                (
                    "Institutional decision: "
                    f"{status}"
                ),
            )

    for warning in _safe_list(
        decision.get(
            "warnings",
            [],
        )
    ):

        _append_unique(
            warnings,
            warning,
        )

    # ========================================================
    # FINAL STATUS
    # ========================================================

    if blocked_reasons:

        status = STATUS_REJECTED

        approved = False

    elif warnings:

        status = STATUS_WARNING

        approved = True

    else:

        status = STATUS_APPROVED

        approved = True

    return {

        "status":
            status,

        "approved":
            approved,

        "blocked_reasons":
            blocked_reasons,

        "warnings":
            warnings,

    }


# ============================================================
# BUILD GOVERNANCE RESULT
# ============================================================

def _build_result(
    portfolio,
    validation,
    risk,
    decision,
    governance,
):
    """
    Build the stable Portfolio Governance contract.
    """

    return {

        "status":
            governance.get(
                "status",
                STATUS_REJECTED,
            ),

        "approved":
            _safe_bool(
                governance.get(
                    "approved",
                    False,
                ),
                False,
            ),

        "portfolio":
            deepcopy(
                portfolio
            ),

        "validation":
            deepcopy(
                validation
            ),

        "risk":
            deepcopy(
                risk
            ),

        "decision":
            deepcopy(
                decision
            ),

        "governance":
            deepcopy(
                governance
            ),

    }


# ============================================================
# MAIN GOVERNANCE PIPELINE
# ============================================================

def run_portfolio_governance(
    portfolio,
):
    """
    Run the Institutional Portfolio Governance pipeline.

    The input portfolio is never modified.

    Existing engine contracts remain untouched.
    """

    safe_portfolio = _safe_dict(
        portfolio
    )

    validation = _run_validation(
        safe_portfolio
    )

    risk = _run_risk(
        safe_portfolio
    )

    decision = _run_decision(
        safe_portfolio
    )

    governance = _evaluate_governance(
        validation,
        risk,
        decision,
    )

    return _build_result(
        safe_portfolio,
        validation,
        risk,
        decision,
        governance,
    )


# ============================================================
# BACKWARD FRIENDLY ALIAS
# ============================================================

def govern_portfolio(
    portfolio,
):
    """
    Friendly alias for run_portfolio_governance().
    """

    return run_portfolio_governance(
        portfolio
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    "STATUS_APPROVED",

    "STATUS_WARNING",

    "STATUS_REJECTED",

    "REQUIRED_GOVERNANCE_KEYS",

    "make_institutional_decision",

    "run_portfolio_governance",

    "govern_portfolio",

]