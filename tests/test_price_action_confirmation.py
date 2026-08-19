import pandas as pd

from strategies.price_action_confirmation import (
    confirm_buy,
    confirmation_score,
)


def test_confirmation():

    row = pd.Series({

        "EMA_FAST": 20,

        "EMA_SLOW": 10,

        "ATR": 2,

        "ADX": 30,

        "Volume": 1000,

    })

    assert confirm_buy(row)

    assert confirmation_score(row) == 100