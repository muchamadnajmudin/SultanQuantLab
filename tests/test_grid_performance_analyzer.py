from copy import deepcopy

from engine.grid_performance_analyzer import (
    GridPerformanceAnalyzer,
    analyze_grid_performance,
)


def make_simulation(
    symbol="BTCUSDT",
    layers=3,
    completed=None,
    open_layers=None,
    pending=None,
    total_capital=1000,
    capital_deployed=600,
    realized_profit=None,
    unrealized_profit=None,
    total_profit=None,
):

    completed = (
        []
        if completed is None
        else completed
    )

    open_layers = (
        []
        if open_layers is None
        else open_layers
    )

    pending = (
        []
        if pending is None
        else pending
    )

    if realized_profit is None:
        realized_profit = sum(
            layer.get("profit", 0)
            for layer in completed
        )

    if unrealized_profit is None:
        unrealized_profit = sum(
            layer.get("profit", 0)
            for layer in open_layers
        )

    if total_profit is None:
        total_profit = (
            realized_profit
            + unrealized_profit
        )

    return {
        "symbol": symbol,
        "layers": layers,
        "total_capital": total_capital,
        "capital_deployed": capital_deployed,
        "realized_profit": realized_profit,
        "unrealized_profit": unrealized_profit,
        "total_profit": total_profit,
        "completed": completed,
        "open": open_layers,
        "pending": pending,
    }


# ==========================================================
# CREATION
# ==========================================================


def test_analyzer_creation():

    analyzer = GridPerformanceAnalyzer()

    assert analyzer is not None


# ==========================================================
# RESULT CONTRACT
# ==========================================================


def test_required_result_keys():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run([])

    required_keys = {
        "status",
        "metrics",
        "analyses",
        "processed_count",
        "failed_count",
        "input",
        "errors",
    }

    assert required_keys.issubset(
        result.keys()
    )


def test_required_metric_keys():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run([])

    required_keys = {
        "total_plans",
        "completed_plans",
        "open_plans",
        "pending_plans",
        "total_layers",
        "completed_layers",
        "open_layers",
        "pending_layers",
        "completion_rate",
        "total_capital",
        "capital_deployed",
        "realized_profit",
        "unrealized_profit",
        "total_profit",
        "realized_return",
        "total_return",
        "profit_per_completed_layer",
        "profit_per_plan",
    }

    assert required_keys.issubset(
        result["metrics"].keys()
    )


# ==========================================================
# EMPTY INPUT
# ==========================================================


def test_none_simulations():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(None)

    assert result["status"] == (
        analyzer.STATUS_EMPTY
    )

    assert result["analyses"] == []


def test_empty_simulations():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run([])

    assert result["status"] == (
        analyzer.STATUS_EMPTY
    )

    assert result["analyses"] == []


# ==========================================================
# INVALID CONTAINER
# ==========================================================


def test_invalid_simulation_container():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run({})

    assert result["status"] == (
        analyzer.STATUS_ERROR
    )


def test_string_simulation_container():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(
        "BTCUSDT"
    )

    assert result["status"] == (
        analyzer.STATUS_ERROR
    )


# ==========================================================
# SINGLE SIMULATION
# ==========================================================


def test_single_valid_simulation():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        completed=[
            {
                "layer": 1,
                "profit": 10,
            }
        ],
        open_layers=[
            {
                "layer": 2,
                "profit": 5,
            }
        ],
        pending=[
            {
                "layer": 3,
            }
        ],
        realized_profit=10,
        unrealized_profit=5,
        total_profit=15,
    )

    result = analyzer.run(
        [simulation]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert len(result["analyses"]) == 1


def test_symbol_is_normalized():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        symbol=" btc/usdt "
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0]["symbol"]
        == "BTCUSDT"
    )


# ==========================================================
# LAYER COUNTS
# ==========================================================


def test_completed_layer_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        completed=[
            {"layer": 1, "profit": 10},
            {"layer": 2, "profit": 20},
        ],
        pending=[
            {"layer": 3},
        ],
    )

    result = analyzer.run(
        [simulation]
    )

    analysis = result[
        "analyses"
    ][0]

    assert analysis[
        "completed_layers"
    ] == 2


def test_open_layer_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        completed=[
            {"layer": 1, "profit": 10},
        ],
        open_layers=[
            {"layer": 2, "profit": 3},
        ],
        pending=[
            {"layer": 3},
        ],
    )

    result = analyzer.run(
        [simulation]
    )

    analysis = result[
        "analyses"
    ][0]

    assert analysis[
        "open_layers"
    ] == 1


def test_pending_layer_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        pending=[
            {"layer": 1},
            {"layer": 2},
            {"layer": 3},
        ]
    )

    result = analyzer.run(
        [simulation]
    )

    analysis = result[
        "analyses"
    ][0]

    assert analysis[
        "pending_layers"
    ] == 3


# ==========================================================
# COMPLETION RATE
# ==========================================================


