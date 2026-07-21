from engine.risk_engine import (
    calculate_position_size,
    calculate_risk_amount,
    calculate_risk_reward,
)


def test_risk_amount():

    risk = calculate_risk_amount(10000)

    assert risk == 100


def test_position_size():

    lot = calculate_position_size(
        balance=10000,
        entry_price=4500,
        stop_loss=4495,
    )

    assert lot == 20.0


def test_rr():

    rr = calculate_risk_reward(
        4500,
        4495,
        4510,
    )

    assert rr == 2.0


if __name__ == "__main__":

    test_risk_amount()
    test_position_size()
    test_rr()

    print("=" * 40)
    print("✓ Position Size Test PASSED")
    print("=" * 40)