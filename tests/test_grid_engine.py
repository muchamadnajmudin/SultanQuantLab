import pytest

from engine.grid_engine import GridEngine


# ============================================================
# TEST 1
# Initial layer harus terbuka pada harga awal
# ============================================================

def test_grid_starts_with_first_layer():

    engine = GridEngine(
        layer_spacing=[
            0.01,
            0.02,
            0.02,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    layer = engine.start(100)

    assert layer.layer == 1

    assert layer.entry_price == 100

    assert layer.quantity == pytest.approx(1.0)

    assert layer.tp_price == pytest.approx(101.0)

    assert layer.status == "OPEN"


# ============================================================
# TEST 2
# Layer kedua aktif setelah turun 1%
#
# 100
# ↓ 1%
# 99
# ============================================================

def test_grid_opens_second_layer_after_price_drop():

    engine = GridEngine(
        layer_spacing=[
            0.01,
            0.02,
            0.02,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    engine.process_price(98)

    assert len(engine.layers) == 2

    assert (
        engine.layers[1].entry_price
        == pytest.approx(99.0)
    )

    assert (
        engine.layers[1].tp_price
        == pytest.approx(99.99)
    )


# ============================================================
# TEST 3
# Beberapa layer terbuka ketika harga turun melewati
# beberapa level.
#
# 100
# ↓ 1%
# 99
# ↓ 2%
# 97.02
# ↓ 2%
# 95.0796
#
# Jika harga hanya turun sampai 96,
# layer 95.0796 belum tersentuh.
# Jadi hanya 3 layer.
# ============================================================

def test_grid_opens_multiple_layers():

    engine = GridEngine(
        layer_spacing=[
            0.01,
            0.02,
            0.02,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    engine.process_price(96)

    assert len(engine.layers) == 3

    assert (
        engine.layers[0].entry_price
        == pytest.approx(100.0)
    )

    assert (
        engine.layers[1].entry_price
        == pytest.approx(99.0)
    )

    assert (
        engine.layers[2].entry_price
        == pytest.approx(97.02)
    )


# ============================================================
# TEST 4
# Take Profit layer pertama.
#
# Entry = 100
# TP = 101
# ============================================================

def test_grid_take_profit():

    engine = GridEngine(
        layer_spacing=[
            0.01,
            0.02,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    closed = engine.process_price(101)

    assert len(closed) == 1

    assert (
        engine.layers[0].status
        == "CLOSED"
    )

    assert (
        engine.layers[0].exit_price
        == pytest.approx(101.0)
    )

    assert (
        engine.layers[0].profit
        == pytest.approx(1.0)
    )

    assert (
        engine.realized_profit
        == pytest.approx(1.0)
    )


# ============================================================
# TEST 5
# Maximum open layers dan capital usage.
#
# Harga 96:
#
# Layer 1 = 100
# Layer 2 = 99
# Layer 3 = 97.02
#
# Total capital:
# 100 + 100 + 100 = 300
# ============================================================

def test_grid_statistics():

    engine = GridEngine(
        layer_spacing=[
            0.01,
            0.02,
            0.02,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    engine.process_price(96)

    result = engine.result()

    assert result.max_open_layers == 3

    assert (
        result.max_capital_used
        == pytest.approx(300)
    )


# ============================================================
# TEST 6
# layer_spacing tidak boleh kosong
# ============================================================

def test_invalid_grid_spacing():

    with pytest.raises(ValueError):

        GridEngine(
            layer_spacing=[],
            tp_percent=0.01,
            capital_per_layer=100,
        )


# ============================================================
# TEST 7
# TP harus > 0
# ============================================================

def test_invalid_tp():

    with pytest.raises(ValueError):

        GridEngine(
            layer_spacing=[
                0.01,
            ],
            tp_percent=0,
            capital_per_layer=100,
        )


# ============================================================
# TEST 8
# Capital per layer harus > 0
# ============================================================

def test_invalid_capital():

    with pytest.raises(ValueError):

        GridEngine(
            layer_spacing=[
                0.01,
            ],
            tp_percent=0.01,
            capital_per_layer=0,
        )


# ============================================================
# TEST 9
# Spacing negatif tidak boleh
# ============================================================

def test_negative_grid_spacing():

    with pytest.raises(ValueError):

        GridEngine(
            layer_spacing=[
                0.01,
                -0.02,
            ],
            tp_percent=0.01,
            capital_per_layer=100,
        )


# ============================================================
# TEST 10
# Grid tidak boleh start dua kali
# ============================================================

def test_grid_cannot_start_twice():

    engine = GridEngine(
        layer_spacing=[
            0.01,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    with pytest.raises(RuntimeError):

        engine.start(100)


# ============================================================
# TEST 11
# Harga harus > 0
# ============================================================

def test_invalid_start_price():

    engine = GridEngine(
        layer_spacing=[
            0.01,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    with pytest.raises(ValueError):

        engine.start(0)


# ============================================================
# TEST 12
# process_price juga harus menolak harga <= 0
# ============================================================

def test_invalid_process_price():

    engine = GridEngine(
        layer_spacing=[
            0.01,
        ],
        tp_percent=0.01,
        capital_per_layer=100,
    )

    engine.start(100)

    with pytest.raises(ValueError):

        engine.process_price(0)