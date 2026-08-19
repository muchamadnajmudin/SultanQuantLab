from strategies.trend_following import generate_signal

import pandas as pd


def test_trend_following_strategy():

    df = pd.DataFrame({

        "close": [100, 101],

        "EMA20": [110, 110],

        "EMA50": [105, 105],

        "EMA200": [95, 95],

        "ADX": [30, 30],

        "ATR": [2, 2],

    })

    result = generate_signal(df)

    assert "BUY" in result.columns
    assert "SELL" in result.columns
    assert "SL" in result.columns
    assert "TP" in result.columns