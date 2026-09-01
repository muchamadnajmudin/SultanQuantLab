from copy import deepcopy

from engine.grid_risk_analyzer import (
    GridRiskAnalyzer,
    analyze_grid_risk,
)


def make_simulation():

    return {
        "symbol": "BTCUSDT",
        "layers": 3,
        "total_capital": 1000.0,
        "realized_profit": 30.0,
        "unrealized_profit": 10.0,
        "layers_detail": [
            {
                "layer": 1,
                "status": "COMPLETED",
                "capital": 300.0,
                "profit": 20.0,
            },
            {
                "layer": 2,
                "status": "OPEN",
                "capital": 300.0,
                "profit": 10.0,
            },
            {
                "layer": 3,
                "status": "PENDING",
                "capital": 400.0,
                "profit": 0.0,
            },
        ],
    }


def test_analyzer_creation():

    analyzer = GridRiskAnalyzer()

    assert analyzer is not None


def test_default_thresholds():

    analyzer = GridRiskAnalyzer()

    assert analyzer.max_safe_utilization == 0.80
    assert analyzer.max_safe_exposure == 0.80


def test_custom_thresholds():

    analyzer = GridRiskAnalyzer(
        max_safe_utilization=0.70,
        max_safe_exposure=0.60,
    )

    assert analyzer.max_safe_utilization == 0.70
    assert analyzer.max_safe_exposure == 0.60


def test_invalid_threshold():

    try:
        GridRiskAnalyzer(
            max_safe_utilization=0
        )
        assert False
    except ValueError:
        assert True


def test_required_result_keys():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run([])

    required_keys = {
        "status",
        "analyses",
        "processed_count",
        "failed_count",
        "errors",
        "input",
    }

    assert required_keys.issubset(
        result.keys()
    )


def test_required_metric_keys():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    metrics = result["analyses"][0]

    required_keys = {
        "symbol",
        "layers",
        "completed_layers",
        "open_layers",
        "pending_layers",
        "completion_rate",
        "total_capital",
        "capital_deployed",
        "capital_available",
        "capital_utilization",
        "capital_exposure",
        "capital_exposure_ratio",
        "maximum_layer_capital",
        "average_layer_capital",
        "realized_profit",
        "unrealized_profit",
        "total_profit",
        "realized_return",
        "total_return",
        "profit_to_exposure",
        "risk_score",
    }

    assert required_keys.issubset(
        metrics.keys()
    )


def test_none_simulations():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(None)

    assert result["status"] == (
        analyzer.STATUS_EMPTY
    )

    assert result["analyses"] == []


def test_empty_simulations():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run([])

    assert result["status"] == (
        analyzer.STATUS_EMPTY
    )

    assert result["analyses"] == []


def test_invalid_simulation_container():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run({})

    assert result["status"] == (
        analyzer.STATUS_ERROR
    )


def test_string_simulation_container():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run("BTCUSDT")

    assert result["status"] == (
        analyzer.STATUS_ERROR
    )


def test_single_valid_simulation():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert len(result["analyses"]) == 1


def test_symbol_is_normalized():

    simulation = make_simulation()

    simulation["symbol"] = " btc/usdt "

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert (
        result["analyses"][0]["symbol"]
        == "BTCUSDT"
    )


def test_completed_layer_count():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    analysis = result["analyses"][0]

    assert analysis["completed_layers"] == 1


def test_open_layer_count():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    analysis = result["analyses"][0]

    assert analysis["open_layers"] == 1


def test_pending_layer_count():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    analysis = result["analyses"][0]

    assert analysis["pending_layers"] == 1


def test_completion_rate():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    analysis = result["analyses"][0]

    assert analysis["completion_rate"] == (
        1 / 3
    )


def test_total_capital_is_preserved():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "total_capital"
    ] == 1000.0


def test_capital_deployed():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "capital_deployed"
    ] == 600.0


def test_capital_available():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "capital_available"
    ] == 400.0


def test_capital_utilization():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "capital_utilization"
    ] == 0.6


def test_capital_exposure():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "capital_exposure"
    ] == 300.0


def test_capital_exposure_ratio():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "capital_exposure_ratio"
    ] == 0.3


def test_maximum_layer_capital():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "maximum_layer_capital"
    ] == 400.0


def test_average_layer_capital():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "average_layer_capital"
    ] == 1000.0 / 3


def test_realized_profit_is_preserved():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "realized_profit"
    ] == 30.0


def test_unrealized_profit_is_preserved():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "unrealized_profit"
    ] == 10.0


def test_total_profit():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "total_profit"
    ] == 40.0


def test_realized_return():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "realized_return"
    ] == 0.03


def test_total_return():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "total_return"
    ] == 0.04


def test_profit_to_exposure():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    assert result["analyses"][0][
        "profit_to_exposure"
    ] == 40.0 / 300.0


def test_profit_can_be_calculated_from_layers():

    simulation = make_simulation()

    simulation.pop(
        "realized_profit"
    )

    simulation.pop(
        "unrealized_profit"
    )

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    analysis = result["analyses"][0]

    assert analysis["realized_profit"] == 20.0
    assert analysis["unrealized_profit"] == 10.0
    assert analysis["total_profit"] == 30.0


def test_multiple_simulations():

    analyzer = GridRiskAnalyzer()

    first = make_simulation()

    second = make_simulation()

    second["symbol"] = "ETHUSDT"

    result = analyzer.run(
        [first, second]
    )

    assert result["processed_count"] == 2
    assert len(result["analyses"]) == 2


