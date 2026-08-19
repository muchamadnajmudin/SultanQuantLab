"""
==========================================
SULTAN QUANT OS
Strategy Capability
Version : 1.0.0
==========================================

Responsibilities:

- Describe strategy capability
- Describe supported market condition
- Describe entry model
- Describe required indicators
- AI Strategy Selector reference

"""

# ==================================================
# STRATEGY CAPABILITY
# ==================================================

STRATEGY_CAPABILITY = {

    "sultan_baseline": {

        "market_condition": [

            "trend",

        ],

        "entry_model": [

            "pullback",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "EMA20",

            "EMA50",

            "EMA200",

            "RSI",

            "ATR",

            "ADX",

            "STOCHASTIC",

        ],

        "risk_level": "LOW",

    },

    "price_action": {

        "market_condition": [

            "trend",

            "range",

        ],

        "entry_model": [

            "pin_bar",

            "engulfing",

            "inside_bar",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "ATR",

        ],

        "risk_level": "MEDIUM",

    },

    "smart_money": {

        "market_condition": [

            "institutional",

        ],

        "entry_model": [

            "order_block",

            "liquidity",

            "choch",

            "bos",

            "fvg",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "ATR",

        ],

        "risk_level": "HIGH",

    },

    "trend_following": {

        "market_condition": [

            "trend",

        ],

        "entry_model": [

            "continuation",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "EMA20",

            "EMA50",

            "EMA200",

            "ADX",

        ],

        "risk_level": "LOW",

    },

    "fibonacci": {

        "market_condition": [

            "trend",

        ],

        "entry_model": [

            "retracement",

            "reversal",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "FIBONACCI",

            "ATR",

        ],

        "risk_level": "MEDIUM",

    },

    "breakout": {

        "market_condition": [

            "consolidation",

        ],

        "entry_model": [

            "breakout",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "ATR",

        ],

        "risk_level": "MEDIUM",

    },

    "mean_reversion": {

        "market_condition": [

            "range",

        ],

        "entry_model": [

            "reversal",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "RSI",

            "STOCHASTIC",

        ],

        "risk_level": "MEDIUM",

    },

    "supply_demand": {

        "market_condition": [

            "institutional",

        ],

        "entry_model": [

            "zone",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "ATR",

        ],

        "risk_level": "MEDIUM",

    },

    "momentum": {

        "market_condition": [

            "trend",

        ],

        "entry_model": [

            "momentum",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "ADX",

            "ATR",

        ],

        "risk_level": "LOW",

    },

    "seasonal": {

        "market_condition": [

            "session",

        ],

        "entry_model": [

            "session_open",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "SESSION",

        ],

        "risk_level": "LOW",

    },

    "statistical_quant": {

        "market_condition": [

            "trend",

            "range",

            "volatile",

        ],

        "entry_model": [

            "statistical",

        ],

        "bias": [

            "bullish",

            "bearish",

        ],

        "required_indicators": [

            "EMA20",

            "EMA50",

            "ATR",

            "RSI",

        ],

        "risk_level": "HIGH",

    },

}


# ==================================================
# GET CAPABILITY
# ==================================================

def get_strategy_capability(name):

    return STRATEGY_CAPABILITY.get(

        name,

        {},

    )


# ==================================================
# GET ALL
# ==================================================

def get_all_capabilities():

    return STRATEGY_CAPABILITY