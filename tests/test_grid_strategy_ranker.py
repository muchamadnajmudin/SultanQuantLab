import copy

import pytest

from engine.grid_strategy_ranker import (
    DEFAULT_PERFORMANCE_WEIGHT,
    DEFAULT_RISK_WEIGHT,
    GridStrategyRanker,
    REQUIRED_RESULT_KEYS,
    REQUIRED_STRATEGY_KEYS,
    execute_grid_strategy_rankings,
    process_grid_strategy_rankings,
    rank_grid_strategies,
)


def make_strategy(
    symbol="HYPEUSDT",
    total_return=20.0,
    realized_return=15.0,
    completion_rate=0.80,
    profit_per_completed_layer=2.0,
    risk_score=20.0,
    exposure_ratio=0.30,
    utilization=0.40,
):
    return {
        "symbol": symbol,
        "performance": {
            "total_return": total_return,
            "realized_return": realized_return,
            "completion_rate": completion_rate,
            "profit_per_completed_layer":
                profit_per_completed_layer,
        },
        "risk": {
            "risk_score": risk_score,
            "capital_exposure_ratio": exposure_ratio,
            "capital_utilization": utilization,
        },
        "analysis": {
            "source": "test",
        },
    }


def test_ranker_creation():
    ranker = GridStrategyRanker()

    assert isinstance(
        ranker,
        GridStrategyRanker,
    )


def test_default_weights():
    ranker = GridStrategyRanker()

    assert (
        ranker.performance_weight
        == DEFAULT_PERFORMANCE_WEIGHT
    )

    assert (
        ranker.risk_weight
        == DEFAULT_RISK_WEIGHT
    )


def test_custom_weights():
    ranker = GridStrategyRanker(
        performance_weight=0.70,
        risk_weight=0.30,
    )

    assert ranker.performance_weight == 0.70
    assert ranker.risk_weight == 0.30


def test_required_result_keys():
    result = rank_grid_strategies([])

    assert REQUIRED_RESULT_KEYS.issubset(
        result.keys()
    )


def test_none_simulations():
    result = rank_grid_strategies(None)

    assert result["success"] is True
    assert result["processed_count"] == 0
    assert result["ranked_strategies"] == []
    assert result["selected_strategies"] == []


def test_empty_simulations():
    result = rank_grid_strategies([])

    assert result["processed_count"] == 0
    assert result["valid_count"] == 0
    assert result["invalid_count"] == 0


def test_tuple_input():
    strategy = make_strategy()

    result = rank_grid_strategies(
        (strategy,)
    )

    assert result["valid_count"] == 1


def test_string_container_is_invalid():
    result = rank_grid_strategies(
        "invalid"
    )

    assert result["success"] is False
    assert result["errors"]


def test_single_valid_strategy():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    assert result["success"] is True
    assert result["valid_count"] == 1
    assert len(
        result["ranked_strategies"]
    ) == 1


def test_strategy_required_keys():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    ranked = result[
        "ranked_strategies"
    ][0]

    assert REQUIRED_STRATEGY_KEYS.issubset(
        ranked.keys()
    )


def test_symbol_is_normalized():
    strategy = make_strategy(
        symbol=" hypeusdt "
    )

    result = rank_grid_strategies(
        [strategy]
    )

    assert (
        result["ranked_strategies"][0]["symbol"]
        == "HYPEUSDT"
    )


def test_score_is_normalized():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    score = result[
        "ranked_strategies"
    ][0]["score"]

    assert 0.0 <= score <= 100.0


def test_performance_score_is_normalized():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    score = result[
        "ranked_strategies"
    ][0]["performance_score"]

    assert 0.0 <= score <= 100.0


def test_risk_score_is_normalized():
    strategy = make_strategy(
        risk_score=20.0
    )

    result = rank_grid_strategies(
        [strategy]
    )

    score = result[
        "ranked_strategies"
    ][0]["risk_score"]

    assert 0.0 <= score <= 100.0


def test_lower_risk_improves_risk_score():
    low_risk = make_strategy(
        symbol="LOW",
        risk_score=10.0,
    )

    high_risk = make_strategy(
        symbol="HIGH",
        risk_score=80.0,
    )

    result = rank_grid_strategies(
        [low_risk, high_risk]
    )

    ranked = result[
        "ranked_strategies"
    ]

    assert (
        ranked[0]["symbol"]
        == "LOW"
    )


def test_higher_performance_improves_rank():
    weak = make_strategy(
        symbol="WEAK",
        total_return=5.0,
        realized_return=3.0,
    )

    strong = make_strategy(
        symbol="STRONG",
        total_return=50.0,
        realized_return=40.0,
    )

    result = rank_grid_strategies(
        [weak, strong]
    )

    ranked = result[
        "ranked_strategies"
    ]

    assert (
        ranked[0]["symbol"]
        == "STRONG"
    )


