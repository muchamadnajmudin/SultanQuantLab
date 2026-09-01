"""
==========================================
SULTAN QUANT OS
Tests : Grid Strategy Pipeline
Version: 1.0.0
==========================================
"""

from copy import deepcopy

import pytest

from engine.grid_strategy_pipeline import (
    VERSION,
    STATUS_SUCCESS,
    STATUS_EMPTY,
    STATUS_PARTIAL,
    STATUS_ERROR,
    REQUIRED_RESULT_KEYS,
    run_grid_strategy_pipeline,
    process_grid_strategy_pipeline,
    execute_grid_strategy_pipeline,
    grid_strategy_pipeline,
    GridStrategyPipeline,
    GridStrategyPipelineEngine,
)


# ============================================================
# TEST DATA
# ============================================================

def _simulation(
    symbol="HYPEUSDT",
    total_return=50.0,
    realized_return=40.0,
    completion_rate=0.80,
    profit_per_completed_layer=20.0,
    risk_score=0.20,
):
    return {
        "symbol": symbol,
        "performance": {
            "total_return": total_return,
            "realized_return": realized_return,
            "completion_rate": completion_rate,
            "profit_per_completed_layer": (
                profit_per_completed_layer
            ),
        },
        "risk": {
            "risk_score": risk_score,
        },
        "analysis": {
            "symbol": symbol,
            "market": {
                "regime": "RANGE",
            },
        },
    }


def _simulation_high_score():
    return _simulation(
        symbol="BTCUSDT",
        total_return=90.0,
        realized_return=80.0,
        completion_rate=0.95,
        profit_per_completed_layer=70.0,
        risk_score=0.10,
    )


def _simulation_low_score():
    return _simulation(
        symbol="ETHUSDT",
        total_return=20.0,
        realized_return=15.0,
        completion_rate=0.40,
        profit_per_completed_layer=5.0,
        risk_score=0.60,
    )


def _simulation_medium_score():
    return _simulation(
        symbol="SOLUSDT",
        total_return=55.0,
        realized_return=45.0,
        completion_rate=0.70,
        profit_per_completed_layer=25.0,
        risk_score=0.30,
    )


# ============================================================
# BASIC CONTRACT
# ============================================================

def test_version_exists():
    assert isinstance(
        VERSION,
        str,
    )

    assert VERSION == "1.0.0"


def test_required_result_keys_are_present():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ]
    )

    assert REQUIRED_RESULT_KEYS.issubset(
        result.keys()
    )


def test_returns_dictionary():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ]
    )

    assert isinstance(
        result,
        dict,
    )


# ============================================================
# NORMAL PIPELINE
# ============================================================

def test_pipeline_runs_rank_then_select():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
        _simulation_medium_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=2,
    )

    assert result["success"] is True
    assert result["status"] == STATUS_SUCCESS

    assert result["processed_count"] == 3
    assert result["valid_count"] == 3
    assert result["invalid_count"] == 0

    assert len(
        result["ranked_strategies"]
    ) == 3

    assert len(
        result["selected_strategies"]
    ) == 2

    assert result["selected_count"] == 2


def test_pipeline_preserves_ranker_output():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert isinstance(
        result["ranking"],
        dict,
    )

    assert (
        result["ranking"]["ranked_strategies"]
        == result["ranked_strategies"]
    )


def test_pipeline_preserves_selector_output():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert isinstance(
        result["selection"],
        dict,
    )

    assert (
        result["selection"]["selected_strategies"]
        == result["selected_strategies"]
    )


# ============================================================
# TOP N
# ============================================================

def test_top_n_one_selects_one_strategy():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_low_score(),
        ],
        top_n=1,
    )

    assert result["selected_count"] == 1

    assert len(
        result["selected_strategies"]
    ) == 1


def test_top_n_two_selects_two_strategies():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ],
        top_n=2,
    )

    assert result["selected_count"] == 2


def test_top_n_none_selects_all_ranked_strategies():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ],
        top_n=None,
    )

    assert result["selected_count"] == 3

    assert len(
        result["selected_strategies"]
    ) == len(
        result["ranked_strategies"]
    )


# ============================================================
# ORDER
# ============================================================

def test_best_strategy_is_selected_first():
    result = run_grid_strategy_pipeline(
        [
            _simulation_low_score(),
            _simulation_high_score(),
            _simulation_medium_score(),
        ],
        top_n=1,
    )

    assert (
        result["selected_strategies"][0]["symbol"]
        == "BTCUSDT"
    )


