"""
==========================================
SULTAN QUANT OS
Tests : Grid Strategy Selector
Version : 1.0.0
==========================================
"""

from copy import deepcopy

import pytest

from engine.grid_strategy_selector import (
    GridStrategySelector,
    GridStrategySelectorEngine,
    select_grid_strategies,
)


# ============================================================
# FIXTURES
# ============================================================

def make_strategy(
    name="Grid Alpha",
    score=80,
    rank=1,
    **extra,
):
    strategy = {
        "name": name,
        "score": score,
        "rank": rank,
    }

    strategy.update(extra)

    return strategy


def make_strategies():
    return [
        make_strategy(
            name="Grid Alpha",
            score=90,
            rank=1,
        ),
        make_strategy(
            name="Grid Beta",
            score=80,
            rank=2,
        ),
        make_strategy(
            name="Grid Gamma",
            score=70,
            rank=3,
        ),
    ]


# ============================================================
# CREATION
# ============================================================

def test_selector_creation():

    selector = GridStrategySelector()

    assert isinstance(
        selector,
        GridStrategySelector,
    )


def test_default_top_n():

    selector = GridStrategySelector()

    assert selector.top_n == 1


def test_custom_top_n():

    selector = GridStrategySelector(
        top_n=3
    )

    assert selector.top_n == 3


def test_invalid_top_n_type():

    with pytest.raises(ValueError):

        GridStrategySelector(
            top_n="2"
        )


def test_boolean_top_n():

    with pytest.raises(ValueError):

        GridStrategySelector(
            top_n=True
        )


def test_zero_top_n():

    with pytest.raises(ValueError):

        GridStrategySelector(
            top_n=0
        )


def test_negative_top_n():

    with pytest.raises(ValueError):

        GridStrategySelector(
            top_n=-1
        )


# ============================================================
# RESULT CONTRACT
# ============================================================

def test_required_result_keys():

    selector = GridStrategySelector()

    result = selector.run(
        make_strategies()
    )

    required = {
        "status",
        "strategies",
        "selected_strategies",
        "processed_count",
        "failed_count",
        "ranked_count",
        "selected_count",
        "top_n",
        "errors",
        "input",
    }

    assert required.issubset(
        result.keys()
    )


# ============================================================
# EMPTY INPUT
# ============================================================

def test_none_strategies():

    selector = GridStrategySelector()

    result = selector.run(None)

    assert result["status"] == "EMPTY"
    assert result["selected_strategies"] == []


def test_empty_strategies():

    selector = GridStrategySelector()

    result = selector.run([])

    assert result["status"] == "EMPTY"
    assert result["selected_strategies"] == []


def test_tuple_input():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        tuple(make_strategies())
    )

    assert result["selected_count"] == 2


# ============================================================
# INVALID CONTAINERS
# ============================================================

def test_invalid_strategy_container():

    selector = GridStrategySelector()

    result = selector.run(
        "invalid"
    )

    assert result["status"] == "ERROR"


def test_invalid_strategy_container_dict():

    selector = GridStrategySelector()

    result = selector.run(
        {}
    )

    assert result["status"] == "ERROR"


# ============================================================
# SINGLE STRATEGY
# ============================================================

def test_single_valid_strategy():

    selector = GridStrategySelector()

    result = selector.run(
        [make_strategy()]
    )

    assert result["status"] == "SUCCESS"
    assert result["selected_count"] == 1
    assert (
        result["selected_strategies"][0]["name"]
        == "Grid Alpha"
    )


def test_strategy_name_is_preserved():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(
                name="  Grid Alpha  "
            )
        ]
    )

    assert (
        result["selected_strategies"][0]["name"]
        == "Grid Alpha"
    )


def test_strategy_alias_is_supported():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "strategy": "Grid Alpha",
                "score": 80,
                "rank": 1,
            }
        ]
    )

    assert result["selected_count"] == 1
    assert (
        result["selected_strategies"][0]["name"]
        == "Grid Alpha"
    )


def test_id_alias_is_supported():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "id": "grid_alpha",
                "score": 80,
                "rank": 1,
            }
        ]
    )

    assert result["selected_count"] == 1
    assert (
        result["selected_strategies"][0]["name"]
        == "grid_alpha"
    )


