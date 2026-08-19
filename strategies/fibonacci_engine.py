"""
==========================================
SULTAN QUANT OS
Fibonacci Engine
Version : 2.1.0
==========================================

Responsibilities

- Fibonacci Retracement
- Fibonacci Extension
- Premium / Discount
- Golden Zone
- Swing Validation
- Foundation for Institutional Strategy

"""

from typing import Dict


# ==================================================
# FIBONACCI LEVELS
# ==================================================

RETRACEMENT_LEVELS = {

    "0.000": 0.000,
    "0.236": 0.236,
    "0.382": 0.382,
    "0.500": 0.500,
    "0.618": 0.618,
    "0.705": 0.705,
    "0.786": 0.786,
    "1.000": 1.000,

}

EXTENSION_LEVELS = {

    "1.272": 1.272,
    "1.618": 1.618,
    "2.000": 2.000,
    "2.618": 2.618,

}


# ==================================================
# VALIDATE SWINGS
# ==================================================

def validate_swings(
    swing_high: float,
    swing_low: float,
):

    if swing_high is None:

        raise ValueError(
            "swing_high cannot be None"
        )

    if swing_low is None:

        raise ValueError(
            "swing_low cannot be None"
        )

    if swing_high <= swing_low:

        raise ValueError(
            "swing_high must be greater than swing_low"
        )


# ==================================================
# SWING DISTANCE
# ==================================================

def swing_distance(
    swing_high: float,
    swing_low: float,
):

    validate_swings(
        swing_high,
        swing_low,
    )

    return round(

        swing_high - swing_low,

        5,

    )


# ==================================================
# RETRACEMENT
# ==================================================

def calculate_retracement(
    swing_high: float,
    swing_low: float,
) -> Dict[str, float]:

    distance = swing_distance(

        swing_high,
        swing_low,

    )

    levels = {}

    for name, ratio in RETRACEMENT_LEVELS.items():

        levels[name] = round(

            swing_high - (distance * ratio),

            5,

        )

    return levels


# ==================================================
# EXTENSION
# ==================================================

def calculate_extension(
    swing_high: float,
    swing_low: float,
) -> Dict[str, float]:

    distance = swing_distance(

        swing_high,
        swing_low,

    )

    levels = {}

    for name, ratio in EXTENSION_LEVELS.items():

        levels[name] = round(

            swing_high + (

                distance * (ratio - 1.0)

            ),

            5,

        )

    return levels


# ==================================================
# CALCULATE ALL
# ==================================================

def calculate_fibonacci(
    swing_high: float,
    swing_low: float,
):

    retracement = calculate_retracement(

        swing_high,
        swing_low,

    )

    extension = calculate_extension(

        swing_high,
        swing_low,

    )

    return {

        "swing_high": swing_high,

        "swing_low": swing_low,

        "distance": swing_distance(

            swing_high,
            swing_low,

        ),

        "retracement": retracement,

        "extension": extension,

    }


# ==================================================
# GET RETRACEMENT LEVEL
# ==================================================

def retracement_level(
    levels: dict,
    name: str,
):

    return levels["retracement"][name]


# ==================================================
# GET EXTENSION LEVEL
# ==================================================

def extension_level(
    levels: dict,
    name: str,
):

    return levels["extension"][name]


# ==================================================
# EQUILIBRIUM PRICE
# ==================================================

def equilibrium_price(
    levels: dict,
):

    return levels["retracement"]["0.500"]

# ==================================================
# PRICE ZONE
# ==================================================

def price_zone(
    price: float,
    levels: dict,
):

    midpoint = equilibrium_price(levels)

    if price > midpoint:

        return "PREMIUM"

    if price < midpoint:

        return "DISCOUNT"

    return "EQUILIBRIUM"


# ==================================================
# DISCOUNT
# ==================================================

def is_discount(
    price: float,
    levels: dict,
):

    return price_zone(

        price,
        levels,

    ) == "DISCOUNT"


# ==================================================
# PREMIUM
# ==================================================