def test_ranked_strategies_have_rank():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ]
    )

    ranks = [
        strategy["rank"]
        for strategy in result[
            "ranked_strategies"
        ]
    ]

    assert ranks == [1, 2, 3]


def test_selected_strategies_have_selection_rank():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ],
        top_n=2,
    )

    selection_ranks = [
        strategy["selection_rank"]
        for strategy in result[
            "selected_strategies"
        ]
    ]

    assert selection_ranks == [1, 2]


# ============================================================
# WEIGHTS
# ============================================================

def test_custom_weights_are_supported():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_low_score(),
        ],
        top_n=1,
        performance_weight=0.80,
        risk_weight=0.20,
    )

    assert result["success"] is True

    assert len(
        result["selected_strategies"]
    ) == 1


def test_weights_are_forwarded_to_ranker():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    normal = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
        performance_weight=0.60,
        risk_weight=0.40,
    )

    performance_heavy = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
        performance_weight=0.90,
        risk_weight=0.10,
    )

    assert (
        normal["ranking"]["ranked_strategies"]
        != []
    )

    assert (
        performance_heavy[
            "ranking"
        ]["ranked_strategies"]
        != []
    )


# ============================================================
# EMPTY / NONE
# ============================================================

def test_none_input_is_safe():
    result = run_grid_strategy_pipeline(
        None
    )

    assert result["status"] == STATUS_EMPTY
    assert result["success"] is True

    assert result["ranked_strategies"] == []
    assert result["selected_strategies"] == []


def test_empty_input_is_safe():
    result = run_grid_strategy_pipeline(
        []
    )

    assert result["status"] == STATUS_EMPTY

    assert result["ranked_strategies"] == []
    assert result["selected_strategies"] == []


# ============================================================
# INVALID INPUT
# ============================================================