# ============================================================
# TOP N
# ============================================================

def test_default_top_n_selects_one():

    selector = GridStrategySelector()

    result = selector.run(
        make_strategies()
    )

    assert result["selected_count"] == 1


def test_top_n_two():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies()
    )

    assert result["selected_count"] == 2


def test_top_n_three():

    selector = GridStrategySelector(
        top_n=3
    )

    result = selector.run(
        make_strategies()
    )

    assert result["selected_count"] == 3


def test_top_n_larger_than_strategies():

    selector = GridStrategySelector(
        top_n=10
    )

    result = selector.run(
        make_strategies()
    )

    assert result["selected_count"] == 3


def test_runtime_top_n():

    selector = GridStrategySelector(
        top_n=1
    )

    result = selector.run(
        make_strategies(),
        top_n=2,
    )

    assert result["top_n"] == 2
    assert result["selected_count"] == 2


def test_runtime_top_n_overrides_default():

    selector = GridStrategySelector(
        top_n=3
    )

    result = selector.run(
        make_strategies(),
        top_n=1,
    )

    assert result["top_n"] == 1
    assert result["selected_count"] == 1


def test_runtime_top_n_none_uses_default():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies(),
        top_n=None,
    )

    assert result["top_n"] == 2


def test_invalid_runtime_top_n():

    selector = GridStrategySelector()

    result = selector.run(
        make_strategies(),
        top_n=0,
    )

    assert result["status"] == "ERROR"


# ============================================================
# RANKING
# ============================================================

def test_rank_numbers_are_added():

    selector = GridStrategySelector(
        top_n=3
    )

    result = selector.run(
        make_strategies()
    )

    ranks = [
        item["rank"]
        for item in result["strategies"]
    ]

    assert ranks == [1, 2, 3]


def test_selection_rank_numbers_are_added():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies()
    )

    ranks = [
        item["selection_rank"]
        for item in result[
            "selected_strategies"
        ]
    ]

    assert ranks == [1, 2]


def test_existing_rank_is_preserved_as_source_rank():

    strategies = [
        make_strategy(
            name="Grid Beta",
            score=80,
            rank=2,
        ),
        make_strategy(
            name="Grid Alpha",
            score=90,
            rank=1,
        ),
    ]

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    assert (
        result["strategies"][0]["name"]
        == "Grid Alpha"
    )

    assert (
        result["strategies"][0]["source_rank"]
        == 1
    )


def test_lower_rank_is_preferred():

    strategies = [
        make_strategy(
            name="Grid Beta",
            score=100,
            rank=2,
        ),
        make_strategy(
            name="Grid Alpha",
            score=50,
            rank=1,
        ),
    ]

    selector = GridStrategySelector(
        top_n=1
    )

    result = selector.run(
        strategies
    )

    assert (
        result["selected_strategies"][0]["name"]
        == "Grid Alpha"
    )


def test_score_breaks_rank_tie():

    strategies = [
        make_strategy(
            name="Grid Alpha",
            score=70,
            rank=1,
        ),
        make_strategy(
            name="Grid Beta",
            score=90,
            rank=1,
        ),
    ]

    selector = GridStrategySelector(
        top_n=1
    )

    result = selector.run(
        strategies
    )

    assert (
        result["selected_strategies"][0]["name"]
        == "Grid Beta"
    )


def test_original_order_breaks_full_tie():

    strategies = [
        make_strategy(
            name="Grid Alpha",
            score=80,
            rank=1,
        ),
        make_strategy(
            name="Grid Beta",
            score=80,
            rank=1,
        ),
    ]

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    assert [
        item["name"]
        for item in result[
            "strategies"
        ]
    ] == [
        "Grid Alpha",
        "Grid Beta",
    ]


# ============================================================
# INVALID STRATEGIES
# ============================================================

def test_invalid_strategy():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(),
            "invalid",
        ]
    )

    assert result["status"] == "PARTIAL"
    assert result["failed_count"] == 1
    assert result["selected_count"] == 1


