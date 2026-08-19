import pandas as pd

from strategies.price_action_trade import (
    execute_buy,
    execute_sell,
)


def test_execute_buy_sell():

    df = pd.DataFrame({

        "BUY": [False],
        "SELL": [False],
        "SL": [0.0],
        "TP": [0.0],

    })

    df = execute_buy(
        df=df,
        index=0,
        entry=100,
        atr=2,
        confirmation_score=30,
        pattern_score=30,
        structure_score=20,
    )

    assert df.loc[0, "BUY"] is True
    assert df.loc[0, "TP"] > df.loc[0, "SL"]

    df = execute_sell(
        df=df,
        index=0,
        entry=100,
        atr=2,
        confirmation_score=30,
        pattern_score=30,
        structure_score=20,
    )

    assert df.loc[0, "SELL"] is True