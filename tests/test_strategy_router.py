import pandas as pd


from strategies.router.strategy_router import (
    recommended_strategy,
)



def test_router_trending():


    row = pd.Series({

        "EMA20":200,

        "EMA50":180,

        "EMA200":150,

        "ADX":30,

        "ATR":5,

        "close":2000,

    })


    result = recommended_strategy(

        row

    )


    assert result == "TREND_FOLLOWING"



def test_router_range():


    row = pd.Series({

        "EMA20":200,

        "EMA50":200,

        "EMA200":200,

        "ADX":15,

        "ATR":1,

        "close":2000,

    })


    result = recommended_strategy(

        row

    )


    assert result == "PRICE_ACTION"