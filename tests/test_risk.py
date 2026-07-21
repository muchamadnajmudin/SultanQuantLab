from engine.risk_engine import (
    calculate_buy_levels,
    calculate_sell_levels
)


def test_buy_levels():

    entry = 4500.0
    atr = 5.0

    sl, tp = calculate_buy_levels(entry, atr)

    assert sl == 4495.0
    assert tp == 4510.0


def test_sell_levels():

    entry = 4500.0
    atr = 5.0

    sl, tp = calculate_sell_levels(entry, atr)

    assert sl == 4505.0
    assert tp == 4490.0


if __name__ == "__main__":

    test_buy_levels()
    test_sell_levels()

    print("=" * 40)
    print("✓ Risk Engine Test PASSED")
    print("=" * 40)