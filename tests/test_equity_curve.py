from reports.equity_curve import (
    build_equity_curve,
    get_final_balance,
)



def test_equity_curve():


    trades = [

        100,

        -50,

        200,

        -25,

    ]



    equity = build_equity_curve(

        trades,

        initial_balance=10000,

    )



    assert equity == [

        10000,

        10100,

        10050,

        10250,

        10225,

    ]



    assert get_final_balance(
        equity
    ) == 10225



    print("=" * 50)

    print("EQUITY CURVE TEST PASSED")

    print("=" * 50)