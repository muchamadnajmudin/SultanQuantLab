"""
==========================================
SULTAN QUANT OS
Market Analyzer
Version : 2.0.1
==========================================

Responsibilities:

- Analyze market condition
- Detect trend
- Detect trend strength
- Detect normalized volatility
- Detect momentum
- Detect trading session
- Detect market regime
- Preserve backward compatibility
- Return institutional market profile
"""

import pandas as pd


# ==================================================
# SAFE FLOAT
# ==================================================

def _safe_float(
    value,
    default=0.0,
):

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==================================================
# ANALYZE MARKET
# ==================================================

def analyze_market(
    df,
):

    """
    Analyze the latest market condition.

    Returns an institutional market profile
    containing:

    - trend
    - trend_strength
    - volatility
    - volatility_percent
    - momentum
    - session
    - bias
    - regime
    - raw indicator values
    """

    if df is None:

        return {}

    if df.empty:

        return {}

    last = df.iloc[-1]

    # ==============================================
    # INDICATORS
    # ==============================================

    ema20 = _safe_float(
        last.get(
            "EMA20",
            0,
        )
    )

    ema50 = _safe_float(
        last.get(
            "EMA50",
            0,
        )
    )

    ema200 = _safe_float(
        last.get(
            "EMA200",
            0,
        )
    )

    adx = _safe_float(
        last.get(
            "ADX",
            0,
        )
    )

    atr = _safe_float(
        last.get(
            "ATR",
            0,
        )
    )

    rsi = _safe_float(
        last.get(
            "RSI",
            50,
        ),
        50,
    )

    close = _get_close(
        last
    )

    # ==============================================
    # NORMALIZED VOLATILITY
    # ==============================================

    volatility_percent = (
        calculate_normalized_volatility(
            atr,
            close,
        )
    )

    # ==============================================
    # MARKET COMPONENTS
    # ==============================================

    trend = detect_trend(
        ema20,
        ema50,
        ema200,
        adx,
    )

    trend_strength = (
        detect_trend_strength(
            adx
        )
    )

    volatility = detect_volatility(
        atr,
        close,
    )

    momentum = detect_momentum(
        rsi
    )

    bias = detect_bias(
        ema20,
        ema50,
        ema200,
    )

    session = detect_session(
        last
    )

    regime = detect_market_regime(
        trend=trend,
        trend_strength=trend_strength,
        volatility=volatility,
        momentum=momentum,
    )

    # ==============================================
    # MARKET PROFILE
    # ==============================================

    profile = {

        "trend":
            trend,

        "trend_strength":
            trend_strength,

        "volatility":
            volatility,

        "volatility_percent":
            volatility_percent,

        "momentum":
            momentum,

        "session":
            session,

        "bias":
            bias,

        "regime":
            regime,

        "adx":
            adx,

        "atr":
            atr,

        "rsi":
            rsi,

        "close":
            close,

    }

    return profile


# ==================================================
# GET CLOSE
# ==================================================

def _get_close(
    row,
):

    """
    Retrieve close price while supporting
    common column naming conventions.
    """

    for column in (

        "close",

        "Close",

        "CLOSE",

    ):

        value = row.get(
            column,
            None,
        )

        if value is not None:

            return _safe_float(
                value,
                0,
            )

    return 0.0


# ==================================================
# NORMALIZED VOLATILITY
# ==================================================

def calculate_normalized_volatility(
    atr,
    close,
):

    """
    Calculate ATR as percentage of price.

    Formula:

        ATR / Close * 100

    This makes volatility measurement more
    comparable across different assets.
    """

    atr = _safe_float(
        atr,
        0,
    )

    close = _safe_float(
        close,
        0,
    )

    if close <= 0:

        return 0.0

    volatility_percent = (

        atr
        /
        close
        *
        100

    )

    return round(
        volatility_percent,
        6,
    )


# ==================================================
# TREND
# ==================================================

