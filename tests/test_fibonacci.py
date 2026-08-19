"""
==========================================
SULTAN QUANT OS
Test Fibonacci Strategy
Version : 1.0.0
==========================================
"""

import pandas as pd

from strategies.fibonacci import generate_signal


def test_fibonacci_strategy():

    df = pd.DataFrame({

        "open":  [1, 2, 3],
        "high":  [2, 3, 4],
        "low":   [0.5, 1.5, 2.5],
        "close": [1.5, 2.5, 3.5],

    })

    result = generate_signal(df)

    assert "BUY" in result.columns
    assert "SELL" in result.columns
    assert "SL" in result.columns
    assert "TP" in result.columns

    assert len(result) == len(df)