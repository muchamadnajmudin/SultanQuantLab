"""
==========================================
SULTAN QUANT OS
Grid Profile Selector Tests
==========================================
"""

from copy import deepcopy

import pytest

from engine.grid_profile_selector import (
    GridProfileSelector,
    select_grid_profiles,
)

from engine.grid_profile_validator import (
    GridProfileValidator,
)


def create_profile(
    symbol="BTCUSDT",
    capital=1000,
    layers=3,
    take_profit=0.02,
):
    spacing = []

    if layers > 1:

        spacing = [
            0.01
            for _ in range(
                layers - 1
            )
        ]

    layer_capital = (
        capital / layers
    )

    return {
        "symbol": symbol,
        "capital": capital,
        "layers": layers,
        "take_profit": take_profit,
        "spacing": spacing,
        "layer_capital": [
            layer_capital
            for _ in range(
                layers
            )
        ],
    }


def create_profiles():

    return [
        create_profile(
            symbol="BTCUSDT",
            capital=1000,
            layers=3,
            take_profit=0.02,
        ),
        create_profile(
            symbol="ETHUSDT",
            capital=2000,
            layers=4,
            take_profit=0.03,
        ),
        create_profile(
            symbol="SOLUSDT",
            capital=1500,
            layers=2,
            take_profit=0.025,
        ),
    ]


def test_selector_creation():

    selector = GridProfileSelector()

    assert selector is not None


def test_default_top_n():

    selector = GridProfileSelector()

    assert selector.top_n is None


def test_custom_top_n():

    selector = GridProfileSelector(
        top_n=2
    )

    assert selector.top_n == 2


def test_custom_validator():

    validator = GridProfileValidator()

    selector = GridProfileSelector(
        validator=validator
    )

    assert selector.validator is validator


def test_invalid_validator():

    with pytest.raises(TypeError):

        GridProfileSelector(
            validator="invalid"
        )


def test_invalid_top_n_type():

    with pytest.raises(ValueError):

        GridProfileSelector(
            top_n="2"
        )


def test_boolean_top_n():

    with pytest.raises(ValueError):

        GridProfileSelector(
            top_n=True
        )


def test_zero_top_n():

    with pytest.raises(ValueError):

        GridProfileSelector(
            top_n=0
        )


def test_negative_top_n():

    with pytest.raises(ValueError):

        GridProfileSelector(
            top_n=-1
        )


def test_required_result_keys():

    selector = GridProfileSelector()

    result = selector.run([])

    required_keys = {
        "status",
        "selected_profiles",
        "ranked_profiles",
        "valid_profiles",
        "invalid_profiles",
        "processed_count",
        "valid_count",
        "invalid_count",
        "selected_count",
        "input",
        "errors",
    }

    assert required_keys.issubset(
        result.keys()
    )


def test_none_profiles():

    selector = GridProfileSelector()

    result = selector.run(None)

    assert result["status"] == (
        selector.STATUS_EMPTY
    )

    assert result["selected_profiles"] == []


def test_empty_profiles():

    selector = GridProfileSelector()

    result = selector.run([])

    assert result["status"] == (
        selector.STATUS_EMPTY
    )

    assert result["selected_profiles"] == []


def test_invalid_profile_container():

    selector = GridProfileSelector()

    result = selector.run({})

    assert result["status"] == (
        selector.STATUS_ERROR
    )


def test_string_profile_container():

    selector = GridProfileSelector()

    result = selector.run(
        "BTCUSDT"
    )

    assert result["status"] == (
        selector.STATUS_ERROR
    )


