"""
==========================================
SULTAN QUANT LAB
Tests : Grid Execution Planner
==========================================
"""

from copy import deepcopy

import pytest

from engine.grid_execution_planner import (
    GridExecutionPlanner,
    build_grid_execution_plans,
)


def create_valid_profile(
    symbol="HYPEUSDT",
    capital=1000.0,
    layers=3,
    take_profit=0.02,
    spacing=None,
    layer_capital=None,
):
    if spacing is None:
        spacing = [0.01] * max(
            layers - 1,
            0,
        )

    if layer_capital is None:
        layer_capital = [
            capital / layers
        ] * layers

    return {
        "symbol": symbol,
        "capital": capital,
        "layers": layers,
        "take_profit": take_profit,
        "spacing": spacing,
        "layer_capital": layer_capital,
    }


def test_planner_creation():
    planner = GridExecutionPlanner()

    assert isinstance(
        planner,
        GridExecutionPlanner,
    )


def test_default_reference_price():
    planner = GridExecutionPlanner(
        default_reference_price=100.0
    )

    assert planner.default_reference_price == 100.0


def test_default_reference_price_none():
    planner = GridExecutionPlanner()

    assert planner.default_reference_price is None


def test_invalid_default_reference_price_type():
    with pytest.raises(TypeError):
        GridExecutionPlanner(
            default_reference_price="100"
        )


def test_boolean_default_reference_price_invalid():
    with pytest.raises(TypeError):
        GridExecutionPlanner(
            default_reference_price=True
        )


def test_zero_default_reference_price_invalid():
    with pytest.raises(ValueError):
        GridExecutionPlanner(
            default_reference_price=0
        )


def test_negative_default_reference_price_invalid():
    with pytest.raises(ValueError):
        GridExecutionPlanner(
            default_reference_price=-100
        )


def test_required_result_keys():
    planner = GridExecutionPlanner()

    result = planner.run(
        [],
        reference_price=100.0,
    )

    assert set(result.keys()) == {
        "success",
        "plans",
        "errors",
        "processed",
        "failed",
    }


def test_none_profiles():
    planner = GridExecutionPlanner()

    result = planner.run(
        None,
        reference_price=100.0,
    )

    assert result["success"] is False
    assert result["plans"] == []
    assert result["failed"] == 1


def test_empty_profiles():
    planner = GridExecutionPlanner()

    result = planner.run(
        [],
        reference_price=100.0,
    )

    assert result["success"] is False
    assert result["plans"] == []
    assert result["processed"] == 0
    assert result["failed"] == 0


def test_invalid_profile_container():
    planner = GridExecutionPlanner()

    result = planner.run(
        {"symbol": "HYPEUSDT"},
        reference_price=100.0,
    )

    assert result["success"] is False
    assert result["plans"] == []
    assert result["failed"] == 1


def test_string_profile_container():
    planner = GridExecutionPlanner()

    result = planner.run(
        "invalid",
        reference_price=100.0,
    )

    assert result["success"] is False
    assert result["plans"] == []


def test_missing_reference_price():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()]
    )

    assert result["success"] is False
    assert result["plans"] == []


def test_runtime_reference_price():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True
    assert result["plans"][0][
        "reference_price"
    ] == 100.0


def test_constructor_reference_price():
    planner = GridExecutionPlanner(
        default_reference_price=200.0
    )

    result = planner.run(
        [create_valid_profile()]
    )

    assert result["success"] is True

    assert result["plans"][0][
        "reference_price"
    ] == 200.0


def test_runtime_reference_price_overrides_default():
    planner = GridExecutionPlanner(
        default_reference_price=200.0
    )

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True

    assert result["plans"][0][
        "reference_price"
    ] == 100.0


def test_invalid_runtime_reference_price_type():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price="100",
    )

    assert result["success"] is False


def test_boolean_reference_price_invalid():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=True,
    )

    assert result["success"] is False


def test_zero_reference_price_invalid():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=0,
    )

    assert result["success"] is False


def test_negative_reference_price_invalid():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=-100,
    )

    assert result["success"] is False


def test_single_valid_profile():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True
    assert len(result["plans"]) == 1
    assert result["processed"] == 1
    assert result["failed"] == 0


def test_multiple_valid_profiles():
    planner = GridExecutionPlanner()

    profiles = [
        create_valid_profile(
            symbol="HYPEUSDT"
        ),
        create_valid_profile(
            symbol="BTCUSDT"
        ),
    ]

    result = planner.run(
        profiles,
        reference_price=100.0,
    )

    assert result["success"] is True
    assert len(result["plans"]) == 2
    assert result["processed"] == 2


def test_symbol_is_normalized():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        symbol=" hypeusdt "
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["plans"][0][
        "symbol"
    ] == "HYPEUSDT"


def test_plan_required_keys():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    plan = result["plans"][0]

    assert set(plan.keys()) == {
        "symbol",
        "reference_price",
        "capital",
        "layers",
        "take_profit",
        "spacing",
        "layer_capital",
        "entry_levels",
        "layer_plans",
        "profile",
    }


def test_entry_levels_length_matches_layers():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=4,
        spacing=[
            0.01,
            0.02,
            0.03,
        ],
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    levels = result["plans"][0][
        "entry_levels"
    ]

    assert len(levels) == 4


def test_first_entry_level_equals_reference_price():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    levels = result["plans"][0][
        "entry_levels"
    ]

    assert levels[0] == 100.0


def test_entry_levels_follow_spacing():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=3,
        spacing=[
            0.01,
            0.02,
        ],
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    levels = result["plans"][0][
        "entry_levels"
    ]

    assert levels[0] == pytest.approx(
        100.0
    )

    assert levels[1] == pytest.approx(
        99.0
    )

    assert levels[2] == pytest.approx(
        97.02
    )