def test_multiple_strategies_are_ranked():
    strategies = [
        make_strategy(
            symbol="AAA",
            total_return=10,
        ),
        make_strategy(
            symbol="BBB",
            total_return=20,
        ),
        make_strategy(
            symbol="CCC",
            total_return=30,
        ),
    ]

    result = rank_grid_strategies(
        strategies
    )

    assert len(
        result["ranked_strategies"]
    ) == 3


def test_rank_numbers_are_added():
    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
    ]

    result = rank_grid_strategies(
        strategies
    )

    ranks = [
        item["rank"]
        for item in result[
            "ranked_strategies"
        ]
    ]

    assert ranks == [1, 2]


def test_top_n_limits_selection():
    strategies = [
        make_strategy(
            symbol="AAA",
            total_return=10,
        ),
        make_strategy(
            symbol="BBB",
            total_return=20,
        ),
        make_strategy(
            symbol="CCC",
            total_return=30,
        ),
    ]

    result = rank_grid_strategies(
        strategies,
        top_n=2,
    )

    assert len(
        result["selected_strategies"]
    ) == 2


def test_top_n_none_selects_all():
    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
    ]

    result = rank_grid_strategies(
        strategies,
        top_n=None,
    )

    assert len(
        result["selected_strategies"]
    ) == 2


def test_top_n_larger_than_count_is_safe():
    strategies = [
        make_strategy(symbol="AAA"),
    ]

    result = rank_grid_strategies(
        strategies,
        top_n=10,
    )

    assert len(
        result["selected_strategies"]
    ) == 1


def test_invalid_top_n_type():
    result = rank_grid_strategies(
        [],
        top_n="2",
    )

    assert result["success"] is False


def test_boolean_top_n_invalid():
    result = rank_grid_strategies(
        [],
        top_n=True,
    )

    assert result["success"] is False


def test_zero_top_n_invalid():
    result = rank_grid_strategies(
        [],
        top_n=0,
    )

    assert result["success"] is False


def test_negative_top_n_invalid():
    result = rank_grid_strategies(
        [],
        top_n=-1,
    )

    assert result["success"] is False


def test_negative_performance_weight_invalid():
    result = rank_grid_strategies(
        [],
        performance_weight=-0.1,
    )

    assert result["success"] is False


def test_negative_risk_weight_invalid():
    result = rank_grid_strategies(
        [],
        risk_weight=-0.1,
    )

    assert result["success"] is False


def test_zero_total_weight_invalid():
    result = rank_grid_strategies(
        [],
        performance_weight=0,
        risk_weight=0,
    )

    assert result["success"] is False


def test_invalid_performance_weight_type():
    result = rank_grid_strategies(
        [],
        performance_weight="0.5",
    )

    assert result["success"] is False


def test_invalid_risk_weight_type():
    result = rank_grid_strategies(
        [],
        risk_weight="0.5",
    )

    assert result["success"] is False


def test_missing_symbol_is_invalid():
    strategy = make_strategy()
    strategy.pop("symbol")

    result = rank_grid_strategies(
        [strategy]
    )

    assert result["invalid_count"] == 1
    assert result["valid_count"] == 0


def test_invalid_symbol_type():
    strategy = make_strategy()
    strategy["symbol"] = 123

    result = rank_grid_strategies(
        [strategy]
    )

    assert result["invalid_count"] == 1


def test_empty_symbol_is_invalid():
    strategy = make_strategy(
        symbol=""
    )

    result = rank_grid_strategies(
        [strategy]
    )

    assert result["invalid_count"] == 1


def test_non_dict_strategy_is_invalid():
    result = rank_grid_strategies(
        [123]
    )

    assert result["invalid_count"] == 1


def test_partial_failure():
    valid = make_strategy(
        symbol="VALID"
    )

    invalid = {
        "symbol": "",
    }

    result = rank_grid_strategies(
        [valid, invalid]
    )

    assert result["processed_count"] == 2
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 1


def test_invalid_strategy_contains_index():
    result = rank_grid_strategies(
        [
            {
                "symbol": "",
            }
        ]
    )

    assert (
        result["invalid_strategies"][0]["index"]
        == 0
    )


def test_invalid_strategy_contains_errors():
    result = rank_grid_strategies(
        [
            {
                "symbol": "",
            }
        ]
    )

    assert (
        result["invalid_strategies"][0]["errors"]
    )


def test_input_is_not_modified():
    strategy = make_strategy()

    original = copy.deepcopy(
        strategy
    )

    rank_grid_strategies(
        [strategy]
    )

    assert strategy == original


def test_result_is_independent():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    strategy["performance"][
        "total_return"
    ] = 999999

    assert (
        result["ranked_strategies"][0][
            "performance"
        ]["total_return"]
        != 999999
    )