def detect_trend(

    ema20,

    ema50,

    ema200,

    adx,

):

    """
    Detect market trend using:

    - EMA alignment
    - ADX confirmation
    """

    if adx < 20:

        return "RANGE"

    if ema20 > ema50 > ema200:

        return "UPTREND"

    if ema20 < ema50 < ema200:

        return "DOWNTREND"

    return "UNCLEAR"


# ==================================================
# TREND STRENGTH
# ==================================================

def detect_trend_strength(
    adx,
):

    """
    Classify trend strength using ADX.
    """

    adx = _safe_float(
        adx,
        0,
    )

    if adx >= 40:

        return "VERY_STRONG"

    if adx >= 30:

        return "STRONG"

    if adx >= 20:

        return "MODERATE"

    return "WEAK"


# ==================================================
# VOLATILITY
# ==================================================

def detect_volatility(
    atr,
    close=None,
):

    """
    Detect market volatility.

    Preferred mode:

        ATR / Close * 100

    Backward compatibility:

    If close price is unavailable or invalid,
    use legacy absolute ATR thresholds.

    This preserves compatibility with older
    datasets and existing tests.
    """

    atr = _safe_float(
        atr,
        0,
    )

    close = _safe_float(
        close,
        0,
    )

    # ==============================================
    # LEGACY MODE
    #
    # Used when close price information
    # is unavailable.
    # ==============================================

    if close <= 0:

        if atr >= 5:

            return "HIGH"

        if atr >= 2:

            return "MEDIUM"

        return "LOW"

    # ==============================================
    # NORMALIZED MODE
    # ==============================================

    volatility_percent = (
        calculate_normalized_volatility(
            atr,
            close,
        )
    )

    if volatility_percent >= 2.0:

        return "HIGH"

    if volatility_percent >= 0.75:

        return "MEDIUM"

    return "LOW"


# ==================================================
# MOMENTUM
# ==================================================

def detect_momentum(
    rsi,
):

    """
    Detect momentum using RSI.
    """

    rsi = _safe_float(
        rsi,
        50,
    )

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

    """
    Detect directional bias using EMA alignment.
    """

    if ema20 > ema50 > ema200:

        return "BULLISH"

    if ema20 < ema50 < ema200:

        return "BEARISH"

    return "NEUTRAL"


# ==================================================
# MARKET REGIME
# ==================================================

def detect_market_regime(

    trend,

    trend_strength,

    volatility,

    momentum,

):

    """
    Determine higher-level market regime.

    Possible output:

    - STRONG_TREND
    - TRENDING
    - RANGE
    - VOLATILE
    - TRANSITION
    """

    # ==============================================
    # RANGE
    # ==============================================

    if trend == "RANGE":

        if volatility == "HIGH":

            return "VOLATILE"

        return "RANGE"

    # ==============================================
    # STRONG TREND
    # ==============================================

    if (

        trend
        in (

            "UPTREND",

            "DOWNTREND",

        )

        and

        trend_strength
        in (

            "STRONG",

            "VERY_STRONG",

        )

    ):

        return "STRONG_TREND"

    # ==============================================
    # NORMAL TREND
    # ==============================================

    if trend in (

        "UPTREND",

        "DOWNTREND",

    ):

        return "TRENDING"

    # ==============================================
    # HIGH VOLATILITY
    # ==============================================

    if volatility == "HIGH":

        return "VOLATILE"

    # ==============================================
    # TRANSITION
    # ==============================================

    return "TRANSITION"


# ==================================================
# SESSION
# ==================================================

def detect_session(
    row,
):

    """
    Detect trading session.

    Supports:

    - time
    - timestamp
    """

    timestamp = row.get(
        "time",
        None,
    )

    if timestamp is None:

        timestamp = row.get(
            "timestamp",
            None,
        )

    if timestamp is None:

        return "UNKNOWN"

    if isinstance(
        timestamp,
        str,
    ):

        timestamp = pd.to_datetime(
            timestamp
        )

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

def print_market_profile(
    profile,
):

    """
    Print formatted market profile.
    """

    print()

    print("=" * 60)
    print("MARKET PROFILE")
    print("=" * 60)

    for key, value in profile.items():

        print(

            f"{key:<25}: {value}"

        )

    print()