import pandas as pd

from strategies.price_action import generate_signal


def test_price_action_strategy():

    df = pd.DataFrame({

        "Open": [100, 98],
        "High": [101, 103],
        "Low": [97, 97],
        "Close": [98, 102],
        "ATR": [2, 2],

    })

    result = generate_signal(df)

    assert "BUY" in result.columns
    assert "SELL" in result.columns
    assert "SL" in result.columns
    assert "TP" in result.columns