from optimizer.monte_carlo import (
    run_bootstrap_monte_carlo,
)


def test_bootstrap_monte_carlo():

    trades = [

        10,

        20,

        -5,

        15,

        -10,

    ]

    results = run_bootstrap_monte_carlo(

        trades,

        simulations=100,

    )

    assert len(results) == 100

    first = results[0]

    assert "final_balance" in first

    assert "max_drawdown" in first

    assert "equity" in first

    assert "trade_count" in first

    assert "method" in first

    assert first["method"] == "bootstrap"

    print("=" * 50)
    print("BOOTSTRAP MONTE CARLO TEST PASSED")
    print("=" * 50)