def test_invalid_strategy_contains_index():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(),
            "invalid",
        ]
    )

    assert result["errors"][0]["index"] == 1


def test_invalid_strategy_contains_errors():

    selector = GridStrategySelector()

    result = selector.run(
        [
            "invalid",
        ]
    )

    assert result["errors"][0]["errors"]


def test_missing_name_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "score": 80,
                "rank": 1,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_invalid_name_type_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": 123,
                "score": 80,
                "rank": 1,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_empty_name_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": " ",
                "score": 80,
                "rank": 1,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_invalid_score_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": "Grid Alpha",
                "score": "invalid",
                "rank": 1,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_boolean_score_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": "Grid Alpha",
                "score": True,
                "rank": 1,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_invalid_rank_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": "Grid Alpha",
                "score": 80,
                "rank": 0,
            }
        ]
    )

    assert result["status"] == "EMPTY"


def test_boolean_rank_fails():

    selector = GridStrategySelector()

    result = selector.run(
        [
            {
                "name": "Grid Alpha",
                "score": 80,
                "rank": True,
            }
        ]
    )

    assert result["status"] == "EMPTY"


# ============================================================
# PARTIAL FAILURE
# ============================================================

def test_partial_failure():

    selector = GridStrategySelector(
        top_n=2
    )

    strategies = [
        make_strategy(
            name="Grid Alpha"
        ),
        None,
        make_strategy(
            name="Grid Beta",
            score=70,
            rank=2,
        ),
    ]

    result = selector.run(
        strategies
    )

    assert result["status"] == "PARTIAL"
    assert result["processed_count"] == 2
    assert result["failed_count"] == 1
    assert result["selected_count"] == 2


# ============================================================
# IMMUTABILITY
# ============================================================

def test_input_is_not_modified():

    strategies = make_strategies()
    original = deepcopy(
        strategies
    )

    selector = GridStrategySelector(
        top_n=2
    )

    selector.run(
        strategies
    )

    assert strategies == original


def test_result_input_preserves_original_data():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    assert result["input"] == strategies


def test_result_is_independent():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    result[
        "selected_strategies"
    ][0]["name"] = "Changed"

    assert (
        strategies[0]["name"]
        == "Grid Alpha"
    )


def test_selected_strategy_is_independent():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    result[
        "selected_strategies"
    ][0]["score"] = 999

    assert (
        result["strategies"][0]["score"]
        != 999
    )


def test_nested_strategy_data_is_independent():

    strategies = [
        make_strategy(
            metadata={
                "source": "research",
                "tags": [
                    "grid",
                    "crypto",
                ],
            }
        )
    ]

    selector = GridStrategySelector()

    result = selector.run(
        strategies
    )

    result[
        "selected_strategies"
    ][0]["metadata"]["tags"].append(
        "changed"
    )

    assert (
        "changed"
        not in strategies[0][
            "metadata"
        ]["tags"]
    )


# ============================================================
# COUNTS
# ============================================================

def test_processed_count():

    selector = GridStrategySelector()

    result = selector.run(
        make_strategies()
    )

    assert result["processed_count"] == 3


def test_failed_count():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(),
            None,
        ]
    )

    assert result["failed_count"] == 1


def test_ranked_count():

    selector = GridStrategySelector()

    result = selector.run(
        make_strategies()
    )

    assert result["ranked_count"] == 3


def test_selected_count():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies()
    )

    assert result["selected_count"] == 2


# ============================================================
# ALIASES
# ============================================================

def test_process_alias():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.process(
        make_strategies()
    )

    assert result["selected_count"] == 2


def test_execute_alias():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.execute(
        make_strategies()
    )

    assert result["selected_count"] == 2


def test_process_alias_matches_run():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    assert (
        selector.process(strategies)
        == selector.run(strategies)
    )


def test_execute_alias_matches_run():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    assert (
        selector.execute(strategies)
        == selector.run(strategies)
    )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def test_convenience_function():

    result = select_grid_strategies(
        make_strategies(),
        top_n=2,
    )

    assert result["status"] == "SUCCESS"
    assert result["selected_count"] == 2


# ============================================================
# ENGINE ALIAS
# ============================================================