def test_completion_rate():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        layers=4,
        completed=[
            {"layer": 1, "profit": 10},
            {"layer": 2, "profit": 20},
        ],
        pending=[
            {"layer": 3},
            {"layer": 4},
        ],
    )

    result = analyzer.run(
        [simulation]
    )

    analysis = result[
        "analyses"
    ][0]

    assert (
        analysis["completion_rate"]
        == 0.5
    )


# ==========================================================
# CAPITAL
# ==========================================================


def test_total_capital_is_preserved():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        total_capital=5000
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "total_capital"
        ]
        == 5000
    )


def test_capital_deployed_is_preserved():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        capital_deployed=2500
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "capital_deployed"
        ]
        == 2500
    )


# ==========================================================
# PROFIT
# ==========================================================


def test_realized_profit_is_preserved():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        realized_profit=100
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "realized_profit"
        ]
        == 100
    )


def test_unrealized_profit_is_preserved():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        unrealized_profit=25
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "unrealized_profit"
        ]
        == 25
    )


def test_total_profit_is_preserved():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        total_profit=125
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "total_profit"
        ]
        == 125
    )


def test_profit_is_calculated_from_layers():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        completed=[
            {"layer": 1, "profit": 10},
            {"layer": 2, "profit": 20},
        ],
        open_layers=[
            {"layer": 3, "profit": 5},
        ],
        realized_profit=None,
        unrealized_profit=None,
        total_profit=None,
    )

    simulation.pop(
        "realized_profit"
    )

    simulation.pop(
        "unrealized_profit"
    )

    simulation.pop(
        "total_profit"
    )

    result = analyzer.run(
        [simulation]
    )

    analysis = result[
        "analyses"
    ][0]

    assert (
        analysis["realized_profit"]
        == 30
    )

    assert (
        analysis["unrealized_profit"]
        == 5
    )

    assert (
        analysis["total_profit"]
        == 35
    )


# ==========================================================
# RETURN
# ==========================================================


def test_realized_return():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        total_capital=1000,
        realized_profit=100,
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "realized_return"
        ]
        == 0.1
    )


def test_total_return():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        total_capital=1000,
        total_profit=150,
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "total_return"
        ]
        == 0.15
    )


# ==========================================================
# PROFIT PER LAYER
# ==========================================================


def test_profit_per_completed_layer():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        completed=[
            {"layer": 1, "profit": 20},
            {"layer": 2, "profit": 40},
        ],
        realized_profit=60,
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0][
            "profit_per_completed_layer"
        ]
        == 30
    )


# ==========================================================
# AGGREGATION
# ==========================================================


def test_multiple_simulations():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            symbol="BTCUSDT",
            layers=3,
            completed=[
                {"layer": 1, "profit": 10},
            ],
            pending=[
                {"layer": 2},
                {"layer": 3},
            ],
            realized_profit=10,
            total_profit=10,
        ),
        make_simulation(
            symbol="ETHUSDT",
            layers=3,
            completed=[
                {"layer": 1, "profit": 20},
                {"layer": 2, "profit": 30},
            ],
            pending=[
                {"layer": 3},
            ],
            realized_profit=50,
            total_profit=50,
        ),
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["metrics"][
            "total_plans"
        ]
        == 2
    )

    assert (
        result["metrics"][
            "total_layers"
        ]
        == 6
    )

    assert (
        result["metrics"][
            "completed_layers"
        ]
        == 3
    )

    assert (
        result["metrics"][
            "pending_layers"
        ]
        == 3
    )

    assert (
        result["metrics"][
            "total_profit"
        ]
        == 60
    )


def test_aggregate_completion_rate():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            layers=4,
            completed=[
                {"layer": 1, "profit": 10},
                {"layer": 2, "profit": 10},
            ],
            pending=[
                {"layer": 3},
                {"layer": 4},
            ],
            realized_profit=20,
            total_profit=20,
        ),
        make_simulation(
            layers=2,
            completed=[
                {"layer": 1, "profit": 10},
            ],
            pending=[
                {"layer": 2},
            ],
            realized_profit=10,
            total_profit=10,
        ),
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["metrics"][
            "completion_rate"
        ]
        == 0.5
    )


def test_aggregate_realized_return():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            total_capital=1000,
            realized_profit=100,
        ),
        make_simulation(
            total_capital=1000,
            realized_profit=50,
        ),
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["metrics"][
            "realized_return"
        ]
        == 0.075
    )


def test_aggregate_total_return():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            total_capital=1000,
            total_profit=100,
        ),
        make_simulation(
            total_capital=1000,
            total_profit=50,
        ),
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["metrics"][
            "total_return"
        ]
        == 0.075
    )


def test_profit_per_plan():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            total_profit=100
        ),
        make_simulation(
            total_profit=50
        ),
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["metrics"][
            "profit_per_plan"
        ]
        == 75
    )


# ==========================================================
# PLAN STATUS COUNTS
# ==========================================================


def test_completed_plan_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        layers=2,
        completed=[
            {"layer": 1, "profit": 10},
            {"layer": 2, "profit": 20},
        ],
        realized_profit=30,
        total_profit=30,
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["metrics"][
            "completed_plans"
        ]
        == 1
    )


