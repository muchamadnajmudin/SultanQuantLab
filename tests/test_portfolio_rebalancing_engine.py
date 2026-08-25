"""
==========================================
SULTAN QUANT OS
Portfolio Rebalancing Engine Tests
==========================================

Tests:

- Rebalancing contract
- No action path
- Allocation drift detection
- Increase action
- Reduce action
- Remove action
- New strategy action
- Warning path
- Invalid input safety
- Input immutability
- Result independence
- Duplicate removal
- Status normalization
- Alias compatibility
- Engine wrapper
"""

from copy import deepcopy

import engine.portfolio_rebalancing_engine as rebalancing


# ============================================================
# SAMPLE PORTFOLIO
# ============================================================

def build_portfolio():

    return {

        "portfolio": [

            {
                "name": "strategy_alpha",
                "allocation": 0.60,
                "evaluation_status": "SUCCESS",
            },

            {
                "name": "strategy_beta",
                "allocation": 0.40,
                "evaluation_status": "SUCCESS",
            },

        ],

        "allocation": {

            "strategy_alpha": 0.60,
            "strategy_beta": 0.40,

        },

        "target_allocation": {

            "strategy_alpha": 0.60,
            "strategy_beta": 0.40,

        },

    }


# ============================================================
# CONTRACT
# ============================================================

def test_required_rebalancing_keys():

    result = rebalancing.run_portfolio_rebalancing(
        {}
    )

    assert (
        rebalancing.REQUIRED_REBALANCING_KEYS
        .issubset(
            result.keys()
        )
    )


def test_rebalancing_returns_dictionary():

    result = rebalancing.run_portfolio_rebalancing(
        {}
    )

    assert isinstance(
        result,
        dict,
    )


def test_rebalancing_contract_is_stable():

    result = rebalancing.run_portfolio_rebalancing(
        build_portfolio()
    )

    assert set(
        result.keys()
    ) == (
        rebalancing.REQUIRED_REBALANCING_KEYS
    )


# ============================================================
# NO ACTION
# ============================================================

def test_equal_allocation_requires_no_rebalance():

    result = rebalancing.run_portfolio_rebalancing(
        build_portfolio()
    )

    assert (
        result["rebalance_required"]
        is False
    )


def test_equal_allocation_has_no_actions():

    result = rebalancing.run_portfolio_rebalancing(
        build_portfolio()
    )

    assert result["actions"] == []


def test_equal_allocation_status_is_no_action():

    result = rebalancing.run_portfolio_rebalancing(
        build_portfolio()
    )

    assert (
        result["status"]
        ==
        rebalancing.STATUS_NO_ACTION
    )


# ============================================================
# INCREASE
# ============================================================

def test_lower_current_weight_requires_increase():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.40

    portfolio["target_allocation"][
        "strategy_alpha"
    ] = 0.60

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert (
        result["rebalance_required"]
        is True
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_alpha"
        )

    )

    assert (
        action["action"]
        ==
        rebalancing.ACTION_INCREASE
    )


# ============================================================
# REDUCE
# ============================================================

def test_higher_current_weight_requires_reduce():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.80

    portfolio["target_allocation"][
        "strategy_alpha"
    ] = 0.60

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_alpha"
        )

    )

    assert (
        action["action"]
        ==
        rebalancing.ACTION_REDUCE
    )


# ============================================================
# REMOVE
# ============================================================

def test_missing_target_strategy_requires_remove():

    portfolio = build_portfolio()

    del portfolio["target_allocation"][
        "strategy_beta"
    ]

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_beta"
        )

    )

    assert (
        action["action"]
        ==
        rebalancing.ACTION_REMOVE
    )


# ============================================================
# ADD
# ============================================================

def test_new_target_strategy_requires_add():

    portfolio = build_portfolio()

    portfolio["target_allocation"][
        "strategy_gamma"
    ] = 0.20

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_gamma"
        )

    )

    assert (
        action["action"]
        ==
        rebalancing.ACTION_ADD
    )


# ============================================================
# DRIFT
# ============================================================

def test_action_contains_current_weight():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.40

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_alpha"
        )

    )

    assert (
        action["current_weight"]
        ==
        0.40
    )


def test_action_contains_target_weight():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.40

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_alpha"
        )

    )

    assert (
        action["target_weight"]
        ==
        0.60
    )


def test_action_contains_drift():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.40

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    action = next(

        item

        for item in result["actions"]

        if (
            item["strategy"]
            ==
            "strategy_alpha"
        )

    )

    assert (
        action["drift"]
        ==
        0.20
    )


