"""
==========================================
SULTAN QUANT OS
Portfolio Lifecycle End-to-End Integration Tests
Version : 1.0.0
==========================================

Integration coverage:

- Portfolio Validation Engine
- Portfolio Risk Engine
- Portfolio Decision Engine
- Portfolio Governance Engine
- Portfolio Lifecycle Engine
- Portfolio State Engine

The purpose of these tests is to verify the
existing public contracts without modifying
production code.
"""

from copy import deepcopy

import engine.portfolio_lifecycle_engine as lifecycle

from engine.portfolio_state_engine import (
    STATE_ACTIVE,
    STATE_APPROVED,
    STATE_BLOCKED,
    STATE_NEW,
    STATE_REBALANCING,
    STATE_WARNING,
    activate_portfolio,
    create_portfolio_state,
    start_rebalancing,
)


# ==========================================================
# SAMPLE PORTFOLIO
# ==========================================================

def build_valid_portfolio():
    """
    Build a portfolio using the currently supported
    compatibility contract.
    """

    return {
        "portfolio": [
            {
                "strategy": "xau_strategy",
                "status": "SUCCESS",
            }
        ],

        "allocation": [
            {
                "strategy": "xau_strategy",
                "weight": 1.0,
            }
        ],

        "exposure": {
            "total": 1.0,
        },

        "risk": {
            "risk_score": 80,
            "approved": True,
        },

        "decision": {
            "approved": True,
        },

        "best_strategy": "xau_strategy",
    }


# ==========================================================
# BASIC LIFECYCLE CONTRACT
# ==========================================================

def test_lifecycle_returns_stable_contract():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert isinstance(
        result,
        dict,
    )

    assert lifecycle.REQUIRED_LIFECYCLE_KEYS.issubset(
        result.keys()
    )


def test_lifecycle_does_not_modify_input():

    portfolio = build_valid_portfolio()

    original = deepcopy(
        portfolio
    )

    lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert portfolio == original


def test_lifecycle_result_portfolio_is_independent():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    result["portfolio"]["integration_test"] = True

    assert (
        "integration_test"
        not in portfolio
    )


# ==========================================================
# VALID LIFECYCLE PATH
# ==========================================================

def test_valid_portfolio_reaches_approved_or_warning_state():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert result["blocked"] is False

    assert result["approved"] is True

    assert result["status"] in {
        lifecycle.STATUS_APPROVED,
        lifecycle.STATUS_WARNING,
    }


def test_valid_lifecycle_preserves_validation_result():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert isinstance(
        result["validation"],
        dict,
    )


def test_valid_lifecycle_preserves_governance_result():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert isinstance(
        result["governance"],
        dict,
    )


def test_valid_lifecycle_has_state_history():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    state = result["state"]

    assert isinstance(
        state,
        dict,
    )

    assert "status" in state

    assert "history" in state

    assert isinstance(
        state["history"],
        list,
    )

    assert len(
        state["history"]
    ) > 0


# ==========================================================
# BLOCKED PATH
# ==========================================================

def test_invalid_allocation_blocks_portfolio():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert result["blocked"] is True

    assert result["approved"] is False

    assert (
        result["status"]
        ==
        lifecycle.STATUS_BLOCKED
    )


def test_invalid_input_blocks_portfolio():

    result = lifecycle.run_portfolio_lifecycle(
        None
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["blocked"] is True

    assert result["approved"] is False


def test_blocked_lifecycle_contains_reason_or_validation_data():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert (
        len(result["reasons"]) > 0
        or bool(result["validation"])
    )


# ==========================================================
# LIFECYCLE -> STATE INTEGRATION
# ==========================================================

def test_approved_lifecycle_can_be_represented_by_state_engine():

    portfolio = build_valid_portfolio()

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    assert (
        lifecycle_result["approved"]
        is True
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"]
    )

    assert (
        state["state"]
        ==
        STATE_NEW
    )


def test_lifecycle_portfolio_can_enter_approved_state():

    portfolio = build_valid_portfolio()

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    assert (
        lifecycle_result["approved"]
        is True
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"],
        state=STATE_APPROVED,
    )

    assert (
        state["state"]
        ==
        STATE_APPROVED
    )


def test_approved_state_can_become_active():

    portfolio = build_valid_portfolio()

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"],
        state=STATE_APPROVED,
    )

    state = activate_portfolio(
        state
    )

    assert (
        state["state"]
        ==
        STATE_ACTIVE
    )


def test_active_portfolio_can_enter_rebalancing():

    portfolio = build_valid_portfolio()

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"],
        state=STATE_APPROVED,
    )

    state = activate_portfolio(
        state
    )

    state = start_rebalancing(
        state
    )

    assert (
        state["state"]
        ==
        STATE_REBALANCING
    )


# ==========================================================
# BLOCKED STATE PROTECTION
# ==========================================================

def test_blocked_lifecycle_must_not_be_activated():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    assert (
        lifecycle_result["blocked"]
        is True
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"],
        state=STATE_BLOCKED,
    )

    updated = activate_portfolio(
        state
    )

    assert (
        updated["state"]
        ==
        STATE_BLOCKED
    )

    assert (
        updated["is_valid_transition"]
        is False
    )


# ==========================================================
# RESULT INDEPENDENCE
# ==========================================================

def test_lifecycle_and_state_results_are_independent():

    portfolio = build_valid_portfolio()

    lifecycle_result = (
        lifecycle.run_portfolio_lifecycle(
            portfolio
        )
    )

    state = create_portfolio_state(
        lifecycle_result["portfolio"],
        state=STATE_APPROVED,
    )

    original_lifecycle = deepcopy(
        lifecycle_result
    )

    state["portfolio"]["changed"] = True

    assert (
        lifecycle_result
        ==
        original_lifecycle
    )
    