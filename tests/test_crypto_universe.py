import pytest

from engine.crypto_universe import (
    CryptoUniverse,
    CryptoUniverseResult,
)


# ============================================================
# BASIC CREATION
# ============================================================


def test_universe_creation():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "ETHUSDT",
            "SOLUSDT",
        ],
    )

    assert universe.symbols == [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
    ]

    assert universe.quote == "USDT"


# ============================================================
# SYMBOL NORMALIZATION
# ============================================================


def test_normalize_symbol_lowercase():

    assert (
        CryptoUniverse.normalize_symbol(
            "btcusdt"
        )
        == "BTCUSDT"
    )


def test_normalize_symbol_slash():

    assert (
        CryptoUniverse.normalize_symbol(
            "BTC/USDT"
        )
        == "BTCUSDT"
    )


def test_normalize_symbol_dash():

    assert (
        CryptoUniverse.normalize_symbol(
            "BTC-USDT"
        )
        == "BTCUSDT"
    )


def test_normalize_symbol_underscore():

    assert (
        CryptoUniverse.normalize_symbol(
            "BTC_USDT"
        )
        == "BTCUSDT"
    )


def test_normalize_symbol_spaces():

    assert (
        CryptoUniverse.normalize_symbol(
            " BTC USDT "
        )
        == "BTCUSDT"
    )


# ============================================================
# INVALID SYMBOLS
# ============================================================


def test_invalid_empty_symbol():

    with pytest.raises(
        ValueError
    ):

        CryptoUniverse.normalize_symbol(
            ""
        )


def test_invalid_non_string_symbol():

    with pytest.raises(
        TypeError
    ):

        CryptoUniverse.normalize_symbol(
            123
        )


# ============================================================
# QUOTE FILTER
# ============================================================


def test_usdt_filter():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "ETHUSDT",
            "BTCUSD",
            "ETHBTC",
        ],
        quote="USDT",
    )

    assert universe.symbols == [
        "BTCUSDT",
        "ETHUSDT",
    ]


def test_quote_normalization():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
        ],
        quote=" usdt ",
    )

    assert universe.quote == "USDT"


def test_invalid_quote_empty():

    with pytest.raises(
        ValueError
    ):

        CryptoUniverse(
            symbols=[
                "BTCUSDT",
            ],
            quote="",
        )


def test_invalid_quote_type():

    with pytest.raises(
        TypeError
    ):

        CryptoUniverse(
            symbols=[
                "BTCUSDT",
            ],
            quote=123,
        )


# ============================================================
# DUPLICATES
# ============================================================


def test_remove_duplicates():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "btcusdt",
            "BTC/USDT",
            "ETHUSDT",
            "ETHUSDT",
        ],
    )

    assert universe.symbols == [
        "BTCUSDT",
        "ETHUSDT",
    ]


# ============================================================
# INVALID INPUT FILTERING
# ============================================================


def test_invalid_symbols_removed():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "",
            None,
            123,
            "BTCUSD",
            "ETHUSDT",
        ],
    )

    assert universe.symbols == [
        "BTCUSDT",
        "ETHUSDT",
    ]


# ============================================================
# VALIDATION
# ============================================================


def test_is_valid_symbol():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
        ],
    )

    assert universe.is_valid_symbol(
        "ETHUSDT"
    )

    assert not universe.is_valid_symbol(
        "BTCUSD"
    )


def test_symbol_too_short():

    universe = CryptoUniverse(
        symbols=[],
        quote="USDT",
    )

    assert not universe.is_valid_symbol(
        "USDT"
    )


# ============================================================
# RESULT
# ============================================================


def test_result():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "BTCUSDT",
            "ETHUSDT",
            "BTCUSD",
        ],
    )

    result = universe.result()

    assert isinstance(
        result,
        CryptoUniverseResult,
    )

    assert result.symbols == [
        "BTCUSDT",
        "ETHUSDT",
    ]

    assert result.quote == "USDT"

    assert result.total_input == 4

    assert result.total_valid == 2

    assert result.total_removed == 2


def test_result_to_dict():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
        ],
    )

    data = universe.result().to_dict()

    assert data["symbols"] == [
        "BTCUSDT",
    ]

    assert data["quote"] == "USDT"

    assert data["total_input"] == 1

    assert data["total_valid"] == 1

    assert data["total_removed"] == 0


# ============================================================
# CONVENIENCE CONSTRUCTOR
# ============================================================


def test_from_symbols():

    universe = (
        CryptoUniverse.from_symbols(
            [
                "BTCUSDT",
                "ETHUSDT",
            ]
        )
    )

    assert len(universe) == 2

    assert universe.symbols == [
        "BTCUSDT",
        "ETHUSDT",
    ]


# ============================================================
# CONTAINER METHODS
# ============================================================


def test_contains():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
        ],
    )

    assert "BTCUSDT" in universe

    assert "btcusdt" in universe

    assert "BTCUSD" not in universe


def test_iteration():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "ETHUSDT",
        ],
    )

    assert list(universe) == [
        "BTCUSDT",
        "ETHUSDT",
    ]


def test_repr():

    universe = CryptoUniverse(
        symbols=[
            "BTCUSDT",
            "ETHUSDT",
        ],
    )

    text = repr(
        universe
    )

    assert "CryptoUniverse" in text

    assert "symbols=2" in text

    assert "USDT" in text