def test_one_layer_profile():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=1,
        spacing=[],
        layer_capital=[1000.0],
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is True

    levels = result["plans"][0][
        "entry_levels"
    ]

    assert levels == [100.0]


def test_layer_plans_length_matches_layers():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=4,
        spacing=[
            0.01,
            0.01,
            0.01,
        ],
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    layer_plans = result["plans"][0][
        "layer_plans"
    ]

    assert len(layer_plans) == 4


def test_layer_numbers_are_added():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    layer_plans = result["plans"][0][
        "layer_plans"
    ]

    assert [
        layer["layer"]
        for layer in layer_plans
    ] == [1, 2, 3]


def test_layer_capital_is_preserved():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=3,
        layer_capital=[
            200.0,
            300.0,
            500.0,
        ],
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    layer_plans = result["plans"][0][
        "layer_plans"
    ]

    assert [
        layer["capital"]
        for layer in layer_plans
    ] == [
        200.0,
        300.0,
        500.0,
    ]


def test_take_profit_price_is_calculated():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        take_profit=0.02
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    layer_plan = result["plans"][0][
        "layer_plans"
    ][0]

    assert layer_plan[
        "take_profit_price"
    ] == pytest.approx(
        102.0
    )


def test_second_layer_take_profit_price():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        layers=2,
        spacing=[0.01],
        layer_capital=[
            500.0,
            500.0,
        ],
        take_profit=0.02,
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    second_layer = result["plans"][0][
        "layer_plans"
    ][1]

    assert second_layer[
        "entry_price"
    ] == pytest.approx(
        99.0
    )

    assert second_layer[
        "take_profit_price"
    ] == pytest.approx(
        100.98
    )


def test_invalid_profile():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    del profile["symbol"]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False
    assert result["plans"] == []
    assert result["failed"] == 1


def test_partial_failure():
    planner = GridExecutionPlanner()

    valid = create_valid_profile()

    invalid = {
        "symbol": "BTCUSDT"
    }

    result = planner.run(
        [
            valid,
            invalid,
        ],
        reference_price=100.0,
    )

    assert result["success"] is False
    assert len(result["plans"]) == 1
    assert result["processed"] == 2
    assert result["failed"] == 1


def test_invalid_profile_contains_errors():
    planner = GridExecutionPlanner()

    result = planner.run(
        [
            {
                "symbol": "HYPEUSDT"
            }
        ],
        reference_price=100.0,
    )

    assert len(result["errors"]) == 1
    assert result["errors"][0][
        "errors"
    ]


def test_invalid_profile_contains_index():
    planner = GridExecutionPlanner()

    result = planner.run(
        [
            create_valid_profile(),
            {
                "symbol": "INVALID"
            },
        ],
        reference_price=100.0,
    )

    assert result["errors"][0][
        "index"
    ] == 1


def test_missing_profile_field_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    del profile["capital"]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_symbol_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        symbol=""
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_capital_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        capital=0
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_layers_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    profile["layers"] = True

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_take_profit_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile(
        take_profit=0
    )

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_spacing_length_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    profile["spacing"] = [0.01]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_spacing_value_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    profile["spacing"] = [
        0.01,
        0,
    ]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_layer_capital_length_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        500.0,
        500.0,
    ]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_invalid_layer_capital_value_fails():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        500.0,
        0,
        500.0,
    ]

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    assert result["success"] is False


def test_input_is_not_modified():
    planner = GridExecutionPlanner()

    profiles = [
        create_valid_profile()
    ]

    original = deepcopy(
        profiles
    )

    planner.run(
        profiles,
        reference_price=100.0,
    )

    assert profiles == original


def test_result_is_independent():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    result["plans"][0][
        "symbol"
    ] = "CHANGED"

    fresh_result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert fresh_result["plans"][0][
        "symbol"
    ] == "HYPEUSDT"


def test_plan_is_independent_from_profile():
    planner = GridExecutionPlanner()

    profile = create_valid_profile()

    result = planner.run(
        [profile],
        reference_price=100.0,
    )

    profile["symbol"] = "CHANGED"

    assert result["plans"][0][
        "symbol"
    ] == "HYPEUSDT"


def test_layer_plan_is_independent():
    planner = GridExecutionPlanner()

    result = planner.run(
        [create_valid_profile()],
        reference_price=100.0,
    )

    result["plans"][0][
        "layer_plans"
    ][0]["capital"] = 99999

    assert result["plans"][0][
        "layer_capital"
    ][0] != 99999


def test_process_alias():
    planner = GridExecutionPlanner()

    result = planner.process(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True


def test_execute_alias():
    planner = GridExecutionPlanner()

    result = planner.execute(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True


def test_process_alias_matches_run():
    planner = GridExecutionPlanner()

    profiles = [
        create_valid_profile()
    ]

    run_result = planner.run(
        profiles,
        reference_price=100.0,
    )

    process_result = planner.process(
        profiles,
        reference_price=100.0,
    )

    assert run_result == process_result


def test_execute_alias_matches_run():
    planner = GridExecutionPlanner()

    profiles = [
        create_valid_profile()
    ]

    run_result = planner.run(
        profiles,
        reference_price=100.0,
    )

    execute_result = planner.execute(
        profiles,
        reference_price=100.0,
    )

    assert run_result == execute_result


def test_convenience_function():
    result = build_grid_execution_plans(
        [create_valid_profile()],
        reference_price=100.0,
    )

    assert result["success"] is True
    assert len(result["plans"]) == 1


def test_tuple_input():
    planner = GridExecutionPlanner()

    profiles = (
        create_valid_profile(),
    )

    result = planner.run(
        profiles,
        reference_price=100.0,
    )

    assert result["success"] is True
    assert len(result["plans"]) == 1