from copy import deepcopy

import pytest

from engine.grid_execution_simulator import (
    GridExecutionSimulator,
    simulate_grid_execution,
)


def make_plan(
    symbol="HYPEUSDT",
    reference_price=100.0,
    layers=3,
    take_profit=0.02,
    capitals=None,
):
    if capitals is None:
        capitals = [100.0] * layers

    entry_levels = []

    for index in range(layers):
        entry_levels.append(
            reference_price * (1 - 0.01 * index)
        )

    layer_plans = []

    for index in range(layers):
        entry_price = entry_levels[index]

        layer_plans.append({
            "layer": index + 1,
            "capital": capitals[index],
            "entry_price": entry_price,
            "take_profit_price": (
                entry_price * (1 + take_profit)
            ),
        })

    return {
        "symbol": symbol,
        "reference_price": reference_price,
        "layers": layers,
        "take_profit": take_profit,
        "entry_levels": entry_levels,
        "layer_plans": layer_plans,
    }


def test_simulator_creation():
    simulator = GridExecutionSimulator()

    assert isinstance(
        simulator,
        GridExecutionSimulator,
    )


def test_required_result_keys():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0],
    )

    assert set(result.keys()) == {
        "plans",
        "simulations",
        "completed",
        "open",
        "errors",
    }


def test_none_plans():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        None,
        [100.0],
    )

    assert result["plans"] == []
    assert result["errors"]


def test_empty_plans():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0],
    )

    assert result["plans"] == []
    assert result["simulations"] == []
    assert result["errors"] == []


def test_invalid_plan_container():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        {"symbol": "HYPEUSDT"},
        [100.0],
    )

    assert result["errors"]


def test_string_plan_container():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        "invalid",
        [100.0],
    )

    assert result["errors"]


def test_none_prices():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        None,
    )

    assert result["errors"]


def test_empty_prices():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [],
    )

    assert result["errors"]


def test_invalid_price_container():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        {"price": 100.0},
    )

    assert result["errors"]


def test_string_price_container():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        "100",
    )

    assert result["errors"]


def test_invalid_price_value():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0, "bad"],
    )

    assert result["errors"]


def test_boolean_price_invalid():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0, True],
    )

    assert result["errors"]


def test_zero_price_invalid():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0, 0],
    )

    assert result["errors"]


def test_negative_price_invalid():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [],
        [100.0, -1.0],
    )

    assert result["errors"]


def test_single_valid_plan():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert len(result["plans"]) == 1
    assert len(result["simulations"]) == 1
    assert result["errors"] == []


def test_multiple_valid_plans():
    simulator = GridExecutionSimulator()

    plan_one = make_plan(
        symbol="HYPEUSDT",
        layers=1,
    )

    plan_two = make_plan(
        symbol="BTCUSDT",
        layers=1,
    )

    result = simulator.run(
        [plan_one, plan_two],
        [100.0],
    )

    assert len(result["plans"]) == 2
    assert len(result["simulations"]) == 2


def test_symbol_is_normalized():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        symbol=" hypeusdt ",
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["plans"][0]["symbol"] == (
        "HYPEUSDT"
    )


def test_simulation_required_keys():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    simulation = result["simulations"][0]

    assert set(simulation.keys()) == {
        "symbol",
        "reference_price",
        "layers",
        "completed_layers",
        "open_layers",
        "pending_layers",
        "completed_count",
        "open_count",
        "pending_count",
        "total_profit",
    }


def test_layer_required_keys():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    layer = result["simulations"][0]["layers"][0]

    assert set(layer.keys()) == {
        "layer",
        "capital",
        "entry_price",
        "take_profit_price",
        "status",
        "opened_at",
        "closed_at",
        "opened_price",
        "closed_price",
        "profit",
    }


def test_first_layer_is_opened():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    layer = result["simulations"][0]["layers"][0]

    assert layer["status"] == "open"
    assert layer["opened_at"] == 0
    assert layer["opened_price"] == 100.0


def test_layer_remains_pending():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=2,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    layers = result["simulations"][0]["layers"]

    assert layers[0]["status"] == "open"
    assert layers[1]["status"] == "pending"


def test_multiple_layers_are_triggered():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=3,
    )

    result = simulator.run(
        [plan],
        [100.0, 99.0, 98.0],
    )

    simulation = result["simulations"][0]

    assert simulation["open_count"] == 3


def test_take_profit_closes_layer():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
        take_profit=0.02,
    )

    result = simulator.run(
        [plan],
        [100.0, 102.0],
    )

    layer = result["simulations"][0]["layers"][0]

    assert layer["status"] == "completed"
    assert layer["closed_at"] == 1
    assert layer["closed_price"] == 102.0


def test_completed_layer_is_added_to_result():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0, 102.0],
    )

    assert len(result["completed"]) == 1
    assert result["completed"][0]["symbol"] == (
        "HYPEUSDT"
    )


def test_open_layer_is_added_to_result():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert len(result["open"]) == 1
    assert result["open"][0]["symbol"] == (
        "HYPEUSDT"
    )


