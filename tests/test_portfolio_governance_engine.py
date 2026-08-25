"""
==========================================
SULTAN QUANT OS
Portfolio Governance Engine Tests
==========================================

Tests:

- Governance contract
- Approval path
- Warning path
- Validation rejection
- Risk rejection
- Decision rejection
- Combined rejection reasons
- Input immutability
- Safe failure handling
- Alias compatibility
"""

from copy import deepcopy

import engine.portfolio_governance_engine as governance


# ============================================================
# SAMPLE PORTFOLIO
# ============================================================

def build_portfolio():
    """
    Build a minimal institutional portfolio fixture.
    """

    return {

        "portfolio": [

            {

                "name":
                    "strategy_alpha",

                "allocation":
                    1.0,

                "evaluation_status":
                    "SUCCESS",

            }

        ],

        "best_strategy": {

            "name":
                "strategy_alpha",

        },

        "allocation": {

            "strategy_alpha":
                1.0,

        },

        "exposure": {

            "strategy_alpha":
                1.0,

        },

    }


# ============================================================
# MONKEYPATCH HELPERS
# ============================================================

def patch_success(
    monkeypatch,
):
    """
    Patch all downstream engines with successful results.
    """

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "valid":
                True,

            "errors":
                [],

            "warnings":
                [],

        },

    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "valid":
                True,

            "risk_score":
                10.0,

            "warnings":
                [],

            "errors":
                [],

        },

    )

    monkeypatch.setattr(

        governance,

        "make_institutional_decision",

        lambda portfolio: {

            "decision":
                "APPROVED",

            "warnings":
                [],

            "errors":
                [],

        },

    )


# ============================================================
# GOVERNANCE CONTRACT
# ============================================================

def test_required_governance_keys():

    result = governance.run_portfolio_governance(
        {}
    )

    for key in governance.REQUIRED_GOVERNANCE_KEYS:

        assert key in result


def test_governance_returns_dictionary():

    result = governance.run_portfolio_governance(
        {}
    )

    assert isinstance(
        result,
        dict,
    )


