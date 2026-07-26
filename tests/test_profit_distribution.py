from reports.profit_distribution import (
    analyze_profit_distribution,
)



def test_profit_distribution():


    trades = [

        100,

        -50,

        200,

        -25,

        75,

    ]



    result = analyze_profit_distribution(
        trades
    )



    assert result["total_trade"] == 5


    assert result["winning_trade"] == 3


    assert result["losing_trade"] == 2


    assert result["average_win"] == 125


    assert result["average_loss"] == -37.5


    assert result["largest_win"] == 200


    assert result["largest_loss"] == -50



    print("=" * 50)

    print("PROFIT DISTRIBUTION TEST PASSED")

    print("=" * 50)