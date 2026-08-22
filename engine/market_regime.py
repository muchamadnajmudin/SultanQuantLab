"""
==========================================
SULTAN QUANT OS
Market Regime Detector
Version : 2.0.0
==========================================

Responsibilities

- Detect Market Condition
- Detect Trend
- Detect Volatility
- Normalize Market Regime
- Preserve Legacy Compatibility
- Strategy Bias Mapping

Canonical Market Regimes

- STRONG_TREND
- TRENDING
- RANGE
- VOLATILE
- TRANSITION
- UNKNOWN

Legacy aliases are preserved:

- RANGING -> RANGE
- QUIET_RANGE -> RANGE
- HIGH_VOLATILITY -> VOLATILE
"""

from engine.market_analyzer import (
    detect_market_regime as _detect_canonical_regime,
)


# ==================================================
# CANONICAL REGIME CONSTANTS
# ==================================================

STRONG_TREND = "STRONG_TREND"

TRENDING = "TRENDING"

RANGE = "RANGE"

VOLATILE = "VOLATILE"

TRANSITION = "TRANSITION"

UNKNOWN = "UNKNOWN"


# ==================================================
# LEGACY REGIME ALIASES
# ==================================================

LEGACY_RANGING = "RANGING"

LEGACY_QUIET_RANGE = "QUIET_RANGE"

LEGACY_HIGH_VOLATILITY = "HIGH_VOLATILITY"


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
# NORMALIZE MARKET REGIME
# ==================================================

def normalize_market_regime(
    regime,
    default=UNKNOWN,
):

    """
    Normalize legacy and alternate regime names
    into the canonical Sultan Quant OS regime
    contract.

    Canonical output:

    - STRONG_TREND
    - TRENDING
    - RANGE
    - VOLATILE
    - TRANSITION
    - UNKNOWN

    Legacy compatibility:

    RANGING
        -> RANGE

    QUIET_RANGE
        -> RANGE

    HIGH_VOLATILITY
        -> VOLATILE
    """

    if regime is None:

        return default

    try:

        regime = str(
            regime
        ).strip().upper()

    except (
        TypeError,
        ValueError,
    ):

        return default

    if not regime:

        return default

    aliases = {

        # ------------------------------------------
        # CANONICAL
        # ------------------------------------------

        STRONG_TREND:
            STRONG_TREND,

        TRENDING:
            TRENDING,

        RANGE:
            RANGE,

        VOLATILE:
            VOLATILE,

        TRANSITION:
            TRANSITION,

        UNKNOWN:
            UNKNOWN,

        # ------------------------------------------
        # LEGACY RANGE
        # ------------------------------------------

        LEGACY_RANGING:
            RANGE,

        LEGACY_QUIET_RANGE:
            RANGE,

        "SIDEWAYS":
            RANGE,

        "RANGE_BOUND":
            RANGE,

        "RANGE_BOUND_MARKET":
            RANGE,

        # ------------------------------------------
        # LEGACY VOLATILITY
        # ------------------------------------------

        LEGACY_HIGH_VOLATILITY:
            VOLATILE,

        "HIGH_VOL":
            VOLATILE,

        "EXTREME_VOLATILITY":
            VOLATILE,

        # ------------------------------------------
        # OTHER COMMON ALIASES
        # ------------------------------------------

        "TREND":
            TRENDING,

        "STRONG_TRENDING":
            STRONG_TREND,

        "WEAK_TREND":
            TRENDING,

        "CHOPPY":
            TRANSITION,

        "MIXED":
            TRANSITION,

    }

    return aliases.get(
        regime,
        default,
    )


# ==================================================
# LEGACY REGIME REPRESENTATION
# ==================================================

def to_legacy_market_regime(
    regime,
):

    """
    Convert canonical regime into the historical
    market_regime.py representation.

    This helper should only be used by modules that
    still require legacy compatibility.
    """

    regime = normalize_market_regime(
        regime
    )

    mapping = {

        STRONG_TREND:
            TRENDING,

        TRENDING:
            TRENDING,

        RANGE:
            LEGACY_RANGING,

        VOLATILE:
            LEGACY_HIGH_VOLATILITY,

        TRANSITION:
            UNKNOWN,

        UNKNOWN:
            UNKNOWN,

    }

    return mapping.get(
        regime,
        UNKNOWN,
    )


# ==================================================
# TREND DETECTION
# ==================================================

def detect_trend(
    row,
):

    """
    EMA Trend Detection.

    Bullish:

        EMA20 > EMA50 > EMA200

    Bearish:

        EMA20 < EMA50 < EMA200

    Otherwise:

        SIDEWAYS
    """

    if row is None:

        return "SIDEWAYS"

    ema20 = _safe_float(
        row.get(
            "EMA20",
            0,
        )
    )

    ema50 = _safe_float(
        row.get(
            "EMA50",
            0,
        )
    )

    ema200 = _safe_float(
        row.get(
            "EMA200",
            0,
        )
    )

    if ema20 > ema50 > ema200:

        return "BULLISH"

    if ema20 < ema50 < ema200:

        return "BEARISH"

    return "SIDEWAYS"


