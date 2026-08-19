"""
==========================================
SULTAN QUANT OS
Unit Test
Fibonacci Trade Builder
Version : 1.0.0
==========================================
"""

import pandas as pd

from strategies.fibonacci_trade import (
    execute_buy,
    execute_sell,
)


# ==================================================
# TEST BUY / SELL
# ==================================================

def test_execute_buy_sell():

    df = pd.DataFrame({

        "BUY": [False],
        "SELL": [False],
        "SL": [0.0],
        "TP": [0.0],

    })

    # ------------------------------------------
    # BUY
    # ------------------------------------------

    result = execute_buy(

        df=df,

        index=0,

        entry=100,

        atr=2,

        confirmation_score=20,

        pattern_score=30,

        structure_score=40,

    )

    assert result.loc[0, "BUY"]
    assert not result.loc[0, "SELL"]

    assert result.loc[0, "SL"] == 98
    assert result.loc[0, "TP"] == 104

    assert result.loc[0, "CONFIRMATION_SCORE"] == 20
    assert result.loc[0, "PATTERN_SCORE"] == 30
    assert result.loc[0, "STRUCTURE_SCORE"] == 40
    assert result.loc[0, "TOTAL_SCORE"] == 90

    # ------------------------------------------
    # SELL
    # ------------------------------------------

    result = execute_sell(

        df=result,

        index=0,

        entry=100,

        atr=2,

        confirmation_score=10,

        pattern_score=20,

        structure_score=30,

    )

    assert not result.loc[0, "BUY"]
    assert result.loc[0, "SELL"]

    assert result.loc[0, "SL"] == 102
    assert result.loc[0, "TP"] == 96

    assert result.loc[0, "CONFIRMATION_SCORE"] == 10
    assert result.loc[0, "PATTERN_SCORE"] == 20
    assert result.loc[0, "STRUCTURE_SCORE"] == 30
    assert result.loc[0, "TOTAL_SCORE"] == 60