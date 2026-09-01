from copy import deepcopy

import pytest

from engine.grid_profile_builder import (
    GridProfileBuilder,
)
from engine.grid_profile_pipeline import (
    GridProfilePipeline,
    run_grid_profile_pipeline,
)
from engine.grid_profile_selector import (
    GridProfileSelector,
)
from engine.grid_profile_validator import (
    GridProfileValidator,
)


def create_candidate(
    symbol="BTCUSDT",
    capital=1000,
    layers=3,
    take_profit=0.02,
):

    return {
        "symbol": symbol,
        "capital": capital,
        "layers": layers,
        "take_profit": take_profit,
    }


def test_pipeline_creation():

    pipeline = GridProfilePipeline()

    assert pipeline is not None


def test_default_dependencies():

    pipeline = GridProfilePipeline()

    assert isinstance(
        pipeline.builder,
        GridProfileBuilder,
    )

    assert isinstance(
        pipeline.validator,
        GridProfileValidator,
    )

    assert isinstance(
        pipeline.selector,
        GridProfileSelector,
    )


def test_custom_dependencies():

    builder = GridProfileBuilder()

    validator = GridProfileValidator()

    selector = GridProfileSelector()

    pipeline = GridProfilePipeline(
        builder=builder,
        validator=validator,
        selector=selector,
    )

    assert pipeline.builder is builder
    assert pipeline.validator is validator
    assert pipeline.selector is selector


def test_invalid_builder():

    class InvalidBuilder:
        pass

    with pytest.raises(
        TypeError
    ):

        GridProfilePipeline(
            builder=InvalidBuilder()
        )


def test_invalid_validator():

    class InvalidValidator:
        pass

    with pytest.raises(
        TypeError
    ):

        GridProfilePipeline(
            validator=InvalidValidator()
        )


def test_invalid_selector():

    class InvalidSelector:
        pass

    with pytest.raises(
        TypeError
    ):

        GridProfilePipeline(
            selector=InvalidSelector()
        )


def test_required_result_keys():

    pipeline = GridProfilePipeline()

    result = pipeline.run([])

    assert set(
        pipeline.REQUIRED_RESULT_KEYS
    ).issubset(
        result.keys()
    )


def test_none_candidates():

    pipeline = GridProfilePipeline()

    result = pipeline.run(None)

    assert result["status"] == (
        pipeline.STATUS_EMPTY
    )

    assert result["profiles"] == []

    assert result["validated_profiles"] == []

    assert result["selected_profiles"] == []


def test_empty_candidates():

    pipeline = GridProfilePipeline()

    result = pipeline.run([])

    assert result["status"] == (
        pipeline.STATUS_EMPTY
    )


def test_invalid_container():

    pipeline = GridProfilePipeline()

    result = pipeline.run({})

    assert result["status"] == (
        pipeline.STATUS_ERROR
    )


def test_string_container():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        "BTCUSDT"
    )

    assert result["status"] == (
        pipeline.STATUS_ERROR
    )


def test_single_valid_candidate():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    assert result["status"] == (
        pipeline.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1

    assert result["failed_count"] == 0

    assert result["selected_count"] == 1

    assert len(
        result["profiles"]
    ) == 1

    assert len(
        result["validated_profiles"]
    ) == 1

    assert len(
        result["selected_profiles"]
    ) == 1


def test_multiple_valid_candidates():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT"
            ),
            create_candidate(
                symbol="ETHUSDT"
            ),
            create_candidate(
                symbol="SOLUSDT"
            ),
        ]
    )

    assert result["status"] == (
        pipeline.STATUS_SUCCESS
    )

    assert result["processed_count"] == 3

    assert result["selected_count"] == 3


def test_builder_failure():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            {
                "symbol": "",
            }
        ]
    )

    assert result["status"] == (
        pipeline.STATUS_ERROR
    )

    assert result["processed_count"] == 0


def test_partial_builder_failure():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT"
            ),
            {
                "symbol": "",
            },
        ]
    )

    assert result["processed_count"] == 1

    assert len(
        result["selected_profiles"]
    ) == 1


def test_symbol_normalization():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol=" btc/usdt "
            )
        ]
    )

    assert (
        result["selected_profiles"][0][
            "symbol"
        ]
        == "BTCUSDT"
    )


def test_top_n_one():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT",
                take_profit=0.02,
            ),
            create_candidate(
                symbol="ETHUSDT",
                take_profit=0.05,
            ),
        ],
        top_n=1,
    )

    assert result["selected_count"] == 1

    assert (
        result["selected_profiles"][0][
            "symbol"
        ]
        == "ETHUSDT"
    )


def test_top_n_two():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT",
                take_profit=0.01,
            ),
            create_candidate(
                symbol="ETHUSDT",
                take_profit=0.03,
            ),
            create_candidate(
                symbol="SOLUSDT",
                take_profit=0.05,
            ),
        ],
        top_n=2,
    )

    assert result["selected_count"] == 2


