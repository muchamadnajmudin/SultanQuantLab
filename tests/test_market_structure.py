import pandas as pd

from strategies.price_action_structure import detect_structure


def test_market_structure():

    df = pd.DataFrame({

        "High": [10, 11, 12, 13, 14],

        "Low": [5, 6, 7, 8, 9],

        "Close": [9, 10, 13, 12, 15],

        "SWING_HIGH": [

            False,

            False,

            True,

            False,

            False,

        ],

        "SWING_LOW": [

            False,

            True,

            False,

            False,

            False,

        ],

    })

    result = detect_structure(df)

    assert "BULLISH_BOS" in result.columns
    assert "BEARISH_BOS" in result.columns
    assert "BULLISH_CHOCH" in result.columns
    assert "BEARISH_CHOCH" in result.columns
    assert "MSS" in result.columns