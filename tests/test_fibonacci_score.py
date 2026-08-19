"""
==========================================
SULTAN QUANT OS
Unit Test
Fibonacci Score Engine
==========================================
"""

import pandas as pd

from strategies.fibonacci_score import (
    setup_score,
)


def test_setup_score():

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

    score = setup_score(row)

    assert score > 0