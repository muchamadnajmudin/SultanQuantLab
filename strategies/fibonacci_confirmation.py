"""
==========================================
SULTAN QUANT OS
Fibonacci Confirmation
Version : 1.0.0
==========================================

Responsibilities

- EMA Trend Confirmation
- RSI Confirmation
- Golden Zone Confirmation
- Premium / Discount Confirmation
- Confirmation Score

"""

from strategies.fibonacci_engine import (
    price_zone,
    is_golden_zone,
)


# ==================================================
# EMA CONFIRMATION
# ==================================================

def ema_confirmation(row):

    ema20 = row.get("EMA20", 0)
    ema50 = row.get("EMA50", 0)
    ema200 = row.get("EMA200", 0)

    if ema20 > ema50 > ema200:

        return 30

    elif ema20 < ema50 < ema200:

        return 30

    return 0


# ==================================================
# RSI CONFIRMATION
# ==================================================

def rsi_confirmation(row):

    rsi = row.get("RSI", 50)

    if 40 <= rsi <= 60:

        return 20

    if 30 <= rsi < 40:

        return 15

    if 60 < rsi <= 70:

        return 15

    return 0


# ==================================================
# GOLDEN ZONE
# ==================================================

def golden_zone_confirmation(row):

    try:

        levels = {

            "retracement": {

                "0.500": row["FIB_500"],
                "0.618": row["FIB_618"],
                "0.786": row["FIB_786"],

            }

        }

        if is_golden_zone(

            row["close"],

            levels,

        ):

            return 30

    except Exception:

        pass

    return 0


# ==================================================
# PREMIUM / DISCOUNT
# ==================================================

def zone_confirmation(row):

    try:

        levels = {

            "retracement": {

                "0.500": row["FIB_500"],

            }

        }

        zone = price_zone(

            row["close"],

            levels,

        )

        if zone == "DISCOUNT":

            return 20

        elif zone == "PREMIUM":

            return 20

    except Exception:

        pass

    return 0


# ==================================================
# TOTAL CONFIRMATION
# ==================================================

def confirmation_score(row):

    score = 0

    score += ema_confirmation(row)

    score += rsi_confirmation(row)

    score += golden_zone_confirmation(row)

    score += zone_confirmation(row)

    return score