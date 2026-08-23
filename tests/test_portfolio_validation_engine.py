"""
==================================================
SULTAN QUANT OS
Portfolio Validation Engine Tests
==================================================

Purpose:

- Validate portfolio contract
- Validate portfolio strategy items
- Validate allocation
- Validate exposure
- Validate risk
- Validate decision
- Validate best strategy consistency
- Validate warning conditions
- Validate invalid contract handling
- Preserve stable validation contract
==================================================
"""

import pytest

from engine.portfolio_validation_engine import (
    STATUS_INVALID,
    STATUS_VALID,
    STATUS_WARNING,
    REQUIRED_PORTFOLIO_KEYS,
    validate_allocation,
    validate_best_strategy,
    validate_decision,
    validate_exposure,
    validate_institutional_portfolio,
    validate_portfolio,
    validate_portfolio_contract,
    validate_portfolio_items,
    validate_risk,
)


# ==================================================
# SAMPLE DATA
# ==================================================

def _successful_strategy(
    name="strategy_a",
):
    return {

        "name":
            name,

        "evaluation_status":
            "SUCCESS",

        "score":
            80.0,

        "statistics":
            {

                "total_trade":
                    10,

                "profit_factor":
                    2.0,

            },

    }


def _failed_strategy(
    name="strategy_failed",
):
    return {

        "name":
            name,

        "evaluation_status":
            "FAILED",

        "error":
            "strategy execution failed",

    }


def _valid_portfolio_result():

    strategy = _successful_strategy()

    return {

        "regime":
            "TRENDING",

        "portfolio":
            [

                strategy,

            ],

        "best":
            strategy,

        "allocation":
            [

                {

                    "name":
                        "strategy_a",

                    "allocation":
                        1.0,

                },

            ],

        "risk":
            {

                "risk_score":
                    20.0,

                "risk_level":
                    "LOW",

            },

        "decision":
            {

                "status":
                    "READY FOR FORWARD TEST",

            },

        "exposure":
            1.0,

        "summary":
            {

                "strategies":
                    1,

            },

    }


# ==================================================
# CONTRACT TESTS
# ==================================================

def test_required_portfolio_keys():

    result = _valid_portfolio_result()

    contract = validate_portfolio_contract(
        result
    )

    assert contract[
        "valid"
    ] is True

    assert contract[
        "missing_keys"
    ] == []

    assert len(
        REQUIRED_PORTFOLIO_KEYS
    ) == 8


def test_missing_portfolio_contract_keys():

    contract = validate_portfolio_contract(
        {}
    )

    assert contract[
        "valid"
    ] is False

    assert set(
        contract[
            "missing_keys"
        ]
    ) == set(
        REQUIRED_PORTFOLIO_KEYS
    )


def test_invalid_portfolio_contract_type():

    contract = validate_portfolio_contract(
        None
    )

    assert contract[
        "valid"
    ] is False

    assert set(
        contract[
            "missing_keys"
        ]
    ) == set(
        REQUIRED_PORTFOLIO_KEYS
    )


# ==================================================
# PORTFOLIO ITEM TESTS
# ==================================================

def test_valid_portfolio_items():

    check = validate_portfolio_items(

        [

            _successful_strategy(),

            _failed_strategy(),

        ]

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "total"
    ] == 2

    assert check[
        "successful"
    ] == 1

    assert check[
        "failed"
    ] == 1

    assert check[
        "invalid_items"
    ] == 0


def test_invalid_portfolio_items():

    check = validate_portfolio_items(

        [

            _successful_strategy(),

            None,

            "invalid",

        ]

    )

    assert check[
        "valid"
    ] is False

    assert check[
        "invalid_items"
    ] == 2


# ==================================================
# ALLOCATION TESTS
# ==================================================

def test_valid_allocation():

    check = validate_allocation(

        [

            {

                "name":
                    "strategy_a",

                "allocation":
                    0.6,

            },

            {

                "name":
                    "strategy_b",

                "allocation":
                    0.4,

            },

        ]

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "total_allocation"
    ] == pytest.approx(
        1.0
    )

    assert check[
        "count"
    ] == 2


