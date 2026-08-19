from engine.market_analyzer import (
    analyze_market,
)

import pandas as pd


def test_market_analyzer():

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

    profile = analyze_market(df)

    assert profile["trend"] == "UPTREND"

    assert profile["bias"] == "BULLISH"

    assert profile["volatility"] == "MEDIUM"

    assert profile["momentum"] == "BULLISH"