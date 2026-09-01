"""
==========================================
SULTAN QUANT OS
Grid Profile Validator Tests
==========================================
"""

from engine.grid_profile_validator import (
    GridProfileValidator,
    validate_grid_profile,
)


def create_valid_profile():
    return {
        "symbol": "BTCUSDT",
        "capital": 1000,
        "layers": 3,
        "take_profit": 0.02,
        "spacing": [
            0.01,
            0.02,
        ],
        "layer_capital": [
            300,
            300,
            300,
        ],
    }


def test_validator_creation():

    validator = GridProfileValidator()

    assert validator is not None


def test_default_values():

    validator = GridProfileValidator()

    assert validator.min_capital == 0.0
    assert validator.min_layers == 1
    assert validator.min_take_profit == 0.0


def test_custom_default_values():

    validator = GridProfileValidator(
        min_capital=100,
        min_layers=2,
        min_take_profit=0.01,
    )

    assert validator.min_capital == 100
    assert validator.min_layers == 2
    assert validator.min_take_profit == 0.01


def test_valid_profile():

    validator = GridProfileValidator()

    result = validator.validate(
        create_valid_profile()
    )

    assert result["status"] == (
        validator.STATUS_VALID
    )

    assert result["valid"] is True
    assert result["errors"] == []


def test_valid_profile_with_one_layer():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layers"] = 1
    profile["spacing"] = []
    profile["layer_capital"] = [1000]

    result = validator.validate(profile)

    assert result["status"] == (
        validator.STATUS_VALID
    )

    assert result["valid"] is True


def test_none_profile():

    validator = GridProfileValidator()

    result = validator.validate(None)

    assert result["status"] == (
        validator.STATUS_INVALID
    )

    assert result["valid"] is False
    assert result["errors"]


def test_non_dict_profile():

    validator = GridProfileValidator()

    result = validator.validate(
        "BTCUSDT"
    )

    assert result["status"] == (
        validator.STATUS_INVALID
    )

    assert result["valid"] is False


def test_missing_symbol():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["symbol"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: symbol"
        in result["errors"]
    )


def test_invalid_symbol_type():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["symbol"] = 123

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Invalid symbol type"
        in result["errors"]
    )


def test_empty_symbol():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["symbol"] = ""

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Symbol cannot be empty"
        in result["errors"]
    )


def test_whitespace_symbol():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["symbol"] = "   "

    result = validator.validate(profile)

    assert result["valid"] is False


def test_missing_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["capital"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: capital"
        in result["errors"]
    )


def test_non_numeric_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["capital"] = "1000"

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Capital must be numeric"
        in result["errors"]
    )


def test_zero_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["capital"] = 0

    result = validator.validate(profile)

    assert result["valid"] is False


def test_negative_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["capital"] = -100

    result = validator.validate(profile)

    assert result["valid"] is False


def test_minimum_capital():

    validator = GridProfileValidator(
        min_capital=100
    )

    profile = create_valid_profile()

    profile["capital"] = 100

    result = validator.validate(profile)

    assert result["valid"] is False


def test_capital_above_minimum():

    validator = GridProfileValidator(
        min_capital=100
    )

    profile = create_valid_profile()

    profile["capital"] = 101

    result = validator.validate(profile)

    assert result["valid"] is True


def test_missing_layers():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["layers"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: layers"
        in result["errors"]
    )


def test_non_integer_layers():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layers"] = 3.5

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Layers must be an integer"
        in result["errors"]
    )


def test_boolean_layers_invalid():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layers"] = True

    result = validator.validate(profile)

    assert result["valid"] is False


def test_zero_layers():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layers"] = 0

    result = validator.validate(profile)

    assert result["valid"] is False


def test_minimum_layers():

    validator = GridProfileValidator(
        min_layers=2
    )

    profile = create_valid_profile()

    profile["layers"] = 1
    profile["spacing"] = []
    profile["layer_capital"] = [1000]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_missing_take_profit():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["take_profit"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: take_profit"
        in result["errors"]
    )


