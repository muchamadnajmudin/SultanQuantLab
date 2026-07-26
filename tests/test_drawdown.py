from reports.drawdown import (
    calculate_drawdown,
    max_drawdown,
    max_drawdown_percent,
)



def test_drawdown():


    equity = [

        10000,

        10500,

        11000,

        10000,

        9500,

        11500,

    ]



    dd = calculate_drawdown(
        equity
    )



    assert dd == [

        0,

        0,

        0,

        1000,

        1500,

        0,

    ]



    assert max_drawdown(
        equity
    ) == 1500



    assert round(

        max_drawdown_percent(
            equity
        ),

        2

    ) == 13.04



    print("=" * 50)

    print("DRAWDOWN TEST PASSED")

    print("=" * 50)