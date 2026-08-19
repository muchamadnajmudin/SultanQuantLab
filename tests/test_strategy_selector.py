from engine.strategy_selector import (
    select_strategies,
)

import pandas as pd


def test_strategy_selector():

    df = pd.DataFrame({

        "time": [

            pd.Timestamp(

                "2026-01-01 10:00"

            )

        ],

        "EMA20": [100],

        "EMA50": [90],

        "EMA200": [80],

        "ADX": [30],

        "ATR": [3],

        "RSI": [60],

    })

    strategies = select_strategies(

        df,

    )

    assert isinstance(

        strategies,

        list,

    )

    assert len(

        strategies,

    ) > 0