def test_selected_is_independent():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    result[
        "selected_strategies"
    ][0]["symbol"] = "CHANGED"

    assert (
        result["ranked_strategies"][0]["symbol"]
        != "CHANGED"
    )


def test_analysis_is_independent():
    strategy = make_strategy()

    result = rank_grid_strategies(
        [strategy]
    )

    strategy["analysis"][
        "source"
    ] = "CHANGED"

    assert (
        result["ranked_strategies"][0][
            "analysis"
        ]["source"]
        == "test"
    )


def test_performance_weight_affects_score():
    strategy = make_strategy(
        total_return=100,
        realized_return=100,
        completion_rate=1,
        profit_per_completed_layer=100,
        risk_score=80,
    )

    performance_heavy = rank_grid_strategies(
        [strategy],
        performance_weight=0.9,
        risk_weight=0.1,
    )

    risk_heavy = rank_grid_strategies(
        [strategy],
        performance_weight=0.1,
        risk_weight=0.9,
    )

    score_a = performance_heavy[
        "ranked_strategies"
    ][0]["score"]

    score_b = risk_heavy[
        "ranked_strategies"
    ][0]["score"]

    assert score_a > score_b


def test_process_alias():
    strategy = make_strategy()

    result = process_grid_strategy_rankings(
        [strategy]
    )

    assert result["valid_count"] == 1


def test_execute_alias():
    strategy = make_strategy()

    result = execute_grid_strategy_rankings(
        [strategy]
    )

    assert result["valid_count"] == 1


def test_process_alias_matches_main_function():
    strategies = [
        make_strategy(
            symbol="AAA"
        )
    ]

    expected = rank_grid_strategies(
        strategies
    )

    actual = process_grid_strategy_rankings(
        strategies
    )

    assert actual == expected


def test_execute_alias_matches_main_function():
    strategies = [
        make_strategy(
            symbol="AAA"
        )
    ]

    expected = rank_grid_strategies(
        strategies
    )

    actual = execute_grid_strategy_rankings(
        strategies
    )

    assert actual == expected


def test_engine_run():
    engine = GridStrategyRanker()

    result = engine.run(
        [make_strategy()]
    )

    assert result["valid_count"] == 1


def test_engine_process():
    engine = GridStrategyRanker()

    result = engine.process(
        [make_strategy()]
    )

    assert result["valid_count"] == 1


def test_engine_execute():
    engine = GridStrategyRanker()

    result = engine.execute(
        [make_strategy()]
    )

    assert result["valid_count"] == 1


def test_runtime_top_n_overrides_constructor():
    engine = GridStrategyRanker(
        top_n=3
    )

    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
        make_strategy(symbol="CCC"),
    ]

    result = engine.run(
        strategies,
        top_n=1,
    )

    assert len(
        result["selected_strategies"]
    ) == 1


def test_runtime_top_n_none_uses_constructor():
    engine = GridStrategyRanker(
        top_n=1
    )

    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
    ]

    result = engine.run(
        strategies
    )

    assert len(
        result["selected_strategies"]
    ) == 1


def test_deterministic_tie_break_symbol():
    a = make_strategy(
        symbol="BBB"
    )

    b = make_strategy(
        symbol="AAA"
    )

    result = rank_grid_strategies(
        [a, b]
    )

    ranked = result[
        "ranked_strategies"
    ]

    assert ranked[0]["symbol"] == "AAA"
    assert ranked[1]["symbol"] == "BBB"


def test_empty_result_has_no_selected_strategies():
    result = rank_grid_strategies([])

    assert (
        result["selected_strategies"]
        == []
    )


def test_valid_count_matches_ranked_count():
    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
        make_strategy(symbol="CCC"),
    ]

    result = rank_grid_strategies(
        strategies
    )

    assert (
        result["valid_count"]
        == len(result["ranked_strategies"])
    )


def test_processed_count_matches_input():
    strategies = [
        make_strategy(symbol="AAA"),
        make_strategy(symbol="BBB"),
    ]

    result = rank_grid_strategies(
        strategies
    )

    assert result[
        "processed_count"
    ] == 2


def test_ranked_order_is_deterministic():
    strategies = [
        make_strategy(
            symbol="A",
            total_return=20,
        ),
        make_strategy(
            symbol="B",
            total_return=50,
        ),
        make_strategy(
            symbol="C",
            total_return=10,
        ),
    ]

    result_one = rank_grid_strategies(
        strategies
    )

    result_two = rank_grid_strategies(
        list(reversed(strategies))
    )

    order_one = [
        item["symbol"]
        for item in result_one[
            "ranked_strategies"
        ]
    ]

    order_two = [
        item["symbol"]
        for item in result_two[
            "ranked_strategies"
        ]
    ]

    assert order_one == order_two