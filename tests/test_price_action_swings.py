import pandas as pd

from strategies.price_action_swings import detect_swings


def test_detect_swings():

    df = pd.DataFrame({

        "High": [10, 12, 15, 12, 10, 11, 14, 11],

        "Low": [5, 4, 6, 3, 2, 3, 4, 5],

    })

    result = detect_swings(df)

    assert "SWING_HIGH" in result.columns
    assert "SWING_LOW" in result.columns
    assert "HH" in result.columns
    assert "HL" in result.columns
    assert "LH" in result.columns
    assert "LL" in result.columns