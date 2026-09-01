from copy import deepcopy

from engine.grid_profile_builder import (
    GridProfileBuilder,
    build_grid_profiles,
)


def test_builder_creation():

    builder = GridProfileBuilder()

    assert builder is not None


def test_default_values():

    builder = GridProfileBuilder()

    assert builder.default_capital == 1000.0
    assert builder.default_layers == 5
    assert builder.default_take_profit == 0.02


def test_custom_default_values():

    builder = GridProfileBuilder(
        default_capital=5000,
        default_layers=10,
        default_take_profit=0.03,
    )

    assert builder.default_capital == 5000.0
    assert builder.default_layers == 10
    assert builder.default_take_profit == 0.03


def test_required_result_keys():

    builder = GridProfileBuilder()

    result = builder.run([])

    required_keys = {
        "status",
        "profiles",
        "processed_count",
        "failed_count",
        "errors",
        "input",
    }

    assert required_keys.issubset(
        result.keys()
    )


def test_empty_candidates():

    builder = GridProfileBuilder()

    result = builder.run([])

    assert result["status"] == (
        builder.STATUS_EMPTY
    )

    assert result["profiles"] == []


def test_none_candidates():

    builder = GridProfileBuilder()

    result = builder.run(None)

    assert result["status"] == (
        builder.STATUS_EMPTY
    )

    assert result["profiles"] == []


def test_invalid_candidate_container():

    builder = GridProfileBuilder()

    result = builder.run({})

    assert result["status"] == (
        builder.STATUS_ERROR
    )


def test_string_candidates_returns_error():

    builder = GridProfileBuilder()

    result = builder.run("BTCUSDT")

    assert result["status"] == (
        builder.STATUS_ERROR
    )


def test_valid_candidate_builds_profile():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == (
        builder.STATUS_SUCCESS
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert len(result["profiles"]) == 1


def test_profile_symbol_is_normalized():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": " btcusdt ",
            }
        ]
    )

    assert (
        result["profiles"][0]["symbol"]
        == "BTCUSDT"
    )


def test_multiple_candidates():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {"symbol": "BTCUSDT"},
            {"symbol": "ETHUSDT"},
            {"symbol": "SOLUSDT"},
        ]
    )

    assert result["processed_count"] == 3

    assert len(result["profiles"]) == 3


def test_non_dict_candidate_fails_safely():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {"symbol": "BTCUSDT"},
            "ETHUSDT",
        ]
    )

    assert result["status"] == (
        builder.STATUS_PARTIAL
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1


def test_missing_symbol_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {}
        ]
    )

    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_invalid_symbol_type_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": 123,
            }
        ]
    )

    assert result["processed_count"] == 0


def test_empty_symbol_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "",
            }
        ]
    )

    assert result["processed_count"] == 0


def test_whitespace_symbol_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "   ",
            }
        ]
    )

    assert result["processed_count"] == 0


def test_candidate_custom_capital():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "capital": 5000,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["capital"] == 5000


def test_candidate_total_capital_alias():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "total_capital": 2500,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["capital"] == 2500


def test_candidate_custom_layers():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 3,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["layers"] == 3


def test_grid_layers_alias():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "grid_layers": 4,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["layers"] == 4


def test_custom_take_profit():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "take_profit": 0.05,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["take_profit"] == 0.05


def test_tp_alias():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "tp": 0.03,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["take_profit"] == 0.03


def test_custom_spacing():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 3,
                "spacing": [
                    0.01,
                    0.02,
                ],
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["spacing"] == [
        0.01,
        0.02,
    ]


def test_invalid_spacing_length_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 4,
                "spacing": [
                    0.01,
                    0.02,
                ],
            }
        ]
    )

    assert result["processed_count"] == 0


def test_default_spacing_is_created():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 4,
            }
        ]
    )

    profile = result["profiles"][0]

    assert len(profile["spacing"]) == 3


def test_volatility_can_be_used_for_spacing():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 3,
                "volatility": 0.025,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["spacing"] == [
        0.025,
        0.025,
    ]


def test_custom_layer_capital():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "capital": 1000,
                "layers": 2,
                "layer_capital": [
                    400,
                    500,
                ],
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["layer_capital"] == [
        400.0,
        500.0,
    ]


def test_equal_capital_allocation():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "capital": 1000,
                "layers": 4,
            }
        ]
    )

    profile = result["profiles"][0]

    assert len(
        profile["layer_capital"]
    ) == 4

    assert sum(
        profile["layer_capital"]
    ) == 1000


def test_invalid_layer_capital_length_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 3,
                "layer_capital": [
                    100,
                    100,
                ],
            }
        ]
    )

    assert result["processed_count"] == 0


def test_layer_capital_exceeds_total_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "capital": 100,
                "layers": 2,
                "layer_capital": [
                    100,
                    100,
                ],
            }
        ]
    )

    assert result["processed_count"] == 0


def test_one_layer_profile():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 1,
            }
        ]
    )

    profile = result["profiles"][0]

    assert profile["layers"] == 1
    assert profile["spacing"] == []


def test_invalid_one_layer_spacing_fails():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
                "layers": 1,
                "spacing": [
                    0.01,
                ],
            }
        ]
    )

    assert result["processed_count"] == 0


def test_input_is_not_modified():

    builder = GridProfileBuilder()

    candidates = [
        {
            "symbol": " btcusdt ",
            "capital": 1000,
        }
    ]

    original = deepcopy(candidates)

    builder.run(candidates)

    assert candidates == original


def test_result_input_preserves_original_data():

    builder = GridProfileBuilder()

    candidates = [
        {
            "symbol": " btcusdt ",
        }
    ]

    result = builder.run(candidates)

    assert result["input"] == candidates


def test_result_is_independent():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    result["profiles"][0]["symbol"] = (
        "MODIFIED"
    )

    second_result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert (
        second_result["profiles"][0]["symbol"]
        == "BTCUSDT"
    )


def test_profile_candidate_is_independent():

    builder = GridProfileBuilder()

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    result = builder.run(candidates)

    result["profiles"][0]["candidate"][
        "symbol"
    ] = "MODIFIED"

    assert candidates[0]["symbol"] == (
        "BTCUSDT"
    )


def test_process_alias():

    builder = GridProfileBuilder()

    result = builder.process(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == (
        builder.STATUS_SUCCESS
    )


def test_execute_alias():

    builder = GridProfileBuilder()

    result = builder.execute(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == (
        builder.STATUS_SUCCESS
    )


def test_process_alias_matches_run():

    builder = GridProfileBuilder()

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    assert (
        builder.process(candidates)
        == builder.run(candidates)
    )


def test_execute_alias_matches_run():

    builder = GridProfileBuilder()

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    assert (
        builder.execute(candidates)
        == builder.run(candidates)
    )


def test_build_grid_profiles_function():

    result = build_grid_profiles(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "SUCCESS"

    assert len(result["profiles"]) == 1


def test_partial_failure():

    builder = GridProfileBuilder()

    result = builder.run(
        [
            {
                "symbol": "BTCUSDT",
            },
            {
                "invalid": True,
            },
        ]
    )

    assert result["status"] == (
        builder.STATUS_PARTIAL
    )

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1