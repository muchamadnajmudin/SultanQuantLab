"""
==========================================
SULTAN QUANT OS
Portfolio State Engine Tests
Version : 1.0.0
==========================================
"""

from copy import deepcopy

from engine.portfolio_state_engine import (
    REQUIRED_STATE_KEYS,
    STATE_ACTIVE,
    STATE_APPROVED,
    STATE_BLOCKED,
    STATE_DECISION_CHECK,
    STATE_NEW,
    STATE_REBALANCING,
    STATE_REJECTED,
    STATE_RISK_CHECK,
    STATE_VALIDATED,
    STATE_VALIDATING,
    STATE_WARNING,
    activate_portfolio,
    block_portfolio,
    can_transition,
    create_portfolio_state,
    create_state,
    decision_failed,
    decision_passed,
    get_available_transitions,
    initialize_portfolio_state,
    is_terminal_state,
    rebalancing_completed,
    required_state_keys,
    risk_failed,
    risk_passed,
    set_warning,
    start_rebalancing,
    start_risk_check,
    start_validation,
    transition_portfolio_state,
    transition_state,
    validation_failed,
    validation_passed,
)


def sample_portfolio():
    return {
        "portfolio": [
            {
                "strategy": "trend_following",
                "allocation": 0.6,
            },
            {
                "strategy": "price_action",
                "allocation": 0.4,
            },
        ],
        "best_strategy": "trend_following",
    }


def test_required_state_keys():

    assert required_state_keys() == REQUIRED_STATE_KEYS


def test_create_portfolio_state_returns_dictionary():

    result = create_portfolio_state()

    assert isinstance(result, dict)


def test_create_portfolio_state_contract():

    result = create_portfolio_state()

    assert set(result.keys()) == set(
        REQUIRED_STATE_KEYS
    )


def test_default_state_is_new():

    result = create_portfolio_state()

    assert result["state"] == STATE_NEW


def test_initial_state_is_valid():

    result = create_portfolio_state()

    assert result["is_valid_transition"] is True


def test_new_state_is_not_terminal():

    result = create_portfolio_state()

    assert result["is_terminal"] is False


def test_portfolio_is_preserved():

    portfolio = sample_portfolio()

    result = create_portfolio_state(
        portfolio=portfolio
    )

    assert result["portfolio"] == portfolio


def test_input_portfolio_is_not_modified():

    portfolio = sample_portfolio()

    original = deepcopy(portfolio)

    create_portfolio_state(
        portfolio=portfolio
    )

    assert portfolio == original


def test_result_portfolio_is_independent():

    portfolio = sample_portfolio()

    result = create_portfolio_state(
        portfolio=portfolio
    )

    result["portfolio"]["best_strategy"] = "changed"

    assert portfolio["best_strategy"] == (
        "trend_following"
    )


def test_invalid_initial_state_falls_back_to_new():

    result = create_portfolio_state(
        state="INVALID"
    )

    assert result["state"] == STATE_NEW


def test_none_portfolio_is_safe():

    result = create_portfolio_state(
        portfolio=None
    )

    assert result["portfolio"] == {}


def test_list_portfolio_is_safe():

    result = create_portfolio_state(
        portfolio=[]
    )

    assert result["portfolio"] == {}


def test_start_validation():

    result = create_portfolio_state()

    result = start_validation(result)

    assert result["state"] == STATE_VALIDATING

    assert result["previous_state"] == STATE_NEW

    assert result["is_valid_transition"] is True


def test_validation_passed():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    assert result["state"] == STATE_VALIDATED

    assert result["previous_state"] == STATE_VALIDATING


def test_validation_failed():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_failed(result)

    assert result["state"] == STATE_REJECTED

    assert result["is_terminal"] is True


def test_risk_check_lifecycle():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    assert result["state"] == STATE_RISK_CHECK


def test_risk_passed_moves_to_decision_check():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    assert result["state"] == STATE_DECISION_CHECK


def test_risk_failed_blocks_portfolio():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_failed(result)

    assert result["state"] == STATE_BLOCKED

    assert result["is_terminal"] is True


def test_decision_passed_approves_portfolio():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_passed(result)

    assert result["state"] == STATE_APPROVED