def test_open_plan_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        layers=2,
        completed=[
            {"layer": 1, "profit": 10},
        ],
        open_layers=[
            {"layer": 2, "profit": 2},
        ],
        realized_profit=10,
        unrealized_profit=2,
        total_profit=12,
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["metrics"][
            "open_plans"
        ]
        == 1
    )


def test_pending_plan_count():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        layers=3,
        pending=[
            {"layer": 1},
            {"layer": 2},
            {"layer": 3},
        ]
    )

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["metrics"][
            "pending_plans"
        ]
        == 1
    )


# ==========================================================
# INVALID SIMULATION
# ==========================================================


def test_invalid_simulation():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )


def test_invalid_simulation_type():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(
        [
            "BTCUSDT"
        ]
    )

    assert result["status"] == (
        analyzer.STATUS_ERROR
    )

    assert result["failed_count"] == 1


def test_invalid_symbol():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        symbol=123
    )

    result = analyzer.run(
        [simulation]
    )

    assert result["failed_count"] == 1


def test_invalid_layers():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        layers=0
    )

    result = analyzer.run(
        [simulation]
    )

    assert result["failed_count"] == 1


def test_invalid_total_capital():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation(
        total_capital=-100
    )

    result = analyzer.run(
        [simulation]
    )

    assert result["failed_count"] == 1


def test_invalid_layer_collection():

    analyzer = GridPerformanceAnalyzer()

    simulation = make_simulation()

    simulation["completed"] = (
        "invalid"
    )

    result = analyzer.run(
        [simulation]
    )

    assert result["failed_count"] == 1


# ==========================================================
# PARTIAL FAILURE
# ==========================================================


def test_partial_failure():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            symbol="BTCUSDT",
            total_profit=10,
        ),
        "INVALID",
    ]

    result = analyzer.run(
        simulations
    )

    assert result["status"] == (
        analyzer.STATUS_PARTIAL
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1


def test_invalid_simulation_contains_index():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(
        [
            make_simulation(),
            "INVALID",
        ]
    )

    assert (
        result["errors"][0]["index"]
        == 1
    )


def test_invalid_simulation_contains_errors():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.run(
        [
            "INVALID"
        ]
    )

    assert len(
        result["errors"]
    ) == 1

    assert "error" in (
        result["errors"][0]
    )


# ==========================================================
# IMMUTABILITY
# ==========================================================


def test_input_is_not_modified():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            symbol=" btcusdt "
        )
    ]

    original = deepcopy(
        simulations
    )

    analyzer.run(
        simulations
    )

    assert simulations == original


def test_result_input_preserves_original_data():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            symbol=" btcusdt "
        )
    ]

    result = analyzer.run(
        simulations
    )

    assert (
        result["input"]
        == simulations
    )


def test_result_is_independent():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation()
    ]

    result = analyzer.run(
        simulations
    )

    result[
        "analyses"
    ][0]["symbol"] = "MODIFIED"

    second_result = analyzer.run(
        simulations
    )

    assert (
        second_result[
            "analyses"
        ][0]["symbol"]
        == "BTCUSDT"
    )


def test_analysis_is_independent_from_simulation():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation(
            completed=[
                {
                    "layer": 1,
                    "profit": 10,
                }
            ]
        )
    ]

    result = analyzer.run(
        simulations
    )

    result[
        "analyses"
    ][0][
        "completed"
    ][0]["profit"] = 999

    assert (
        simulations[0][
            "completed"
        ][0]["profit"]
        == 10
    )


def test_simulation_snapshot_is_independent():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation()
    ]

    result = analyzer.run(
        simulations
    )

    result[
        "analyses"
    ][0][
        "simulation"
    ]["symbol"] = "MODIFIED"

    assert (
        simulations[0]["symbol"]
        == "BTCUSDT"
    )


# ==========================================================
# ALIASES
# ==========================================================


def test_process_alias():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.process(
        [
            make_simulation()
        ]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )


def test_execute_alias():

    analyzer = GridPerformanceAnalyzer()

    result = analyzer.execute(
        [
            make_simulation()
        ]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )


def test_process_alias_matches_run():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation()
    ]

    assert (
        analyzer.process(
            simulations
        )
        == analyzer.run(
            simulations
        )
    )


def test_execute_alias_matches_run():

    analyzer = GridPerformanceAnalyzer()

    simulations = [
        make_simulation()
    ]

    assert (
        analyzer.execute(
            simulations
        )
        == analyzer.run(
            simulations
        )
    )


# ==========================================================
# CONVENIENCE FUNCTION
# ==========================================================


def test_convenience_function():

    result = analyze_grid_performance(
        [
            make_simulation()
        ]
    )

    assert result["status"] == (
        "SUCCESS"
    )

    assert len(
        result["analyses"]
    ) == 1


# ==========================================================
# TUPLE INPUT
# ==========================================================


def test_tuple_input():

    analyzer = GridPerformanceAnalyzer()

    simulations = (
        make_simulation(),
    )

    result = analyzer.run(
        simulations
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1