def test_governance_contract_is_stable(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert set(
        governance.REQUIRED_GOVERNANCE_KEYS
    ).issubset(
        result.keys()
    )


# ============================================================
# APPROVAL
# ============================================================

def test_portfolio_is_approved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_APPROVED

    assert result["approved"] is True

    assert result["governance"]["approved"] is True


def test_approved_portfolio_has_no_blocks(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["governance"]["blocked_reasons"] == []


# ============================================================
# WARNING
# ============================================================

def test_warning_portfolio_is_not_rejected(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "valid":
                True,

            "errors":
                [],

            "warnings":
                [
                    "Allocation concentration warning"
                ],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_WARNING

    assert result["approved"] is True

    assert (
        "Allocation concentration warning"
        in
        result["governance"]["warnings"]
    )


def test_risk_warning_is_preserved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "valid":
                True,

            "risk_score":
                50.0,

            "warnings":
                [
                    "Portfolio risk elevated"
                ],

            "errors":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_WARNING

    assert (
        "Portfolio risk elevated"
        in
        result["governance"]["warnings"]
    )


def test_decision_warning_is_preserved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "make_institutional_decision",

        lambda portfolio: {

            "decision":
                "APPROVED",

            "warnings":
                [
                    "Limited confidence"
                ],

            "errors":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_WARNING

    assert (
        "Limited confidence"
        in
        result["governance"]["warnings"]
    )


# ============================================================
# VALIDATION REJECTION
# ============================================================

def test_validation_failure_rejects_portfolio(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "valid":
                False,

            "errors":
                [
                    "Invalid allocation"
                ],

            "warnings":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_REJECTED

    assert result["approved"] is False

    assert (
        "Invalid allocation"
        in
        result["governance"]["blocked_reasons"]
    )


def test_validation_engine_exception_rejects(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    def raise_error(
        portfolio,
    ):

        raise RuntimeError(
            "Validation crash"
        )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        raise_error,

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is False

    assert result["status"] == governance.STATUS_REJECTED

    assert any(

        "Portfolio validation failed"

        in

        reason

        for reason

        in

        result["governance"]["blocked_reasons"]

    )


# ============================================================
# RISK REJECTION
# ============================================================

def test_risk_failure_rejects_portfolio(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "valid":
                False,

            "risk_score":
                95.0,

            "errors":
                [
                    "Portfolio risk too high"
                ],

            "warnings":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_REJECTED

    assert result["approved"] is False

    assert (
        "Portfolio risk too high"
        in
        result["governance"]["blocked_reasons"]
    )


def test_risk_engine_exception_rejects(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    def raise_error(
        portfolio,
    ):

        raise RuntimeError(
            "Risk crash"
        )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        raise_error,

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is False

    assert any(

        "Portfolio risk evaluation failed"

        in

        reason

        for reason

        in

        result["governance"]["blocked_reasons"]

    )


# ============================================================
# DECISION REJECTION
# ============================================================

def test_decision_rejection_blocks_portfolio(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "make_institutional_decision",

        lambda portfolio: {

            "decision":
                "REJECTED",

            "errors":
                [
                    "Institutional gate failed"
                ],

            "warnings":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["status"] == governance.STATUS_REJECTED

    assert result["approved"] is False

    assert (
        "Institutional gate failed"
        in
        result["governance"]["blocked_reasons"]
    )


def test_decision_engine_exception_rejects(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    def raise_error(
        portfolio,
    ):

        raise RuntimeError(
            "Decision crash"
        )

    monkeypatch.setattr(

        governance,

        "make_institutional_decision",

        raise_error,

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is False

    assert result["status"] == governance.STATUS_REJECTED

    assert any(

        "Institutional decision failed"

        in

        reason

        for reason

        in

        result["governance"]["blocked_reasons"]

    )


# ============================================================
# MULTIPLE FAILURES
# ============================================================

def test_multiple_failures_are_combined(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "valid":
                False,

            "errors":
                [
                    "Invalid allocation"
                ],

            "warnings":
                [],

        },

    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "valid":
                False,

            "risk_score":
                100.0,

            "errors":
                [
                    "Risk limit exceeded"
                ],

            "warnings":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    reasons = result[
        "governance"
    ][
        "blocked_reasons"
    ]

    assert "Invalid allocation" in reasons

    assert "Risk limit exceeded" in reasons

    assert result["status"] == governance.STATUS_REJECTED


# ============================================================
# DUPLICATE REASONS
# ============================================================

def test_duplicate_reasons_are_removed(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "valid":
                False,

            "errors":
                [
                    "Shared failure"
                ],

            "warnings":
                [],

        },

    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "valid":
                False,

            "risk_score":
                100.0,

            "errors":
                [
                    "Shared failure"
                ],

            "warnings":
                [],

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    reasons = result[
        "governance"
    ][
        "blocked_reasons"
    ]

    assert reasons.count(
        "Shared failure"
    ) == 1


# ============================================================
# INPUT IMMUTABILITY
# ============================================================

def test_input_portfolio_is_not_modified(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    portfolio = build_portfolio()

    original = deepcopy(
        portfolio
    )

    governance.run_portfolio_governance(
        portfolio
    )

    assert portfolio == original


def test_result_portfolio_is_independent_copy(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    portfolio = build_portfolio()

    result = governance.run_portfolio_governance(
        portfolio
    )

    result["portfolio"]["portfolio"][0][
        "name"
    ] = "changed"

    assert (

        portfolio["portfolio"][0]["name"]

        ==

        "strategy_alpha"

    )


# ============================================================
# INVALID INPUT
# ============================================================

def test_none_input_is_safe(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        None
    )

    assert isinstance(
        result,
        dict,
    )

    assert "status" in result


def test_list_input_is_safe(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        []
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["portfolio"] == {}


def test_string_input_is_safe(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        "invalid"
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["portfolio"] == {}


# ============================================================
# NORMALIZATION
# ============================================================

def test_decision_status_fallback_from_approved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "make_institutional_decision",

        lambda portfolio: {

            "approved":
                True,

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is True

    assert result["status"] == governance.STATUS_APPROVED


def test_risk_approved_alias_is_supported(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "calculate_portfolio_risk",

        lambda portfolio: {

            "approved":
                True,

            "risk_score":
                10,

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is True


def test_validation_is_valid_alias_supported(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    monkeypatch.setattr(

        governance,

        "validate_institutional_portfolio",

        lambda portfolio: {

            "is_valid":
                True,

        },

    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert result["approved"] is True


# ============================================================
# ALIAS
# ============================================================

def test_govern_portfolio_alias(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    portfolio = build_portfolio()

    result_a = governance.run_portfolio_governance(
        portfolio
    )

    result_b = governance.govern_portfolio(
        portfolio
    )

    assert result_a == result_b


# ============================================================
# RAW RESULTS ARE PRESERVED
# ============================================================

def test_risk_raw_result_is_preserved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert "raw" in result["risk"]


def test_decision_raw_result_is_preserved(
    monkeypatch,
):

    patch_success(
        monkeypatch
    )

    result = governance.run_portfolio_governance(
        build_portfolio()
    )

    assert "raw" in result["decision"]


# ============================================================
# PUBLIC STATUS CONSTANTS
# ============================================================

def test_status_constants():

    assert governance.STATUS_APPROVED == "APPROVED"

    assert governance.STATUS_WARNING == "WARNING"

    assert governance.STATUS_REJECTED == "REJECTED"