def test_decision_failed_blocks_portfolio():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_failed(result)

    assert result["state"] == STATE_BLOCKED


def test_approved_portfolio_can_be_activated():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_passed(result)

    result = activate_portfolio(result)

    assert result["state"] == STATE_ACTIVE


def test_active_portfolio_can_enter_warning():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_passed(result)

    result = activate_portfolio(result)

    result = set_warning(result)

    assert result["state"] == STATE_WARNING


def test_warning_portfolio_can_rebalance():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_passed(result)

    result = activate_portfolio(result)

    result = set_warning(result)

    result = start_rebalancing(result)

    assert result["state"] == STATE_REBALANCING


def test_rebalancing_completed_returns_active():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = start_risk_check(result)

    result = risk_passed(result)

    result = decision_passed(result)

    result = activate_portfolio(result)

    result = start_rebalancing(result)

    result = rebalancing_completed(result)

    assert result["state"] == STATE_ACTIVE


def test_invalid_transition_does_not_change_state():

    result = create_portfolio_state()

    result = transition_portfolio_state(
        result,
        STATE_ACTIVE,
    )

    assert result["state"] == STATE_NEW

    assert result["is_valid_transition"] is False


def test_invalid_target_state_is_safe():

    result = create_portfolio_state()

    result = transition_portfolio_state(
        result,
        "UNKNOWN_STATE",
    )

    assert result["state"] == STATE_NEW

    assert result["is_valid_transition"] is False


def test_terminal_state_cannot_transition():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_failed(result)

    result = transition_portfolio_state(
        result,
        STATE_VALIDATED,
    )

    assert result["state"] == STATE_REJECTED

    assert result["is_valid_transition"] is False


def test_history_tracks_transitions():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    assert len(result["history"]) == 2

    assert result["history"][0] == {
        "previous_state": STATE_NEW,
        "state": STATE_VALIDATING,
    }

    assert result["history"][1] == {
        "previous_state": STATE_VALIDATING,
        "state": STATE_VALIDATED,
    }


def test_can_transition():

    assert can_transition(
        STATE_NEW,
        STATE_VALIDATING,
    ) is True

    assert can_transition(
        STATE_NEW,
        STATE_ACTIVE,
    ) is False


def test_terminal_state_helper():

    assert is_terminal_state(
        STATE_BLOCKED
    ) is True

    assert is_terminal_state(
        STATE_REJECTED
    ) is True

    assert is_terminal_state(
        STATE_ACTIVE
    ) is False


def test_available_transitions():

    transitions = get_available_transitions(
        STATE_NEW
    )

    assert STATE_VALIDATING in transitions

    assert len(transitions) == 1


def test_unknown_state_has_no_available_transitions():

    transitions = get_available_transitions(
        "UNKNOWN"
    )

    assert transitions == []


def test_block_portfolio():

    result = create_portfolio_state()

    result = start_validation(result)

    result = validation_passed(result)

    result = block_portfolio(result)

    assert result["state"] == STATE_BLOCKED

    assert result["is_terminal"] is True


def test_create_state_alias():

    result = create_state()

    assert result["state"] == STATE_NEW


def test_transition_state_alias():

    result = create_state()

    result = transition_state(
        result,
        STATE_VALIDATING,
    )

    assert result["state"] == STATE_VALIDATING


def test_initialize_portfolio_state():

    portfolio = sample_portfolio()

    result = initialize_portfolio_state(
        portfolio
    )

    assert result["state"] == STATE_NEW

    assert result["portfolio"] == portfolio


def test_transition_does_not_modify_input():

    result = create_portfolio_state(
        sample_portfolio()
    )

    original = deepcopy(result)

    transition_portfolio_state(
        result,
        STATE_VALIDATING,
    )

    assert result == original


def test_transition_result_is_independent():

    result = create_portfolio_state(
        sample_portfolio()
    )

    updated = transition_portfolio_state(
        result,
        STATE_VALIDATING,
    )

    updated["portfolio"]["best_strategy"] = "changed"

    assert (
        result["portfolio"]["best_strategy"]
        == "trend_following"
    )