def test_valid_dict_allocation():

    check = validate_allocation(

        {

            "strategy_a":
                0.7,

            "strategy_b":
                0.3,

        }

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "total_allocation"
    ] == pytest.approx(
        1.0
    )


def test_invalid_allocation_total():

    check = validate_allocation(

        [

            {

                "name":
                    "strategy_a",

                "allocation":
                    0.5,

            },

            {

                "name":
                    "strategy_b",

                "allocation":
                    0.2,

            },

        ]

    )

    assert check[
        "valid"
    ] is False


def test_negative_allocation():

    check = validate_allocation(

        [

            {

                "name":
                    "strategy_a",

                "allocation":
                    1.2,

            },

            {

                "name":
                    "strategy_b",

                "allocation":
                    -0.2,

            },

        ]

    )

    assert check[
        "valid"
    ] is False

    assert check[
        "negative_items"
    ] == 1


def test_empty_allocation_is_safe():

    check = validate_allocation(
        []
    )

    assert check[
        "valid"
    ] is True

    assert check[
        "total_allocation"
    ] == 0.0

    assert check[
        "count"
    ] == 0


# ==================================================
# EXPOSURE TESTS
# ==================================================

def test_valid_exposure():

    allocation = [

        {

            "name":
                "strategy_a",

            "allocation":
                0.6,

        },

        {

            "name":
                "strategy_b",

            "allocation":
                0.4,

        },

    ]

    check = validate_exposure(
        allocation,
        1.0,
    )

    assert check[
        "valid"
    ] is True

    assert check[
        "calculated_exposure"
    ] == pytest.approx(
        1.0
    )

    assert check[
        "reported_exposure"
    ] == pytest.approx(
        1.0
    )


def test_invalid_exposure():

    allocation = [

        {

            "name":
                "strategy_a",

            "allocation":
                0.6,

        },

        {

            "name":
                "strategy_b",

            "allocation":
                0.4,

        },

    ]

    check = validate_exposure(
        allocation,
        0.8,
    )

    assert check[
        "valid"
    ] is False


# ==================================================
# RISK TESTS
# ==================================================

def test_empty_risk_is_safe():

    check = validate_risk(
        {}
    )

    assert check[
        "valid"
    ] is True

    assert check[
        "empty"
    ] is True


def test_valid_risk_score():

    check = validate_risk(

        {

            "risk_score":
                25.0,

        }

    )

    assert check[
        "valid"
    ] is True


def test_invalid_risk_score():

    check = validate_risk(

        {

            "risk_score":
                -1.0,

        }

    )

    assert check[
        "valid"
    ] is False


# ==================================================
# DECISION TESTS
# ==================================================

def test_empty_decision_is_safe():

    check = validate_decision(
        {}
    )

    assert check[
        "valid"
    ] is True

    assert check[
        "empty"
    ] is True


def test_valid_decision():

    check = validate_decision(

        {

            "status":
                "READY FOR FORWARD TEST",

        }

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "empty"
    ] is False

    assert check[
        "status"
    ] == "READY FOR FORWARD TEST"


# ==================================================
# BEST STRATEGY TESTS
# ==================================================

def test_best_strategy_is_consistent():

    strategy = _successful_strategy()

    check = validate_best_strategy(

        [

            strategy,

            _failed_strategy(),

        ],

        strategy,

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "has_best"
    ] is True


def test_best_strategy_not_in_portfolio():

    check = validate_best_strategy(

        [

            _successful_strategy(),

        ],

        _successful_strategy(
            "unknown_strategy"
        ),

    )

    assert check[
        "valid"
    ] is False


def test_empty_best_when_no_success():

    check = validate_best_strategy(

        [

            _failed_strategy(),

        ],

        None,

    )

    assert check[
        "valid"
    ] is True

    assert check[
        "has_best"
    ] is False


