from engine.trade import Trade
from engine.statistics_engine import calculate_statistics


def test_statistics_engine():

    trades = [

        Trade(
            direction="BUY",
            entry_time=None,
            profit=10,
            risk_reward=1.5,
        ),

        Trade(
            direction="BUY",
            entry_time=None,
            profit=20,
            risk_reward=1.5,
        ),

        Trade(
            direction="SELL",
            entry_time=None,
            profit=-5,
            risk_reward=1.5,
        ),

        Trade(
            direction="SELL",
            entry_time=None,
            profit=-15,
            risk_reward=1.5,
        ),

    ]


    stats = calculate_statistics(trades)


    assert stats["total_trade"] == 4
    assert stats["winner"] == 2
    assert stats["loser"] == 2

    assert stats["gross_profit"] == 30
    assert stats["gross_loss"] == 20
    assert stats["net_profit"] == 10

    assert stats["profit_factor"] == 1.5

    assert stats["average_win"] == 15
    assert stats["average_loss"] == 10

    assert stats["expectancy"] == 2.5

    assert stats["max_win"] == 20
    assert stats["max_loss"] == -15

    assert stats["average_rr"] == 1.5