def test_engine_alias():

    assert (
        GridStrategySelectorEngine
        is GridStrategySelector
    )


# ============================================================
# PRESERVE COMPLETE DATA
# ============================================================

def test_complete_strategy_data_is_preserved():

    strategy = make_strategy(
        metadata={
            "symbol": "HYPEUSDT",
            "timeframe": "5m",
        },
        risk={
            "score": 20,
        },
    )

    selector = GridStrategySelector()

    result = selector.run(
        [strategy]
    )

    selected = result[
        "selected_strategies"
    ][0]

    assert selected["metadata"] == {
        "symbol": "HYPEUSDT",
        "timeframe": "5m",
    }

    assert selected["risk"] == {
        "score": 20,
    }


# ============================================================
# NUMERIC SCORE COMPATIBILITY
# ============================================================

def test_integer_score():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(
                score=80
            )
        ]
    )

    assert (
        result["selected_strategies"][0][
            "score"
        ]
        == 80.0
    )


def test_float_score():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(
                score=80.5
            )
        ]
    )

    assert (
        result["selected_strategies"][0][
            "score"
        ]
        == 80.5
    )


def test_numeric_string_score():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(
                score="80.5"
            )
        ]
    )

    assert (
        result["selected_strategies"][0][
            "score"
        ]
        == 80.5
    )


# ============================================================
# SCORE ORDER
# ============================================================

def test_high_score_wins_same_rank():

    strategies = [
        make_strategy(
            name="Weak",
            score=50,
            rank=1,
        ),
        make_strategy(
            name="Strong",
            score=95,
            rank=1,
        ),
    ]

    selector = GridStrategySelector()

    result = selector.run(
        strategies
    )

    assert (
        result["selected_strategies"][0]["name"]
        == "Strong"
    )


def test_negative_score_is_allowed():

    selector = GridStrategySelector()

    result = selector.run(
        [
            make_strategy(
                score=-10
            )
        ]
    )

    assert result["selected_count"] == 1


# ============================================================
# EMPTY AFTER VALIDATION
# ============================================================

def test_all_invalid_strategies():

    selector = GridStrategySelector()

    result = selector.run(
        [
            None,
            "invalid",
            123,
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 3
    assert result["selected_count"] == 0


def test_all_invalid_strategies_have_errors():

    selector = GridStrategySelector()

    result = selector.run(
        [
            None,
            "invalid",
        ]
    )

    assert len(
        result["errors"]
    ) == 2


# ============================================================
# STABLE OUTPUT
# ============================================================

def test_selected_strategies_follow_ranked_order():

    strategies = [
        make_strategy(
            name="Gamma",
            score=70,
            rank=3,
        ),
        make_strategy(
            name="Alpha",
            score=90,
            rank=1,
        ),
        make_strategy(
            name="Beta",
            score=80,
            rank=2,
        ),
    ]

    selector = GridStrategySelector(
        top_n=3
    )

    result = selector.run(
        strategies
    )

    assert [
        item["name"]
        for item in result[
            "selected_strategies"
        ]
    ] == [
        "Alpha",
        "Beta",
        "Gamma",
    ]


def test_selection_rank_matches_selection_order():

    selector = GridStrategySelector(
        top_n=3
    )

    result = selector.run(
        make_strategies()
    )

    for index, strategy in enumerate(
        result["selected_strategies"],
        start=1,
    ):
        assert (
            strategy["selection_rank"]
            == index
        )


def test_selected_objects_are_deep_copies():

    strategies = make_strategies()

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        strategies
    )

    assert (
        result["selected_strategies"]
        is not result["strategies"]
    )


# ============================================================
# TOP N RESULT INDEPENDENCE
# ============================================================

def test_top_n_result_is_independent():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies()
    )

    result["top_n"] = 999

    assert (
        selector.top_n == 2
    )


# ============================================================
# FINAL CONTRACT
# ============================================================

def test_success_status_without_failures():

    selector = GridStrategySelector(
        top_n=2
    )

    result = selector.run(
        make_strategies()
    )

    assert result["status"] == "SUCCESS"
    assert result["failed_count"] == 0
    assert result["selected_count"] == 2