def is_premium(
    price: float,
    levels: dict,
):

    return price_zone(

        price,
        levels,

    ) == "PREMIUM"


# ==================================================
# GOLDEN ZONE
# ==================================================

def is_golden_zone(
    price: float,
    levels: dict,
):

    upper = levels["retracement"]["0.618"]

    lower = levels["retracement"]["0.786"]

    return (

        lower <= price <= upper

    )


# ==================================================
# DEEP DISCOUNT
# ==================================================

def is_deep_discount(
    price: float,
    levels: dict,
):

    """
    Institutional Buy Zone
    (0.618 - 0.786)
    """

    lower = levels["retracement"]["0.786"]

    upper = levels["retracement"]["0.618"]

    return lower <= price <= upper


# ==================================================
# DEEP PREMIUM
# ==================================================

def is_deep_premium(
    price: float,
    levels: dict,
):

    """
    Institutional Sell Zone
    Mirror of Golden Zone
    """

    midpoint = equilibrium_price(levels)

    premium_618 = round(

        midpoint + (

            midpoint
            - levels["retracement"]["0.618"]

        ),

        5,

    )

    premium_786 = round(

        midpoint + (

            midpoint
            - levels["retracement"]["0.786"]

        ),

        5,

    )

    lower = min(

        premium_618,
        premium_786,

    )

    upper = max(

        premium_618,
        premium_786,

    )

    return lower <= price <= upper


# ==================================================
# NEAREST RETRACEMENT
# ==================================================

def nearest_retracement(
    price: float,
    levels: dict,
):

    name, value = min(

        levels["retracement"].items(),

        key=lambda item: abs(

            item[1] - price

        ),

    )

    return {

        "name": name,

        "price": value,

    }


# ==================================================
# NEAREST EXTENSION
# ==================================================

def nearest_extension(
    price: float,
    levels: dict,
):

    name, value = min(

        levels["extension"].items(),

        key=lambda item: abs(

            item[1] - price

        ),

    )

    return {

        "name": name,

        "price": value,

    }


# ==================================================
# MARKET BIAS
# ==================================================

def market_bias(
    price: float,
    levels: dict,
    trend: str | None = None,
):

    """
    Institutional Market Bias

    trend:
        None
        UP
        DOWN
        RANGE
    """

    if trend == "UP":

        if is_deep_discount(price, levels):

            return "STRONG_BUY"

        if is_discount(price, levels):

            return "BUY"

        return "WAIT"

    if trend == "DOWN":

        if is_deep_premium(price, levels):

            return "STRONG_SELL"

        if is_premium(price, levels):

            return "SELL"

        return "WAIT"

    if is_deep_discount(price, levels):

        return "STRONG_BUY"

    if is_discount(price, levels):

        return "BUY"

    if is_deep_premium(price, levels):

        return "STRONG_SELL"

    if is_premium(price, levels):

        return "SELL"

    return "NEUTRAL"

# ==================================================
# ZONE NAME
# ==================================================

def zone_name(
    price: float,
    levels: dict,
):

    if is_deep_discount(price, levels):

        return "GOLDEN_ZONE"

    if is_discount(price, levels):

        return "DISCOUNT"

    if is_deep_premium(price, levels):

        return "PREMIUM_EXTREME"

    if is_premium(price, levels):

        return "PREMIUM"

    return "EQUILIBRIUM"


# ==================================================
# RETRACEMENT STRENGTH
# ==================================================

def retracement_strength(
    price: float,
    levels: dict,
):

    nearest = nearest_retracement(
        price,
        levels,
    )

    score = {

        "0.000": 0,
        "0.236": 20,
        "0.382": 40,
        "0.500": 60,
        "0.618": 80,
        "0.705": 90,
        "0.786": 100,
        "1.000": 0,

    }

    return score.get(

        nearest["name"],

        0,

    )


# ==================================================
# EXTENSION STRENGTH
# ==================================================