def test_non_numeric_take_profit():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["take_profit"] = "0.02"

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Take profit must be numeric"
        in result["errors"]
    )


def test_zero_take_profit():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["take_profit"] = 0

    result = validator.validate(profile)

    assert result["valid"] is False


def test_negative_take_profit():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["take_profit"] = -0.01

    result = validator.validate(profile)

    assert result["valid"] is False


def test_missing_spacing():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["spacing"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: spacing"
        in result["errors"]
    )


def test_spacing_must_be_list_or_tuple():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["spacing"] = "0.01"

    result = validator.validate(profile)

    assert result["valid"] is False


def test_invalid_spacing_length():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["spacing"] = [
        0.01,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Spacing length must equal layers minus one"
        in result["errors"]
    )


def test_non_numeric_spacing():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["spacing"] = [
        0.01,
        "0.02",
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_zero_spacing():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["spacing"] = [
        0.01,
        0,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_negative_spacing():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["spacing"] = [
        0.01,
        -0.02,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_missing_layer_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    del profile["layer_capital"]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Missing required field: layer_capital"
        in result["errors"]
    )


def test_layer_capital_must_be_list_or_tuple():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layer_capital"] = 1000

    result = validator.validate(profile)

    assert result["valid"] is False


def test_invalid_layer_capital_length():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        500,
        500,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Layer capital length must equal layers"
        in result["errors"]
    )


def test_non_numeric_layer_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        300,
        "300",
        300,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_zero_layer_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        300,
        0,
        300,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_negative_layer_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["layer_capital"] = [
        300,
        -100,
        300,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False


def test_layer_capital_exceeds_total_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["capital"] = 1000

    profile["layer_capital"] = [
        500,
        500,
        500,
    ]

    result = validator.validate(profile)

    assert result["valid"] is False

    assert (
        "Total layer capital cannot exceed capital"
        in result["errors"]
    )


def test_layer_capital_equal_total_capital():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    profile["capital"] = 900

    profile["layer_capital"] = [
        300,
        300,
        300,
    ]

    result = validator.validate(profile)

    assert result["valid"] is True


def test_input_is_not_modified():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    original_symbol = profile["symbol"]

    result = validator.validate(profile)

    assert profile["symbol"] == original_symbol

    assert result["profile"] is not profile


def test_result_profile_is_independent():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    result = validator.validate(profile)

    result["profile"]["symbol"] = (
        "MODIFIED"
    )

    assert profile["symbol"] == "BTCUSDT"


def test_original_profile_change_does_not_affect_result():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    result = validator.validate(profile)

    profile["symbol"] = "ETHUSDT"

    assert (
        result["profile"]["symbol"]
        == "BTCUSDT"
    )


def test_run_alias():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    result = validator.run(profile)

    assert result["status"] == (
        validator.STATUS_VALID
    )


def test_process_alias():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    result = validator.process(profile)

    assert result["status"] == (
        validator.STATUS_VALID
    )


def test_execute_alias():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    result = validator.execute(profile)

    assert result["status"] == (
        validator.STATUS_VALID
    )


def test_run_alias_matches_validate():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    assert (
        validator.run(profile)
        == validator.validate(profile)
    )


def test_process_alias_matches_validate():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    assert (
        validator.process(profile)
        == validator.validate(profile)
    )


def test_execute_alias_matches_validate():

    validator = GridProfileValidator()

    profile = create_valid_profile()

    assert (
        validator.execute(profile)
        == validator.validate(profile)
    )


def test_validate_grid_profile_function():

    result = validate_grid_profile(
        create_valid_profile()
    )

    assert result["status"] == "VALID"
    assert result["valid"] is True


def test_multiple_errors():

    validator = GridProfileValidator()

    profile = {
        "symbol": "",
        "capital": -100,
        "layers": 0,
        "take_profit": 0,
        "spacing": [0],
        "layer_capital": [0],
    }

    result = validator.validate(profile)

    assert result["status"] == (
        validator.STATUS_INVALID
    )

    assert result["valid"] is False
    assert len(result["errors"]) > 1