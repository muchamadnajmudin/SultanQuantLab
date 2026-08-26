"""
==========================================
SULTAN QUANT OS
Portfolio Rebalancing State Integration Tests
Version : 1.0.0
==========================================

Integration coverage:

- Portfolio State Engine
- Portfolio Rebalancing Engine

The tests verify that both engines can work
together without modifying existing production
contracts.
"""

from copy import deepcopy


from engine.portfolio_state_engine import (
    STATE_ACTIVE,
    STATE_APPROVED,
    STATE_BLOCKED,
    STATE_NEW,
    STATE_REBALANCING,
    STATE_VALIDATING,
    STATE_WARNING,
    activate_portfolio,
    create_portfolio_state,
    decision_passed,
    rebalancing_completed,
    risk_passed,
    set_warning,
    start_rebalancing,
    start_risk_check,
    start_validation,
    transition_portfolio_state,
    validation_passed,
)

from engine.portfolio_rebalancing_engine import (
    STATUS_NO_ACTION,
    STATUS_REBALANCE_REQUIRED,
    STATUS_WARNING,
    run_portfolio_rebalancing,
)


# ==========================================================
# SAMPLE PORTFOLIOS
# ==========================================================

def portfolio_no_action():

    return {
        "allocation": {
            "trend_following": 0.60,
            "price_action": 0.40,
        },

        "target_allocation": {
            "trend_following": 0.60,
            "price_action": 0.40,
        },
    }


def portfolio_rebalance_required():

    return {
        "allocation": {
            "trend_following": 0.60,
            "price_action": 0.40,
        },

        "target_allocation": {
            "trend_following": 0.50,
            "price_action": 0.50,
        },
    }


def portfolio_large_rebalance():

    return {
        "allocation": {
            "trend_following": 0.90,
            "price_action": 0.10,
        },

        "target_allocation": {
            "trend_following": 0.40,
            "price_action": 0.60,
        },
    }


# ==========================================================
# STATE HELPERS
# ==========================================================

def create_approved_state(
    portfolio,
):

    result = create_portfolio_state(
        portfolio
    )

    result = start_validation(
        result
    )

    result = validation_passed(
        result
    )

    result = start_risk_check(
        result
    )

    result = risk_passed(
        result
    )

    result = decision_passed(
        result
    )

    return result


def create_active_state(
    portfolio,
):

    result = create_approved_state(
        portfolio
    )

    result = activate_portfolio(
        result
    )

    return result


# ==========================================================
# NO ACTION
# ==========================================================

def test_no_action_does_not_require_rebalancing():

    portfolio = portfolio_no_action()

    result = run_portfolio_rebalancing(
        portfolio
    )

    assert (
        result["status"]
        ==
        STATUS_NO_ACTION
    )

    assert (
        result["rebalance_required"]
        is False
    )

    assert result["actions"] == []


def test_no_action_preserves_active_state():

    portfolio = portfolio_no_action()

    state = create_active_state(
        portfolio
    )

    original = deepcopy(
        state
    )

    rebalancing = run_portfolio_rebalancing(
        state["portfolio"]
    )

    assert (
        rebalancing["status"]
        ==
        STATUS_NO_ACTION
    )

    assert (
        rebalancing["rebalance_required"]
        is False
    )

    assert state == original

    assert (
        state["state"]
        ==
        STATE_ACTIVE
    )


# ==========================================================
# REBALANCE REQUIRED
# ==========================================================

def test_rebalance_required_can_enter_rebalancing_state():

    portfolio = portfolio_rebalance_required()

    state = create_active_state(
        portfolio
    )

    rebalancing = run_portfolio_rebalancing(
        state["portfolio"]
    )

    assert (
        rebalancing["status"]
        ==
        STATUS_REBALANCE_REQUIRED
    )

    assert (
        rebalancing["rebalance_required"]
        is True
    )

    updated_state = start_rebalancing(
        state
    )

    assert (
        updated_state["state"]
        ==
        STATE_REBALANCING
    )

    assert (
        updated_state["previous_state"]
        ==
        STATE_ACTIVE
    )


def test_rebalancing_can_complete_to_active():

    portfolio = portfolio_rebalance_required()

    state = create_active_state(
        portfolio
    )

    state = start_rebalancing(
        state
    )

    assert (
        state["state"]
        ==
        STATE_REBALANCING
    )

    state = rebalancing_completed(
        state
    )

    assert (
        state["state"]
        ==
        STATE_ACTIVE
    )

    assert (
        state["previous_state"]
        ==
        STATE_REBALANCING
    )


# ==========================================================
# LARGE REBALANCE WARNING
# ==========================================================

