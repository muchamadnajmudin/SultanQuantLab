"""
==========================================
SULTAN QUANT OS
Test Fibonacci Swing Engine
Version : 1.0.0
==========================================
"""

import pandas as pd

from strategies.fibonacci_swings import (
    detect_swings,
    last_swing_high,
    last_swing_low,
    latest_swings,
    fibonacci_anchor,
    has_valid_swings,
    impulse_direction,
)


# ==================================================
# TEST FIBONACCI SWINGS
# ==================================================

def test_detect_swings():

    df = pd.DataFrame({

        "high": [

            10,
            12,
            15,
            13,
            11,
            14,
            17,
            15,
            13,

        ],

        "low": [

            5,
            6,
            7,
            6,
            4,
            5,
            6,
            5,
            4,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    assert "SWING_HIGH" in df.columns

    assert "SWING_LOW" in df.columns

    assert "HH" in df.columns

    assert "HL" in df.columns

    assert "LH" in df.columns

    assert "LL" in df.columns


# ==================================================
# TEST LAST SWING HIGH
# ==================================================

def test_last_swing_high():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            5,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    value = last_swing_high(df)

    assert (

        value is None

        or

        isinstance(

            value,

            (int, float),

        )

    )


# ==================================================
# TEST LAST SWING LOW
# ==================================================

def test_last_swing_low():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            4,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    value = last_swing_low(df)

    assert (

        value is None

        or

        isinstance(

            value,

            (int, float),

        )

    )


# ==================================================
# TEST LATEST SWINGS
# ==================================================

def test_latest_swings():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            4,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    high, low = latest_swings(df)

    assert (

        high is None

        or

        isinstance(

            high,

            (int, float),

        )

    )

    assert (

        low is None

        or

        isinstance(

            low,

            (int, float),

        )

    )


# ==================================================
# TEST FIBONACCI ANCHOR
# ==================================================

def test_fibonacci_anchor():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            4,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    anchor = fibonacci_anchor(df)

    assert (

        anchor is None

        or

        isinstance(

            anchor,

            dict,

        )

    )


# ==================================================
# TEST VALID SWINGS
# ==================================================

def test_has_valid_swings():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            4,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    result = has_valid_swings(df)

    assert isinstance(

        result,

        bool,

    )


# ==================================================
# TEST IMPULSE DIRECTION
# ==================================================

def test_impulse_direction():

    df = pd.DataFrame({

        "high": [

            10,
            15,
            12,
            18,
            13,

        ],

        "low": [

            5,
            6,
            4,
            7,
            6,

        ],

    })

    df = detect_swings(

        df,

        lookback=1,

    )

    direction = impulse_direction(df)

    assert direction in (

        "BULLISH",
        "BEARISH",
        "UNKNOWN",

    )