def test_single_valid_profile():

    selector = GridProfileSelector()

    result = selector.run(
        [
            create_profile()
        ]
    )

    assert result["status"] == (
        selector.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 0
    assert result["selected_count"] == 1


def test_multiple_valid_profiles():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    assert result["status"] == (
        selector.STATUS_SUCCESS
    )

    assert result["processed_count"] == 3
    assert result["valid_count"] == 3
    assert result["invalid_count"] == 0
    assert result["selected_count"] == 3


def test_invalid_profile():

    selector = GridProfileSelector()

    profile = create_profile()

    profile["capital"] = -100

    result = selector.run(
        [profile]
    )

    assert result["status"] == (
        selector.STATUS_ERROR
    )

    assert result["valid_count"] == 0
    assert result["invalid_count"] == 1
    assert result["selected_count"] == 0


def test_partial_failure():

    selector = GridProfileSelector()

    invalid_profile = create_profile(
        symbol="ETHUSDT"
    )

    invalid_profile["layers"] = 0

    result = selector.run(
        [
            create_profile(),
            invalid_profile,
        ]
    )

    assert result["status"] == (
        selector.STATUS_PARTIAL
    )

    assert result["valid_count"] == 1
    assert result["invalid_count"] == 1
    assert result["selected_count"] == 1


def test_invalid_profile_contains_errors():

    selector = GridProfileSelector()

    profile = create_profile()

    profile["symbol"] = ""

    result = selector.run(
        [profile]
    )

    assert len(
        result["invalid_profiles"]
    ) == 1

    assert result[
        "invalid_profiles"
    ][0]["errors"]


def test_invalid_profile_contains_index():

    selector = GridProfileSelector()

    profiles = create_profiles()

    profiles[1]["capital"] = -100

    result = selector.run(
        profiles
    )

    assert result[
        "invalid_profiles"
    ][0]["index"] == 1


def test_higher_take_profit_ranks_first():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    assert (
        result["ranked_profiles"][0]
        ["symbol"]
        == "ETHUSDT"
    )


def test_higher_capital_breaks_take_profit_tie():

    selector = GridProfileSelector()

    profiles = [
        create_profile(
            symbol="BTCUSDT",
            capital=1000,
            take_profit=0.02,
        ),
        create_profile(
            symbol="ETHUSDT",
            capital=2000,
            take_profit=0.02,
        ),
    ]

    result = selector.run(
        profiles
    )

    assert (
        result["ranked_profiles"][0]
        ["symbol"]
        == "ETHUSDT"
    )


def test_fewer_layers_breaks_second_tie():

    selector = GridProfileSelector()

    profiles = [
        create_profile(
            symbol="BTCUSDT",
            capital=1000,
            layers=4,
            take_profit=0.02,
        ),
        create_profile(
            symbol="ETHUSDT",
            capital=1000,
            layers=2,
            take_profit=0.02,
        ),
    ]

    result = selector.run(
        profiles
    )

    assert (
        result["ranked_profiles"][0]
        ["symbol"]
        == "ETHUSDT"
    )


def test_symbol_breaks_full_metric_tie():

    selector = GridProfileSelector()

    profiles = [
        create_profile(
            symbol="ETHUSDT",
            capital=1000,
            layers=3,
            take_profit=0.02,
        ),
        create_profile(
            symbol="BTCUSDT",
            capital=1000,
            layers=3,
            take_profit=0.02,
        ),
    ]

    result = selector.run(
        profiles
    )

    assert (
        result["ranked_profiles"][0]
        ["symbol"]
        == "BTCUSDT"
    )


def test_rank_numbers_are_added():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    ranks = [
        profile["rank"]
        for profile in result[
            "ranked_profiles"
        ]
    ]

    assert ranks == [
        1,
        2,
        3,
    ]


def test_top_n_constructor_limit():

    selector = GridProfileSelector(
        top_n=2
    )

    result = selector.run(
        create_profiles()
    )

    assert result["selected_count"] == 2

    assert len(
        result["selected_profiles"]
    ) == 2


def test_top_n_runtime_override():

    selector = GridProfileSelector(
        top_n=1
    )

    result = selector.run(
        create_profiles(),
        top_n=2,
    )

    assert result["selected_count"] == 2


def test_runtime_top_n_none_uses_default():

    selector = GridProfileSelector(
        top_n=2
    )

    result = selector.run(
        create_profiles(),
        top_n=None,
    )

    assert result["selected_count"] == 2


def test_top_n_larger_than_profiles():

    selector = GridProfileSelector(
        top_n=10
    )

    result = selector.run(
        create_profiles()
    )

    assert result["selected_count"] == 3


def test_selected_profiles_follow_ranking():

    selector = GridProfileSelector(
        top_n=2
    )

    result = selector.run(
        create_profiles()
    )

    assert (
        result["selected_profiles"]
        == result["ranked_profiles"][:2]
    )


def test_all_valid_profiles_selected_by_default():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    assert result[
        "selected_profiles"
    ] == result[
        "ranked_profiles"
    ]


def test_invalid_profiles_are_not_ranked():

    selector = GridProfileSelector()

    invalid_profile = create_profile(
        symbol="BADUSDT"
    )

    invalid_profile["take_profit"] = 0

    result = selector.run(
        [
            create_profile(),
            invalid_profile,
        ]
    )

    assert len(
        result["ranked_profiles"]
    ) == 1


def test_invalid_profiles_are_not_selected():

    selector = GridProfileSelector()

    invalid_profile = create_profile(
        symbol="BADUSDT"
    )

    invalid_profile["capital"] = -1

    result = selector.run(
        [
            create_profile(),
            invalid_profile,
        ]
    )

    assert len(
        result["selected_profiles"]
    ) == 1


def test_errors_match_invalid_profiles():

    selector = GridProfileSelector()

    invalid_a = create_profile(
        symbol="A"
    )

    invalid_b = create_profile(
        symbol="B"
    )

    invalid_a["capital"] = -1
    invalid_b["layers"] = 0

    result = selector.run(
        [
            create_profile(),
            invalid_a,
            invalid_b,
        ]
    )

    assert len(
        result["errors"]
    ) == 2

    assert result["invalid_count"] == 2


def test_input_is_not_modified():

    selector = GridProfileSelector()

    profiles = create_profiles()

    original = deepcopy(
        profiles
    )

    selector.run(profiles)

    assert profiles == original


def test_result_input_preserves_original_data():

    selector = GridProfileSelector()

    profiles = create_profiles()

    result = selector.run(
        profiles
    )

    assert result["input"] == profiles


def test_result_is_independent():

    selector = GridProfileSelector()

    profiles = create_profiles()

    result = selector.run(
        profiles
    )

    result[
        "selected_profiles"
    ][0]["symbol"] = "MODIFIED"

    second_result = selector.run(
        profiles
    )

    assert (
        second_result[
            "selected_profiles"
        ][0]["symbol"]
        != "MODIFIED"
    )


def test_ranked_profile_is_independent_from_valid_profile():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    result[
        "ranked_profiles"
    ][0]["symbol"] = "MODIFIED"

    assert (
        result[
            "valid_profiles"
        ][0]["symbol"]
        != "MODIFIED"
    )


def test_selected_profile_is_independent_from_ranked_profile():

    selector = GridProfileSelector()

    result = selector.run(
        create_profiles()
    )

    result[
        "selected_profiles"
    ][0]["symbol"] = "MODIFIED"

    assert (
        result[
            "ranked_profiles"
        ][0]["symbol"]
        != "MODIFIED"
    )


def test_process_alias():

    selector = GridProfileSelector()

    result = selector.process(
        create_profiles()
    )

    assert result["status"] == (
        selector.STATUS_SUCCESS
    )


def test_execute_alias():

    selector = GridProfileSelector()

    result = selector.execute(
        create_profiles()
    )

    assert result["status"] == (
        selector.STATUS_SUCCESS
    )


def test_process_alias_matches_run():

    selector = GridProfileSelector()

    profiles = create_profiles()

    assert (
        selector.process(profiles)
        == selector.run(profiles)
    )


def test_execute_alias_matches_run():

    selector = GridProfileSelector()

    profiles = create_profiles()

    assert (
        selector.execute(profiles)
        == selector.run(profiles)
    )


def test_convenience_function():

    result = select_grid_profiles(
        create_profiles(),
        top_n=2,
    )

    assert result["status"] == "SUCCESS"

    assert result["selected_count"] == 2


def test_tuple_input():

    selector = GridProfileSelector()

    profiles = tuple(
        create_profiles()
    )

    result = selector.run(
        profiles
    )

    assert result["status"] == (
        selector.STATUS_SUCCESS
    )

    assert result["processed_count"] == 3