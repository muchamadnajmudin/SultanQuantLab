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


from engine.market_analyzer import (
    calculate_normalized_volatility,
    detect_trend_strength,
    detect_market_regime,
)


def test_normalized_volatility():

    result = calculate_normalized_volatility(

        atr=2,

        close=100,

    )

    assert result == 2.0


def test_normalized_volatility_zero_close():

    result = calculate_normalized_volatility(

        atr=2,

        close=0,

    )

    assert result == 0.0


def test_trend_strength():

    assert detect_trend_strength(10) == "WEAK"

    assert detect_trend_strength(25) == "MODERATE"

    assert detect_trend_strength(35) == "STRONG"

    assert detect_trend_strength(45) == "VERY_STRONG"


def test_market_regime_strong_trend():

    regime = detect_market_regime(

        trend="UPTREND",

        trend_strength="STRONG",

        volatility="MEDIUM",

        momentum="BULLISH",

    )

    assert regime == "STRONG_TREND"


def test_market_regime_range():

    regime = detect_market_regime(

        trend="RANGE",

        trend_strength="WEAK",

        volatility="LOW",

        momentum="NEUTRAL",

    )

    assert regime == "RANGE"


def test_market_regime_volatile_range():

    regime = detect_market_regime(

        trend="RANGE",

        trend_strength="WEAK",

        volatility="HIGH",

        momentum="NEUTRAL",

    )

    assert regime == "VOLATILE"