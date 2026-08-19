"""
==========================================
SULTAN QUANT OS
Unit Test
Fibonacci Confirmation
==========================================
"""

import pandas as pd

from strategies.fibonacci_confirmation import (
    confirmation_score,
)


def test_confirmation():

    row = pd.Series({

        "EMA20": 200,
        "EMA50": 150,
        "EMA200": 100,

        "RSI": 50,

        "close": 145,

        "FIB_500": 150,
        "FIB_618": 138,
        "FIB_786": 121,

    })

    score = confirmation_score(row)

    assert score >= 50