def test_profit_is_calculated():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
        capitals=[100.0],
    )

    result = simulator.run(
        [plan],
        [100.0, 102.0],
    )

    simulation = result["simulations"][0]

    assert simulation["total_profit"] == pytest.approx(
        2.0
    )


def test_completed_count():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0, 102.0],
    )

    simulation = result["simulations"][0]

    assert simulation["completed_count"] == 1
    assert simulation["open_count"] == 0
    assert simulation["pending_count"] == 0


def test_open_count():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    simulation = result["simulations"][0]

    assert simulation["completed_count"] == 0
    assert simulation["open_count"] == 1


def test_pending_count():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=2,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    simulation = result["simulations"][0]

    assert simulation["pending_count"] == 1


def test_invalid_plan():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [{"symbol": "HYPEUSDT"}],
        [100.0],
    )

    assert result["plans"] == []
    assert result["errors"]


def test_partial_failure():
    simulator = GridExecutionSimulator()

    valid_plan = make_plan(
        layers=1,
    )

    invalid_plan = {
        "symbol": "",
    }

    result = simulator.run(
        [valid_plan, invalid_plan],
        [100.0],
    )

    assert len(result["plans"]) == 1
    assert len(result["errors"]) == 1


def test_invalid_plan_contains_errors():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [{"symbol": ""}],
        [100.0],
    )

    assert result["errors"][0]["errors"]


def test_invalid_plan_contains_index():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [{"symbol": ""}],
        [100.0],
    )

    assert result["errors"][0]["index"] == 0


def test_missing_symbol_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    del plan["symbol"]

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_symbol_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["symbol"] = 123

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_reference_price_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["reference_price"] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layers_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layers"] = True

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_take_profit_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["take_profit"] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_entry_levels_length_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=2,
    )

    plan["entry_levels"] = [100.0]

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_entry_level_value_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["entry_levels"][0] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layer_plans_length_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=2,
    )

    plan["layer_plans"] = [
        plan["layer_plans"][0]
    ]

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layer_plan_type_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layer_plans"][0] = "invalid"

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layer_number_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layer_plans"][0]["layer"] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layer_capital_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layer_plans"][0]["capital"] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_layer_entry_price_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layer_plans"][0]["entry_price"] = -1

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_invalid_take_profit_price_fails():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    plan["layer_plans"][0][
        "take_profit_price"
    ] = 0

    result = simulator.run(
        [plan],
        [100.0],
    )

    assert result["errors"]


def test_input_is_not_modified():
    simulator = GridExecutionSimulator()

    plans = [
        make_plan(
            symbol=" hypeusdt ",
            layers=1,
        )
    ]

    original = deepcopy(plans)

    simulator.run(
        plans,
        [100.0, 102.0],
    )

    assert plans == original


def test_result_is_independent():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [make_plan(layers=1)],
        [100.0],
    )

    copied = deepcopy(result)

    result["plans"][0]["symbol"] = "CHANGED"

    assert copied["plans"][0]["symbol"] == (
        "HYPEUSDT"
    )


def test_simulation_is_independent_from_plan():
    simulator = GridExecutionSimulator()

    plan = make_plan(
        layers=1,
    )

    result = simulator.run(
        [plan],
        [100.0],
    )

    result["plans"][0]["symbol"] = "CHANGED"

    assert (
        result["simulations"][0]["symbol"]
        == "HYPEUSDT"
    )


def test_layer_result_is_independent():
    simulator = GridExecutionSimulator()

    result = simulator.run(
        [make_plan(layers=1)],
        [100.0],
    )

    result["simulations"][0]["layers"][0][
        "status"
    ] = "changed"

    assert result["open"][0]["status"] == "open"


def test_process_alias():
    simulator = GridExecutionSimulator()

    result = simulator.process(
        [make_plan(layers=1)],
        [100.0],
    )

    assert len(result["simulations"]) == 1


def test_execute_alias():
    simulator = GridExecutionSimulator()

    result = simulator.execute(
        [make_plan(layers=1)],
        [100.0],
    )

    assert len(result["simulations"]) == 1


def test_process_alias_matches_run():
    simulator = GridExecutionSimulator()

    plans = [make_plan(layers=1)]
    prices = [100.0]

    assert simulator.process(
        plans,
        prices,
    ) == simulator.run(
        plans,
        prices,
    )


def test_execute_alias_matches_run():
    simulator = GridExecutionSimulator()

    plans = [make_plan(layers=1)]
    prices = [100.0]

    assert simulator.execute(
        plans,
        prices,
    ) == simulator.run(
        plans,
        prices,
    )


def test_convenience_function():
    result = simulate_grid_execution(
        [make_plan(layers=1)],
        [100.0],
    )

    assert len(result["simulations"]) == 1


def test_tuple_input():
    plan = make_plan(
        layers=1,
    )

    result = simulate_grid_execution(
        (plan,),
        (100.0,),
    )

    assert len(result["simulations"]) == 1