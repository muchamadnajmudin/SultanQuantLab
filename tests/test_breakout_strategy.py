import pandas as pd

from strategies.breakout import generate_signal


def test_breakout_strategy():

    df = pd.DataFrame(
        {
            "open": [100, 101, 102, 103, 104] * 10,
            "high": [101, 102, 103, 104, 105] * 10,
            "low": [99, 100, 101, 102, 103] * 10,
            "close": [100, 101, 102, 103, 106] * 10,
            "ATR": [2.0] * 50,
        }
    )

    result = generate_signal(df)

    assert "BUY" in result.columns
    assert "SELL" in result.columns
    assert "SL" in result.columns
    assert "TP" in result.columns