# ============================================================
# WARNING
# ============================================================

def test_warning_when_rebalance_is_large():

    portfolio = build_portfolio()

    portfolio["allocation"][
        "strategy_alpha"
    ] = 0.0

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert (
        result["status"]
        ==
        rebalancing.STATUS_WARNING
    )

    assert isinstance(
        result["warnings"],
        list,
    )


# ============================================================
# INVALID INPUT
# ============================================================

def test_none_input_is_safe():

    result = rebalancing.run_portfolio_rebalancing(
        None
    )

    assert isinstance(
        result,
        dict,
    )


def test_list_input_is_safe():

    result = rebalancing.run_portfolio_rebalancing(
        []
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["portfolio"] == {}


def test_string_input_is_safe():

    result = rebalancing.run_portfolio_rebalancing(
        "invalid"
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["portfolio"] == {}


# ============================================================
# IMMUTABILITY
# ============================================================

def test_input_portfolio_is_not_modified():

    portfolio = build_portfolio()

    original = deepcopy(
        portfolio
    )

    rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert portfolio == original


def test_result_portfolio_is_independent():

    portfolio = build_portfolio()

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    result["portfolio"][
        "changed"
    ] = True

    assert (
        "changed"
        not in portfolio
    )


# ============================================================
# NORMALIZATION
# ============================================================

def test_missing_allocation_is_safe():

    portfolio = build_portfolio()

    portfolio.pop(
        "allocation"
    )

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert isinstance(
        result["current_allocation"],
        dict,
    )


def test_missing_target_allocation_is_safe():

    portfolio = build_portfolio()

    portfolio.pop(
        "target_allocation"
    )

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert isinstance(
        result["target_allocation"],
        dict,
    )


def test_list_allocation_is_supported():

    portfolio = build_portfolio()

    portfolio["allocation"] = [

        {
            "strategy": "strategy_alpha",
            "weight": 0.60,
        },

        {
            "strategy": "strategy_beta",
            "weight": 0.40,
        },

    ]

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert (
        result["current_allocation"]
        ==
        {
            "strategy_alpha": 0.60,
            "strategy_beta": 0.40,
        }
    )


def test_list_target_allocation_is_supported():

    portfolio = build_portfolio()

    portfolio["target_allocation"] = [

        {
            "strategy": "strategy_alpha",
            "weight": 0.60,
        },

        {
            "strategy": "strategy_beta",
            "weight": 0.40,
        },

    ]

    result = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    assert (
        result["target_allocation"]
        ==
        {
            "strategy_alpha": 0.60,
            "strategy_beta": 0.40,
        }
    )


# ============================================================
# ALIAS
# ============================================================

def test_rebalance_portfolio_alias():

    portfolio = build_portfolio()

    result_a = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    result_b = rebalancing.rebalance_portfolio(
        portfolio
    )

    assert result_a == result_b


def test_process_rebalancing_alias():

    portfolio = build_portfolio()

    result_a = rebalancing.run_portfolio_rebalancing(
        portfolio
    )

    result_b = rebalancing.process_rebalancing(
        portfolio
    )

    assert result_a == result_b


# ============================================================
# ENGINE WRAPPER
# ============================================================

def test_engine_wrapper_run():

    engine = (
        rebalancing.PortfolioRebalancingEngine()
    )

    result = engine.run(
        build_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


def test_engine_wrapper_rebalance():

    engine = (
        rebalancing.PortfolioRebalancingEngine()
    )

    result = engine.rebalance(
        build_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


# ============================================================
# STATUS CONSTANTS
# ============================================================

def test_status_constants():

    assert (
        rebalancing.STATUS_NO_ACTION
        ==
        "NO_ACTION"
    )

    assert (
        rebalancing.STATUS_REBALANCE_REQUIRED
        ==
        "REBALANCE_REQUIRED"
    )

    assert (
        rebalancing.STATUS_WARNING
        ==
        "WARNING"
    )

    assert (
        rebalancing.STATUS_BLOCKED
        ==
        "BLOCKED"
    )


# ============================================================
# ACTION CONSTANTS
# ============================================================

def test_action_constants():

    assert (
        rebalancing.ACTION_ADD
        ==
        "ADD"
    )

    assert (
        rebalancing.ACTION_INCREASE
        ==
        "INCREASE"
    )

    assert (
        rebalancing.ACTION_REDUCE
        ==
        "REDUCE"
    )

    assert (
        rebalancing.ACTION_REMOVE
        ==
        "REMOVE"
    )