def test_empty_best_with_success_is_invalid():

    check = validate_best_strategy(

        [

            _successful_strategy(),

        ],

        None,

    )

    assert check[
        "valid"
    ] is False


# ==================================================
# FULL VALIDATION
# ==================================================

def test_valid_institutional_portfolio():

    result = validate_institutional_portfolio(
        _valid_portfolio_result()
    )

    assert result[
        "valid"
    ] is True

    assert result[
        "status"
    ] == STATUS_VALID

    assert result[
        "errors"
    ] == []

    assert result[
        "warnings"
    ] == []

    assert set(
        result[
            "checks"
        ].keys()
    ) == {

        "contract",

        "portfolio",

        "allocation",

        "exposure",

        "risk",

        "decision",

        "best",

    }

    assert result[
        "summary"
    ][
        "portfolio_items"
    ] == 1

    assert result[
        "summary"
    ][
        "successful_strategies"
    ] == 1

    assert result[
        "summary"
    ][
        "allocation_total"
    ] == pytest.approx(
        1.0
    )


def test_invalid_contract_returns_stable_result():

    result = validate_institutional_portfolio(
        {}
    )

    assert result[
        "valid"
    ] is False

    assert result[
        "status"
    ] == STATUS_INVALID

    assert result[
        "errors"
    ]

    assert result[
        "summary"
    ][
        "portfolio_items"
    ] == 0


def test_invalid_exposure_invalidates_result():

    portfolio = _valid_portfolio_result()

    portfolio[
        "exposure"
    ] = 0.5

    result = validate_institutional_portfolio(
        portfolio
    )

    assert result[
        "valid"
    ] is False

    assert result[
        "status"
    ] == STATUS_INVALID

    assert result[
        "checks"
    ][
        "exposure"
    ][
        "valid"
    ] is False


def test_invalid_allocation_invalidates_result():

    portfolio = _valid_portfolio_result()

    portfolio[
        "allocation"
    ] = [

        {

            "name":
                "strategy_a",

            "allocation":
                0.5,

        }

    ]

    result = validate_institutional_portfolio(
        portfolio
    )

    assert result[
        "valid"
    ] is False

    assert result[
        "status"
    ] == STATUS_INVALID


def test_failed_strategies_are_allowed():

    portfolio = _valid_portfolio_result()

    portfolio[
        "portfolio"
    ] = [

        _failed_strategy(),

    ]

    portfolio[
        "best"
    ] = None

    portfolio[
        "allocation"
    ] = []

    portfolio[
        "exposure"
    ] = 0.0

    result = validate_institutional_portfolio(
        portfolio
    )

    assert result[
        "valid"
    ] is True

    assert result[
        "status"
    ] == STATUS_WARNING

    assert result[
        "summary"
    ][
        "successful_strategies"
    ] == 0

    assert result[
        "warnings"
    ]


def test_successful_strategy_without_allocation_warning():

    portfolio = _valid_portfolio_result()

    portfolio[
        "allocation"
    ] = []

    portfolio[
        "exposure"
    ] = 0.0

    result = validate_institutional_portfolio(
        portfolio
    )

    assert result[
        "valid"
    ] is True

    assert result[
        "status"
    ] == STATUS_WARNING

    assert result[
        "warnings"
    ]


# ==================================================
# BACKWARD COMPATIBILITY
# ==================================================

def test_validate_portfolio_alias():

    result = validate_portfolio(
        _valid_portfolio_result()
    )

    assert result[
        "valid"
    ] is True

    assert result[
        "status"
    ] == STATUS_VALID


def test_validation_does_not_modify_input():

    portfolio = _valid_portfolio_result()

    original_exposure = portfolio[
        "exposure"
    ]

    original_allocation = portfolio[
        "allocation"
    ][0][
        "allocation"
    ]

    validate_institutional_portfolio(
        portfolio
    )

    assert portfolio[
        "exposure"
    ] == original_exposure

    assert portfolio[
        "allocation"
    ][0][
        "allocation"
    ] == original_allocation