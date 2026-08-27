import pytest

from engine.grid_profile import GridProfile


def test_profile_creation():
    profile = GridProfile(
        symbol="HYPEUSDT",
        capital=1000,
        layers=4,
        spacing=[
            0.01,
            0.015,
            0.02,
        ],
        tp_percent=0.01,
    )

    assert profile.symbol == "HYPEUSDT"
    assert profile.capital == 1000.0
    assert profile.layers == 4
    assert len(profile.spacing) == 3
    assert profile.total_allocated_capital == 1000.0
    assert profile.is_fully_allocated is True


def test_symbol_normalization():
    profile = GridProfile(
        symbol=" btcusdt ",
        capital=100,
        layers=2,
        spacing=[0.01],
        tp_percent=0.01,
    )

    assert profile.symbol == "BTCUSDT"


def test_equal_capital_allocation():
    profile = GridProfile(
        symbol="ETHUSDT",
        capital=1000,
        layers=4,
        spacing=[
            0.01,
            0.01,
            0.01,
        ],
        tp_percent=0.01,
    )

    assert profile.layer_capital == [
        250.0,
        250.0,
        250.0,
        250.0,
    ]


def test_custom_capital_allocation():
    profile = GridProfile(
        symbol="SOLUSDT",
        capital=1000,
        layers=4,
        spacing=[
            0.01,
            0.015,
            0.02,
        ],
        tp_percent=0.01,
        layer_capital=[
            100,
            200,
            300,
            400,
        ],
    )

    assert profile.get_layer_capital(0) == 100.0
    assert profile.get_layer_capital(3) == 400.0
    assert profile.total_allocated_capital == 1000.0


def test_unused_capital():
    profile = GridProfile(
        symbol="BTCUSDT",
        capital=1000,
        layers=3,
        spacing=[
            0.01,
            0.02,
        ],
        tp_percent=0.01,
        layer_capital=[
            100,
            200,
            300,
        ],
    )

    assert profile.total_allocated_capital == 600.0
    assert profile.unused_capital == 400.0
    assert profile.is_fully_allocated is False


def test_get_spacing():
    profile = GridProfile(
        symbol="HYPEUSDT",
        capital=1000,
        layers=4,
        spacing=[
            0.01,
            0.015,
            0.02,
        ],
        tp_percent=0.01,
    )

    assert profile.get_spacing(0) == 0.01
    assert profile.get_spacing(2) == 0.02


def test_to_dict_and_from_dict():
    profile = GridProfile(
        symbol="HYPEUSDT",
        capital=1000,
        layers=3,
        spacing=[
            0.01,
            0.02,
        ],
        tp_percent=0.01,
        metadata={
            "exchange": "bitget",
            "timeframe": "5m",
        },
    )

    data = profile.to_dict()

    restored = GridProfile.from_dict(
        data
    )

    assert restored.symbol == "HYPEUSDT"
    assert restored.capital == 1000.0
    assert restored.layers == 3
    assert restored.metadata["exchange"] == "bitget"


def test_invalid_empty_symbol():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="",
            capital=1000,
            layers=2,
            spacing=[0.01],
            tp_percent=0.01,
        )


def test_invalid_capital():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=0,
            layers=2,
            spacing=[0.01],
            tp_percent=0.01,
        )


def test_invalid_layers():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=0,
            spacing=[],
            tp_percent=0.01,
        )


def test_insufficient_spacing():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=4,
            spacing=[
                0.01,
                0.02,
            ],
            tp_percent=0.01,
        )


def test_invalid_spacing():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=2,
            spacing=[0],
            tp_percent=0.01,
        )


def test_invalid_tp():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=2,
            spacing=[0.01],
            tp_percent=0,
        )


def test_invalid_layer_capital_length():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=3,
            spacing=[
                0.01,
                0.02,
            ],
            tp_percent=0.01,
            layer_capital=[
                100,
                200,
            ],
        )


def test_layer_capital_exceeds_total():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=2,
            spacing=[0.01],
            tp_percent=0.01,
            layer_capital=[
                600,
                600,
            ],
        )


def test_invalid_layer_index():
    profile = GridProfile(
        symbol="BTCUSDT",
        capital=1000,
        layers=2,
        spacing=[0.01],
        tp_percent=0.01,
    )

    with pytest.raises(IndexError):
        profile.get_layer_capital(5)


def test_invalid_spacing_index():
    profile = GridProfile(
        symbol="BTCUSDT",
        capital=1000,
        layers=2,
        spacing=[0.01],
        tp_percent=0.01,
    )

    with pytest.raises(IndexError):
        profile.get_spacing(5)


def test_one_layer_profile():
    profile = GridProfile(
        symbol="BTCUSDT",
        capital=1000,
        layers=1,
        spacing=[],
        tp_percent=0.01,
    )

    assert profile.layers == 1
    assert profile.spacing == []


def test_one_layer_cannot_have_spacing():
    with pytest.raises(ValueError):
        GridProfile(
            symbol="BTCUSDT",
            capital=1000,
            layers=1,
            spacing=[0.01],
            tp_percent=0.01,
        )