def test_large_rebalance_generates_warning():

    portfolio = portfolio_large_rebalance()

    result = run_portfolio_rebalancing(
        portfolio,
        large_rebalance_threshold=0.25,
    )

    assert (
        result["status"]
        ==
        STATUS_WARNING
    )

    assert (
        result["rebalance_required"]
        is True
    )

    assert len(
        result["warnings"]
    ) > 0


def test_active_portfolio_can_enter_warning_before_rebalancing():

    portfolio = portfolio_large_rebalance()

    state = create_active_state(
        portfolio
    )

    rebalancing = run_portfolio_rebalancing(
        state["portfolio"],
        large_rebalance_threshold=0.25,
    )

    assert (
        rebalancing["status"]
        ==
        STATUS_WARNING
    )

    state = set_warning(
        state
    )

    assert (
        state["state"]
        ==
        STATE_WARNING
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
# APPROVED STATE SUPPORT
# ==========================================================

def test_approved_portfolio_can_enter_rebalancing():

    portfolio = portfolio_rebalance_required()

    state = create_approved_state(
        portfolio
    )

    assert (
        state["state"]
        ==
        STATE_APPROVED
    )

    rebalancing = run_portfolio_rebalancing(
        state["portfolio"]
    )

    assert (
        rebalancing["rebalance_required"]
        is True
    )

    updated_state = start_rebalancing(
        state
    )

    assert (
        updated_state["state"]
        ==
        STATE_REBALANCING
    )


# ==========================================================
# INVALID STATE TRANSITION
# ==========================================================

def test_new_state_cannot_enter_rebalancing():

    portfolio = portfolio_rebalance_required()

    state = create_portfolio_state(
        portfolio
    )

    assert (
        state["state"]
        ==
        STATE_NEW
    )

    updated_state = start_rebalancing(
        state
    )

    assert (
        updated_state["state"]
        ==
        STATE_NEW
    )

    assert (
        updated_state["is_valid_transition"]
        is False
    )


def test_validating_state_cannot_enter_rebalancing():

    portfolio = portfolio_rebalance_required()

    state = create_portfolio_state(
        portfolio
    )

    state = start_validation(
        state
    )

    assert (
        state["state"]
        ==
        STATE_VALIDATING
    )

    updated_state = start_rebalancing(
        state
    )

    assert (
        updated_state["state"]
        ==
        STATE_VALIDATING
    )

    assert (
        updated_state["is_valid_transition"]
        is False
    )


# ==========================================================
# TERMINAL STATE PROTECTION
# ==========================================================

def test_blocked_state_cannot_rebalance():

    portfolio = portfolio_rebalance_required()

    state = create_portfolio_state(
        portfolio
    )

    state = transition_portfolio_state(
        state,
        STATE_VALIDATING,
    )

    state = transition_portfolio_state(
        state,
        STATE_BLOCKED,
    )

    # VALIDATING -> BLOCKED is not valid.
    # Therefore explicitly build a terminal state
    # through the supported lifecycle.

    state = create_portfolio_state(
        portfolio
    )

    state = start_validation(
        state
    )

    state = validation_passed(
        state
    )

    state = start_risk_check(
        state
    )

    from engine.portfolio_state_engine import (
        risk_failed,
    )

    state = risk_failed(
        state
    )

    assert (
        state["state"]
        ==
        STATE_BLOCKED
    )

    updated_state = start_rebalancing(
        state
    )

    assert (
        updated_state["state"]
        ==
        STATE_BLOCKED
    )

    assert (
        updated_state["is_valid_transition"]
        is False
    )


# ==========================================================
# INPUT IMMUTABILITY
# ==========================================================

def test_rebalancing_does_not_modify_state_input():

    portfolio = portfolio_rebalance_required()

    state = create_active_state(
        portfolio
    )

    original = deepcopy(
        state
    )

    run_portfolio_rebalancing(
        state["portfolio"]
    )

    assert state == original


def test_state_transition_does_not_modify_rebalancing_result():

    portfolio = portfolio_rebalance_required()

    rebalancing = run_portfolio_rebalancing(
        portfolio
    )

    original = deepcopy(
        rebalancing
    )

    state = create_active_state(
        portfolio
    )

    start_rebalancing(
        state
    )

    assert rebalancing == original


# ==========================================================
# CONTRACT INTEGRITY
# ==========================================================

def test_rebalancing_and_state_contracts_remain_independent():

    portfolio = portfolio_rebalance_required()

    state = create_active_state(
        portfolio
    )

    rebalancing = run_portfolio_rebalancing(
        state["portfolio"]
    )

    assert "state" in state

    assert "history" in state

    assert "actions" in rebalancing

    assert "rebalance_required" in rebalancing

    assert (
        state["portfolio"]
        ==
        rebalancing["portfolio"]
    )