def test_invalid_simulation():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [
            make_simulation(),
            {},
        ]
    )

    assert result["status"] == (
        analyzer.STATUS_PARTIAL
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1


def test_invalid_simulation_contains_index():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [
            make_simulation(),
            {},
        ]
    )

    assert result["errors"][0]["index"] == 1


def test_invalid_simulation_contains_errors():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [
            make_simulation(),
            {},
        ]
    )

    assert "error" in (
        result["errors"][0]
    )


def test_invalid_simulation_type():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [
            make_simulation(),
            "BTCUSDT",
        ]
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1


def test_missing_symbol_fails():

    simulation = make_simulation()

    del simulation["symbol"]

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_invalid_symbol_fails():

    simulation = make_simulation()

    simulation["symbol"] = 123

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_layers_fails():

    simulation = make_simulation()

    simulation["layers"] = 0

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_total_capital_fails():

    simulation = make_simulation()

    simulation["total_capital"] = -100

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_layer_collection_fails():

    simulation = make_simulation()

    simulation["layers_detail"] = {}

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_layer_type_fails():

    simulation = make_simulation()

    simulation["layers_detail"][0] = "INVALID"

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_layer_status_fails():

    simulation = make_simulation()

    simulation["layers_detail"][0][
        "status"
    ] = "UNKNOWN"

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_invalid_layer_capital_fails():

    simulation = make_simulation()

    simulation["layers_detail"][0][
        "capital"
    ] = -1

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_layer_collection_length_mismatch_fails():

    simulation = make_simulation()

    simulation["layers_detail"].pop()

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 0


def test_risk_score_is_normalized():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    score = result["analyses"][0][
        "risk_score"
    ]

    assert 0.0 <= score <= 1.0


def test_high_exposure_increases_risk():

    low = make_simulation()

    high = make_simulation()

    high["layers_detail"][2][
        "status"
    ] = "OPEN"

    high["layers_detail"][2][
        "capital"
    ] = 400.0

    analyzer = GridRiskAnalyzer()

    low_result = analyzer.run(
        [low]
    )

    high_result = analyzer.run(
        [high]
    )

    low_score = low_result[
        "analyses"
    ][0]["risk_score"]

    high_score = high_result[
        "analyses"
    ][0]["risk_score"]

    assert high_score > low_score


def test_input_is_not_modified():

    analyzer = GridRiskAnalyzer()

    simulations = [
        make_simulation()
    ]

    original = deepcopy(
        simulations
    )

    analyzer.run(
        simulations
    )

    assert simulations == original


def test_result_input_preserves_original_data():

    analyzer = GridRiskAnalyzer()

    simulations = [
        make_simulation()
    ]

    result = analyzer.run(
        simulations
    )

    assert result["input"] == simulations


def test_result_is_independent():

    analyzer = GridRiskAnalyzer()

    simulations = [
        make_simulation()
    ]

    result = analyzer.run(
        simulations
    )

    result["analyses"][0][
        "symbol"
    ] = "MODIFIED"

    second_result = analyzer.run(
        simulations
    )

    assert (
        second_result["analyses"][0][
            "symbol"
        ]
        == "BTCUSDT"
    )


def test_analysis_is_independent_from_simulation():

    analyzer = GridRiskAnalyzer()

    simulation = make_simulation()

    result = analyzer.run(
        [simulation]
    )

    result["analyses"][0][
        "layers_detail"
    ][0]["capital"] = 999999

    assert (
        simulation["layers_detail"][0][
            "capital"
        ]
        == 300.0
    )


def test_simulation_snapshot_is_independent():

    analyzer = GridRiskAnalyzer()

    simulation = make_simulation()

    result = analyzer.run(
        [simulation]
    )

    result["analyses"][0][
        "simulation"
    ]["symbol"] = "MODIFIED"

    assert (
        simulation["symbol"]
        == "BTCUSDT"
    )


def test_layer_detail_is_independent():

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [make_simulation()]
    )

    result["analyses"][0][
        "layers_detail"
    ][0]["status"] = "OPEN"

    assert (
        result["analyses"][0][
            "layers_detail"
        ][0]["status"]
        == "OPEN"
    )


def test_process_alias():

    analyzer = GridRiskAnalyzer()

    result = analyzer.process(
        [make_simulation()]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )


def test_execute_alias():

    analyzer = GridRiskAnalyzer()

    result = analyzer.execute(
        [make_simulation()]
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )


def test_process_alias_matches_run():

    analyzer = GridRiskAnalyzer()

    simulations = [
        make_simulation()
    ]

    assert (
        analyzer.process(simulations)
        == analyzer.run(simulations)
    )


def test_execute_alias_matches_run():

    analyzer = GridRiskAnalyzer()

    simulations = [
        make_simulation()
    ]

    assert (
        analyzer.execute(simulations)
        == analyzer.run(simulations)
    )


def test_convenience_function():

    result = analyze_grid_risk(
        [make_simulation()]
    )

    assert result["status"] == "SUCCESS"

    assert (
        len(result["analyses"])
        == 1
    )


def test_tuple_input():

    analyzer = GridRiskAnalyzer()

    simulation = make_simulation()

    result = analyzer.run(
        (simulation,)
    )

    assert result["status"] == (
        analyzer.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1


def test_layer_capital_alias():

    simulation = make_simulation()

    for layer in simulation[
        "layers_detail"
    ]:
        layer["layer_capital"] = (
            layer["capital"]
        )
        del layer["capital"]

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 1


def test_layer_results_alias():

    simulation = make_simulation()

    simulation["layer_results"] = (
        simulation.pop(
            "layers_detail"
        )
    )

    analyzer = GridRiskAnalyzer()

    result = analyzer.run(
        [simulation]
    )

    assert result["processed_count"] == 1