"""
==========================================
SULTAN QUANT OS
Strategy Metadata
Version : 1.0.0
==========================================

Responsibilities:

- Store strategy information
- Strategy category
- Supported market
- Supported timeframe
- Strategy complexity

"""

# ==================================================
# STRATEGY METADATA
# ==================================================

STRATEGY_INFO = {

    "sultan_baseline": {

        "name": "Sultan Baseline",

        "category": "Trend Following",

        "market": [

            "XAUUSD",

        ],

        "timeframes": [

            "M1",

            "M5",

        ],

        "complexity": "Low",

        "status": "ACTIVE",

    },

    "price_action": {

        "name": "Price Action Quant",

        "category": "Price Action",

        "market": [

            "XAUUSD",

            "BTCUSD",

        ],

        "timeframes": [

            "M1",

            "M5",

            "M15",

        ],

        "complexity": "Medium",

        "status": "PLANNED",

    },

    "smart_money": {

        "name": "Smart Money Concept",

        "category": "Institutional",

        "market": [

            "XAUUSD",

            "BTCUSD",

        ],

        "timeframes": [

            "M5",

            "M15",

            "H1",

        ],

        "complexity": "High",

        "status": "PLANNED",

    },

    "trend_following": {

        "name": "Trend Following",

        "category": "Trend",

        "market": [

            "XAUUSD",

            "BTCUSD",

            "FOREX",

        ],

        "timeframes": [

            "M5",

            "M15",

            "H1",

        ],

        "complexity": "Low",

        "status": "PLANNED",

    },

    "fibonacci": {

        "name": "Fibonacci Retracement",

        "category": "Reversal",

        "market": [

            "XAUUSD",

            "BTCUSD",

        ],

        "timeframes": [

            "M5",

            "M15",

        ],

        "complexity": "Medium",

        "status": "PLANNED",

    },

    "breakout": {

        "name": "Breakout",

        "category": "Breakout",

        "market": [

            "XAUUSD",

            "BTCUSD",

            "FOREX",

        ],

        "timeframes": [

            "M1",

            "M5",

            "M15",

        ],

        "complexity": "Low",

        "status": "PLANNED",

    },

    "mean_reversion": {

        "name": "Mean Reversion",

        "category": "Mean Reversion",

        "market": [

            "XAUUSD",

            "FOREX",

        ],

        "timeframes": [

            "M1",

            "M5",

        ],

        "complexity": "Medium",

        "status": "PLANNED",

    },

    "supply_demand": {

        "name": "Supply & Demand",

        "category": "Institutional",

        "market": [

            "XAUUSD",

        ],

        "timeframes": [

            "M5",

            "M15",

        ],

        "complexity": "Medium",

        "status": "PLANNED",

    },

    "momentum": {

        "name": "Momentum",

        "category": "Momentum",

        "market": [

            "XAUUSD",

            "BTCUSD",

            "FOREX",

        ],

        "timeframes": [

            "M1",

            "M5",

        ],

        "complexity": "Low",

        "status": "PLANNED",

    },

    "seasonal": {

        "name": "Seasonal / Session Trading",

        "category": "Session",

        "market": [

            "XAUUSD",

            "FOREX",

        ],

        "timeframes": [

            "M5",

            "M15",

        ],

        "complexity": "Medium",

        "status": "PLANNED",

    },

    "statistical_quant": {

        "name": "Statistical Quant",

        "category": "Quantitative",

        "market": [

            "XAUUSD",

            "BTCUSD",

            "FOREX",

        ],

        "timeframes": [

            "M1",

            "M5",

            "M15",

            "H1",

        ],

        "complexity": "High",

        "status": "PLANNED",

    },

}


# ==================================================
# GET STRATEGY INFO
# ==================================================

def get_strategy_info(name):

    return STRATEGY_INFO.get(

        name,

        {},

    )


# ==================================================
# GET ALL STRATEGIES
# ==================================================

def get_all_strategy_info():

    return STRATEGY_INFO


# ==================================================
# GET ACTIVE STRATEGIES
# ==================================================

def get_active_strategies():

    return {

        key: value

        for key, value in STRATEGY_INFO.items()

        if value.get("status") == "ACTIVE"

    }