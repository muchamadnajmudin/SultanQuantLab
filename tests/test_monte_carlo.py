from optimizer.monte_carlo import (
    run_monte_carlo,
)



def test_monte_carlo():


    trades = [

        10,

        20,

        -5,

        15,

        -10,

    ]


    results = run_monte_carlo(

        trades,

        simulations=100,

    )


    assert len(results) == 100


    assert "final_balance" in results[0]


    assert "max_drawdown" in results[0]


    print("=" * 50)

    print("MONTE CARLO TEST PASSED")

    print("=" * 50)