def extension_strength(
    price: float,
    levels: dict,
):

    nearest = nearest_extension(
        price,
        levels,
    )

    score = {

        "1.272": 40,
        "1.618": 70,
        "2.000": 90,
        "2.618": 100,

    }

    return score.get(

        nearest["name"],

        0,

    )


# ==================================================
# REVERSAL BUY
# ==================================================

def is_reversal_buy(
    price: float,
    levels: dict,
):

    return is_deep_discount(
        price,
        levels,
    )


# ==================================================
# REVERSAL SELL
# ==================================================

def is_reversal_sell(
    price: float,
    levels: dict,
):

    return is_deep_premium(
        price,
        levels,
    )


# ==================================================
# BUY ZONE
# ==================================================

def is_buy_zone(
    price: float,
    levels: dict,
):

    return (

        is_discount(
            price,
            levels,
        )

        and

        is_golden_zone(
            price,
            levels,
        )

    )


# ==================================================
# SELL ZONE
# ==================================================

def is_sell_zone(
    price: float,
    levels: dict,
):

    return is_deep_premium(
        price,
        levels,
    )


# ==================================================
# RECOMMENDED TP BUY
# ==================================================

def recommended_tp_buy(
    levels: dict,
):

    return {

        "TP1": levels["retracement"]["0.382"],

        "TP2": levels["retracement"]["0.236"],

        "TP3": levels["retracement"]["0.000"],

    }


# ==================================================
# RECOMMENDED TP SELL
# ==================================================

def recommended_tp_sell(
    levels: dict,
):

    return {

        "TP1": levels["extension"]["1.272"],

        "TP2": levels["extension"]["1.618"],

        "TP3": levels["extension"]["2.000"],

    }


# ==================================================
# RISK SCORE
# ==================================================

def risk_score(
    price: float,
    levels: dict,
):

    if is_deep_discount(price, levels):

        return 100

    if is_golden_zone(price, levels):

        return 90

    if is_discount(price, levels):

        return 70

    if is_premium(price, levels):

        return 40

    return 20


# ==================================================
# CONFLUENCE SCORE
# ==================================================

def confluence_score(

    fibonacci_score=0,

    confirmation_score=0,

    structure_score=0,

    pattern_score=0,

):

    total = (

        fibonacci_score

        + confirmation_score

        + structure_score

        + pattern_score

    )

    return min(

        total,

        100,

    )


# ==================================================
# SUMMARY
# ==================================================

def fibonacci_summary(
    price: float,
    levels: dict,
    trend: str | None = None,
):

    return {

        "price": price,

        "swing_high": levels["swing_high"],

        "swing_low": levels["swing_low"],

        "distance": levels["distance"],

        "equilibrium": equilibrium_price(levels),

        "zone": zone_name(
            price,
            levels,
        ),

        "bias": market_bias(
            price,
            levels,
            trend,
        ),

        "nearest_retracement": nearest_retracement(
            price,
            levels,
        ),

        "nearest_extension": nearest_extension(
            price,
            levels,
        ),

        "retracement_score": retracement_strength(
            price,
            levels,
        ),

        "extension_score": extension_strength(
            price,
            levels,
        ),

        "risk_score": risk_score(
            price,
            levels,
        ),

        "buy_zone": is_buy_zone(
            price,
            levels,
        ),

        "sell_zone": is_sell_zone(
            price,
            levels,
        ),

        "golden_zone": is_golden_zone(
            price,
            levels,
        ),

        "discount": is_discount(
            price,
            levels,
        ),

        "premium": is_premium(
            price,
            levels,
        ),

        "deep_discount": is_deep_discount(
            price,
            levels,
        ),

        "deep_premium": is_deep_premium(
            price,
            levels,
        ),

        "reversal_buy": is_reversal_buy(
            price,
            levels,
        ),

        "reversal_sell": is_reversal_sell(
            price,
            levels,
        ),

        "tp_buy": recommended_tp_buy(
            levels,
        ),

        "tp_sell": recommended_tp_sell(
            levels,
        ),

    }        