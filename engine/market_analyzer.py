"""
==========================================
SULTAN QUANT OS
Market Analyzer
Version : 1.0.0
==========================================

Responsibilities:

- Analyze market condition
- Detect trend
- Detect volatility
- Detect momentum
- Detect trading session
- Return market profile

"""

import pandas as pd


# ==================================================
# ANALYZE MARKET
# ==================================================

def analyze_market(df):

    if df.empty:

        return {}

    last = df.iloc[-1]

    ema20 = last.get("EMA20", 0)
    ema50 = last.get("EMA50", 0)
    ema200 = last.get("EMA200", 0)

    adx = last.get("ADX", 0)
    atr = last.get("ATR", 0)

    rsi = last.get("RSI", 50)

    profile = {

        "trend": detect_trend(

            ema20,

            ema50,

            ema200,

            adx,

        ),

        "volatility": detect_volatility(

            atr,

        ),

        "momentum": detect_momentum(

            rsi,

        ),

        "session": detect_session(

            last,

        ),

        "bias": detect_bias(

            ema20,

            ema50,

            ema200,

        ),

        "adx": adx,

        "atr": atr,

        "rsi": rsi,

    }

    return profile


# ==================================================
# TREND
# ==================================================

def detect_trend(

    ema20,

    ema50,

    ema200,

    adx,

):

    if adx < 20:

        return "RANGE"

    if ema20 > ema50 > ema200:

        return "UPTREND"

    if ema20 < ema50 < ema200:

        return "DOWNTREND"

    return "UNCLEAR"


# ==================================================
# VOLATILITY
# ==================================================

def detect_volatility(atr):

    if atr >= 5:

        return "HIGH"

    if atr >= 2:

        return "MEDIUM"

    return "LOW"


# ==================================================
# MOMENTUM
# ==================================================

def detect_momentum(rsi):

    if rsi >= 70:

        return "STRONG_BULLISH"

    if rsi >= 55:

        return "BULLISH"

    if rsi <= 30:

        return "STRONG_BEARISH"

    if rsi <= 45:

        return "BEARISH"

    return "NEUTRAL"


# ==================================================
# BIAS
# ==================================================

def detect_bias(

    ema20,

    ema50,

    ema200,

):

    if ema20 > ema50 > ema200:

        return "BULLISH"

    if ema20 < ema50 < ema200:

        return "BEARISH"

    return "NEUTRAL"


# ==================================================
# SESSION
# ==================================================

def detect_session(row):

    timestamp = row.get("time")

    if timestamp is None:

        return "UNKNOWN"

    if isinstance(timestamp, str):

        timestamp = pd.to_datetime(timestamp)

    hour = timestamp.hour

    if 0 <= hour < 7:

        return "ASIAN"

    if 7 <= hour < 13:

        return "LONDON"

    if 13 <= hour < 22:

        return "NEW_YORK"

    return "AFTER_HOURS"


# ==================================================
# PRINT MARKET PROFILE
# ==================================================

def print_market_profile(profile):

    print()

    print("=" * 60)
    print("MARKET PROFILE")
    print("=" * 60)

    for key, value in profile.items():

        print(

            f"{key:<20}: {value}"

        )

    print()