# ==================================================
# VOLATILITY DETECTION
# ==================================================

def detect_volatility(
    row,
):

    """
    ATR-based volatility detection.

    Uses:

        ATR / Close * 100

    Output:

    - HIGH
    - NORMAL
    - LOW
    - UNKNOWN
    """

    if row is None:

        return "UNKNOWN"

    atr = _safe_float(
        row.get(
            "ATR",
            0,
        )
    )

    close = _safe_float(
        row.get(
            "close",
            row.get(
                "Close",
                row.get(
                    "CLOSE",
                    0,
                ),
            ),
        )
    )

    if close <= 0:

        return "UNKNOWN"

    atr_percent = (

        atr
        /
        close

    ) * 100

    if atr_percent >= 0.5:

        return "HIGH"

    if atr_percent <= 0.15:

        return "LOW"

    return "NORMAL"


# ==================================================
# REGIME DETECTION
# ==================================================

def detect_regime(
    row,
):

    """
    Detect canonical market regime.

    This function preserves the historical public
    interface:

        detect_regime(row)

    but now returns the canonical Sultan Quant OS
    regime contract.

    Detection uses:

    - EMA trend
    - ADX
    - ATR volatility

    Canonical output:

    - STRONG_TREND
    - TRENDING
    - RANGE
    - VOLATILE
    - TRANSITION
    - UNKNOWN
    """

    if row is None:

        return UNKNOWN

    trend = detect_trend(
        row
    )

    volatility = detect_volatility(
        row
    )

    adx = _safe_float(
        row.get(
            "ADX",
            0,
        )
    )

    # ----------------------------------------------
    # MAP LEGACY TREND
    # ----------------------------------------------

    if trend == "BULLISH":

        analyzer_trend = "UPTREND"

    elif trend == "BEARISH":

        analyzer_trend = "DOWNTREND"

    elif adx < 20:

        analyzer_trend = "RANGE"

    else:

        analyzer_trend = "UNCLEAR"

    # ----------------------------------------------
    # TREND STRENGTH
    # ----------------------------------------------

    if adx >= 40:

        trend_strength = "VERY_STRONG"

    elif adx >= 30:

        trend_strength = "STRONG"

    elif adx >= 20:

        trend_strength = "MODERATE"

    else:

        trend_strength = "WEAK"

    # ----------------------------------------------
    # MOMENTUM
    #
    # Legacy detector has no RSI dependency.
    # Neutral preserves compatibility.
    # ----------------------------------------------

    momentum = "NEUTRAL"

    # ----------------------------------------------
    # CANONICAL DETECTION
    # ----------------------------------------------

    regime = _detect_canonical_regime(

        trend=analyzer_trend,

        trend_strength=trend_strength,

        volatility=volatility,

        momentum=momentum,

    )

    return normalize_market_regime(
        regime
    )


# ==================================================
# STRATEGY BIAS
# ==================================================

def strategy_bias(
    regime,
    trend=None,
):

    """
    Return preferred strategy IDs for a market regime.

    Accepts both canonical and legacy regime names.
    """

    regime = normalize_market_regime(
        regime
    )

    if regime in (

        STRONG_TREND,

        TRENDING,

    ):

        return [

            "trend_following",

            "price_action",

            "fibonacci",

        ]

    if regime == RANGE:

        return [

            "price_action",

            "fibonacci",

            "breakout",

        ]

    if regime == VOLATILE:

        return [

            "price_action",

            "fibonacci",

            "breakout",

        ]

    if regime == TRANSITION:

        return [

            "price_action",

        ]

    return []


# ==================================================
# FULL ANALYSIS
# ==================================================

def analyze_market(
    row,
):

    """
    Return complete market regime analysis.

    Output uses canonical regime naming.
    """

    if row is None:

        return {

            "regime":
                UNKNOWN,

            "trend":
                "SIDEWAYS",

            "volatility":
                "UNKNOWN",

            "strategy_bias":
                [],

        }

    trend = detect_trend(
        row
    )

    volatility = detect_volatility(
        row
    )

    regime = detect_regime(
        row
    )

    return {

        "regime":
            regime,

        "trend":
            trend,

        "volatility":
            volatility,

        "strategy_bias":

            strategy_bias(

                regime,

                trend,

            ),

    }


# ==================================================
# PUBLIC API
# ==================================================

__all__ = [

    "STRONG_TREND",

    "TRENDING",

    "RANGE",

    "VOLATILE",

    "TRANSITION",

    "UNKNOWN",

    "normalize_market_regime",

    "to_legacy_market_regime",

    "detect_trend",

    "detect_volatility",

    "detect_regime",

    "strategy_bias",

    "analyze_market",

]