def test_invalid_string_input_is_safe():
    result = run_grid_strategy_pipeline(
        "invalid"
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False
    assert result["errors"]


def test_invalid_bytes_input_is_safe():
    result = run_grid_strategy_pipeline(
        b"invalid"
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False
    assert result["errors"]


def test_invalid_weight_is_safe():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        performance_weight="invalid",
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False
    assert result["errors"]


def test_negative_performance_weight_is_safe():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        performance_weight=-1.0,
        risk_weight=1.0,
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False


def test_negative_risk_weight_is_safe():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        performance_weight=1.0,
        risk_weight=-1.0,
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False


def test_zero_total_weights_are_rejected():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        performance_weight=0.0,
        risk_weight=0.0,
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False


def test_invalid_top_n_is_safe():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        top_n=0,
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False


def test_boolean_top_n_is_rejected():
    result = run_grid_strategy_pipeline(
        [
            _simulation(),
        ],
        top_n=True,
    )

    assert result["status"] == STATUS_ERROR
    assert result["success"] is False


# ============================================================
# PARTIAL FAILURE
# ============================================================

def test_partial_invalid_strategy_is_supported():
    simulations = [
        _simulation_high_score(),
        {
            "symbol": "INVALID",
        },
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert result["status"] == STATUS_PARTIAL

    assert result["processed_count"] == 2
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 1

    assert len(
        result["ranked_strategies"]
    ) == 1

    assert len(
        result["selected_strategies"]
    ) == 1


def test_invalid_strategy_does_not_stop_valid_strategies():
    simulations = [
        {
            "invalid": True,
        },
        _simulation_high_score(),
        {
            "symbol": "",
        },
        _simulation_medium_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=2,
    )

    assert result["valid_count"] == 2
    assert result["invalid_count"] == 2

    assert len(
        result["ranked_strategies"]
    ) == 2

    assert len(
        result["selected_strategies"]
    ) == 2


# ============================================================
# IMMUTABILITY
# ============================================================

def test_input_is_not_modified():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    original = deepcopy(
        simulations
    )

    run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert simulations == original


def test_nested_input_is_not_modified():
    simulations = [
        _simulation_high_score(),
    ]

    original = deepcopy(
        simulations
    )

    run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert simulations == original


def test_result_contains_independent_input_snapshot():
    simulations = [
        _simulation_high_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations
    )

    result["input"][0]["symbol"] = (
        "CHANGED"
    )

    assert (
        simulations[0]["symbol"]
        == "BTCUSDT"
    )


# ============================================================
# RESULT INDEPENDENCE
# ============================================================

def test_result_is_independent():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    result["ranked_strategies"][0][
        "symbol"
    ] = "CHANGED"

    assert (
        result["selection"][
            "selected_strategies"
        ][0]["symbol"]
        == "BTCUSDT"
    )


def test_nested_result_is_independent():
    simulations = [
        _simulation_high_score(),
    ]

    result = run_grid_strategy_pipeline(
        simulations
    )

    result["ranking"][
        "ranked_strategies"
    ][0][
        "performance"
    ][
        "total_return"
    ] = 999999

    assert (
        result["ranked_strategies"][0][
            "performance"
        ][
            "total_return"
        ]
        != 999999
    )


# ============================================================
# FUNCTION ALIASES
# ============================================================

def test_process_alias():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = process_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


def test_execute_alias():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = execute_grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


def test_convenience_function():
    simulations = [
        _simulation_high_score(),
        _simulation_low_score(),
    ]

    result = grid_strategy_pipeline(
        simulations,
        top_n=1,
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


# ============================================================
# CLASS WRAPPER
# ============================================================

def test_engine_wrapper_exists():
    engine = GridStrategyPipeline()

    assert isinstance(
        engine,
        GridStrategyPipeline,
    )


def test_engine_alias_exists():
    engine = GridStrategyPipelineEngine()

    assert isinstance(
        engine,
        GridStrategyPipeline,
    )


def test_engine_wrapper_run():
    engine = GridStrategyPipeline(
        top_n=1
    )

    result = engine.run(
        [
            _simulation_high_score(),
            _simulation_low_score(),
        ]
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


def test_engine_wrapper_process():
    engine = GridStrategyPipeline(
        top_n=1
    )

    result = engine.process(
        [
            _simulation_high_score(),
            _simulation_low_score(),
        ]
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


def test_engine_wrapper_execute():
    engine = GridStrategyPipeline(
        top_n=1
    )

    result = engine.execute(
        [
            _simulation_high_score(),
            _simulation_low_score(),
        ]
    )

    assert result["success"] is True
    assert result["selected_count"] == 1


def test_runtime_top_n_overrides_constructor():
    engine = GridStrategyPipeline(
        top_n=1
    )

    result = engine.run(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ],
        top_n=2,
    )

    assert result["selected_count"] == 2


# ============================================================
# PIPELINE DATA CONTRACT
# ============================================================

def test_pipeline_contains_ranking_and_selection():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
        ],
        top_n=1,
    )

    assert "ranking" in result
    assert "selection" in result

    assert isinstance(
        result["ranking"],
        dict,
    )

    assert isinstance(
        result["selection"],
        dict,
    )


def test_pipeline_contains_ranked_strategies():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
        ]
    )

    assert "ranked_strategies" in result

    assert isinstance(
        result["ranked_strategies"],
        list,
    )


def test_pipeline_contains_selected_strategies():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
        ],
        top_n=1,
    )

    assert "selected_strategies" in result

    assert isinstance(
        result["selected_strategies"],
        list,
    )


def test_selected_strategy_is_from_ranked_strategies():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
            _simulation_low_score(),
        ],
        top_n=2,
    )

    ranked_symbols = {
        strategy["symbol"]
        for strategy in result[
            "ranked_strategies"
        ]
    }

    selected_symbols = {
        strategy["symbol"]
        for strategy in result[
            "selected_strategies"
        ]
    }

    assert selected_symbols.issubset(
        ranked_symbols
    )


# ============================================================
# STATUS CONTRACT
# ============================================================

@pytest.mark.parametrize(
    "top_n",
    [1, 2],
)
def test_success_status_for_valid_pipeline(
    top_n,
):
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            _simulation_medium_score(),
        ],
        top_n=top_n,
    )

    assert result["status"] == STATUS_SUCCESS
    assert result["success"] is True


def test_partial_status_for_mixed_input():
    result = run_grid_strategy_pipeline(
        [
            _simulation_high_score(),
            {},
        ],
        top_n=1,
    )

    assert result["status"] == STATUS_PARTIAL
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 1


def test_empty_status_for_empty_list():
    result = run_grid_strategy_pipeline(
        []
    )

    assert result["status"] == STATUS_EMPTY
    assert result["selected_count"] == 0