def test_top_n_none():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT"
            ),
            create_candidate(
                symbol="ETHUSDT"
            ),
        ],
        top_n=None,
    )

    assert result["selected_count"] == 2


def test_selected_profiles_are_ranked():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT",
                take_profit=0.01,
            ),
            create_candidate(
                symbol="ETHUSDT",
                take_profit=0.05,
            ),
            create_candidate(
                symbol="SOLUSDT",
                take_profit=0.03,
            ),
        ]
    )

    selected = result[
        "selected_profiles"
    ]

    assert selected[0]["symbol"] == (
        "ETHUSDT"
    )

    assert selected[1]["symbol"] == (
        "SOLUSDT"
    )

    assert selected[2]["symbol"] == (
        "BTCUSDT"
    )


def test_build_result_is_present():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    assert isinstance(
        result["build_result"],
        dict,
    )


def test_validation_result_is_present():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    assert isinstance(
        result["validation_result"],
        dict,
    )


def test_selection_result_is_present():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    assert isinstance(
        result["selection_result"],
        dict,
    )


def test_validated_profiles_match_processed_count():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT"
            ),
            create_candidate(
                symbol="ETHUSDT"
            ),
        ]
    )

    assert len(
        result["validated_profiles"]
    ) == result[
        "processed_count"
    ]


def test_input_is_not_modified():

    pipeline = GridProfilePipeline()

    candidates = [
        create_candidate(
            symbol=" btc/usdt "
        )
    ]

    original = deepcopy(
        candidates
    )

    pipeline.run(
        candidates
    )

    assert candidates == original


def test_result_input_preserves_original_data():

    pipeline = GridProfilePipeline()

    candidates = [
        create_candidate(
            symbol=" btc/usdt "
        )
    ]

    result = pipeline.run(
        candidates
    )

    assert result["input"] == candidates


def test_result_is_independent():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    result["selected_profiles"][0][
        "symbol"
    ] = "MODIFIED"

    second_result = pipeline.run(
        [
            create_candidate()
        ]
    )

    assert (
        second_result["selected_profiles"][0][
            "symbol"
        ]
        == "BTCUSDT"
    )


def test_profiles_are_independent():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    result["profiles"][0][
        "symbol"
    ] = "MODIFIED"

    assert (
        result["validated_profiles"][0][
            "symbol"
        ]
        == "BTCUSDT"
    )


def test_validated_profiles_are_independent():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    result["validated_profiles"][0][
        "symbol"
    ] = "MODIFIED"

    assert (
        result["selected_profiles"][0][
            "symbol"
        ]
        == "BTCUSDT"
    )


def test_process_alias():

    pipeline = GridProfilePipeline()

    result = pipeline.process(
        [
            create_candidate()
        ]
    )

    assert result["status"] == (
        pipeline.STATUS_SUCCESS
    )


def test_execute_alias():

    pipeline = GridProfilePipeline()

    result = pipeline.execute(
        [
            create_candidate()
        ]
    )

    assert result["status"] == (
        pipeline.STATUS_SUCCESS
    )


def test_process_alias_matches_run():

    pipeline = GridProfilePipeline()

    candidates = [
        create_candidate()
    ]

    assert (
        pipeline.process(candidates)
        == pipeline.run(candidates)
    )


def test_execute_alias_matches_run():

    pipeline = GridProfilePipeline()

    candidates = [
        create_candidate()
    ]

    assert (
        pipeline.execute(candidates)
        == pipeline.run(candidates)
    )


def test_convenience_function():

    result = run_grid_profile_pipeline(
        [
            create_candidate()
        ]
    )

    assert result["status"] == "SUCCESS"

    assert len(
        result["selected_profiles"]
    ) == 1


def test_tuple_input():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        (
            create_candidate(
                symbol="BTCUSDT"
            ),
            create_candidate(
                symbol="ETHUSDT"
            ),
        )
    )

    assert result["status"] == (
        pipeline.STATUS_SUCCESS
    )

    assert result["processed_count"] == 2


def test_rank_is_preserved_in_selected_profiles():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT",
                take_profit=0.01,
            ),
            create_candidate(
                symbol="ETHUSDT",
                take_profit=0.05,
            ),
        ]
    )

    assert (
        result["selected_profiles"][0][
            "rank"
        ]
        == 1
    )


def test_top_n_larger_than_profiles():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate(
                symbol="BTCUSDT"
            )
        ],
        top_n=10,
    )

    assert result["selected_count"] == 1


def test_stage_results_are_independent():

    pipeline = GridProfilePipeline()

    result = pipeline.run(
        [
            create_candidate()
        ]
    )

    result["build_result"]["profiles"][0][
        "symbol"
    ] = "MODIFIED"

    assert (
        result["profiles"][0]["symbol"]
        == "BTCUSDT"
    )