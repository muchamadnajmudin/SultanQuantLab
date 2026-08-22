"""
==========================================
SULTAN QUANT OS
Allocation Intelligence Tests
==========================================
"""

from strategies.intelligence.strategy_memory import (
    _memory,
)

from engine.allocation_engine import (
    build_allocation,
    calculate_adaptive_allocation_score,
)


def setup_function():

    _memory.memory.clear()


# ============================================================
# BASIC ALLOCATION
# ============================================================

def test_allocation_returns_candidates():

    results = [

        {
            "name": "price_action",

            "market_regime": "TRENDING",

            "evaluation_status": "SUCCESS",

            "score": 80,

            "statistics": {

                "profit_factor": 2.0,

                "expectancy": 1.5,

            },

        },

        {
            "name": "breakout",

            "market_regime": "TRENDING",

            "evaluation_status": "SUCCESS",

            "score": 70,

            "statistics": {

                "profit_factor": 1.8,

                "expectancy": 1.0,

            },

        },

    ]

    allocation = build_allocation(
        results,
        regime="TRENDING",
    )

    assert allocation

    assert len(
        allocation
    ) <= 3


# ============================================================
# ALLOCATION SUM
# ============================================================

def test_allocation_sum_is_one():

    results = [

        {
            "name": "price_action",

            "evaluation_status": "SUCCESS",

            "score": 80,

            "statistics": {

                "profit_factor": 2.0,

                "expectancy": 1.5,

            },

        },

        {
            "name": "breakout",

            "evaluation_status": "SUCCESS",

            "score": 70,

            "statistics": {

                "profit_factor": 1.8,

                "expectancy": 1.0,

            },

        },

    ]

    allocation = build_allocation(
        results
    )

    total = sum(
        item["allocation"]
        for item in allocation
    )

    assert total == 1.0


# ============================================================
# WEAK STRATEGY FILTER
# ============================================================

def test_weak_strategy_receives_no_allocation():

    results = [

        {
            "name": "weak",

            "evaluation_status": "SUCCESS",

            "score": 10,

            "statistics": {

                "profit_factor": 0.8,

                "expectancy": -1,

            },

        },

        {
            "name": "strong",

            "evaluation_status": "SUCCESS",

            "score": 80,

            "statistics": {

                "profit_factor": 2.0,

                "expectancy": 1.5,

            },

        },

    ]

    allocation = build_allocation(
        results
    )

    names = [
        item["name"]
        for item in allocation
    ]

    assert "strong" in names

    assert "weak" not in names


# ============================================================
# MEMORY IS REGIME SPECIFIC
# ============================================================

def test_memory_is_regime_specific():

    _memory.update(
        strategy="price_action",
        regime="TRENDING",
        profit=100,
        win=True,
    )

    _memory.update(
        strategy="price_action",
        regime="RANGE",
        profit=-100,
        win=False,
    )

    trending = build_allocation(
        [
            {
                "name": "price_action",

                "evaluation_status":
                    "SUCCESS",

                "score": 80,

                "statistics": {

                    "profit_factor": 2,

                    "expectancy": 1,

                },
            }
        ],
        regime="TRENDING",
    )

    ranging = build_allocation(
        [
            {
                "name": "price_action",

                "evaluation_status":
                    "SUCCESS",

                "score": 80,

                "statistics": {

                    "profit_factor": 2,

                    "expectancy": 1,

                },
            }
        ],
        regime="RANGE",
    )

    assert trending[0][
        "allocation_regime"
    ] == "TRENDING"

    assert ranging[0][
        "allocation_regime"
    ] == "RANGE"


# ============================================================
# MEMORY METADATA
# ============================================================

def test_memory_metadata_is_exposed():

    _memory.update(
        strategy="price_action",
        regime="TRENDING",
        profit=100,
        win=True,
    )

    results = [

        {
            "name": "price_action",

            "evaluation_status":
                "SUCCESS",

            "score": 80,

            "statistics": {

                "profit_factor": 2,

                "expectancy": 1,

            },

        }

    ]

    allocation = build_allocation(
        results,
        regime="TRENDING",
    )

    item = allocation[0]

    assert (
        "historical_weight"
        in item
    )

    assert (
        "historical_confidence"
        in item
    )

    assert (
        "memory_trades"
        in item
    )

    assert (
        "memory_wins"
        in item
    )

    assert (
        "memory_profit"
        in item
    )


# ============================================================
# ADAPTIVE SCORE
# ============================================================

def test_adaptive_score_is_positive():

    result = {

        "name": "price_action",

        "score": 80,

        "statistics": {

            "profit_factor": 2,

            "expectancy": 1,

        },

    }

    score = (
        calculate_adaptive_allocation_score(
            result,
            regime="TRENDING",
        )
    )

    assert score > 0


# ============================================================
# FAILED STRATEGY
# ============================================================

def test_failed_strategy_is_not_allocated():

    results = [

        {

            "name": "broken",

            "evaluation_status":
                "FAILED",

            "score": 100,

            "statistics": {

                "profit_factor": 10,

                "expectancy": 10,

            },

        },

        {

            "name": "valid",

            "evaluation_status":
                "SUCCESS",

            "score": 70,

            "statistics": {

                "profit_factor": 1.5,

                "expectancy": 1,

            },

        },

    ]

    allocation = build_allocation(
        results
    )

    names = [
        item["name"]
        for item in allocation
    ]

    assert "broken" not in names

    assert "valid" in names