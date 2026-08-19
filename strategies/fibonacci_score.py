"""
==========================================
SULTAN QUANT OS
Fibonacci Score Engine
Version : 1.0.0
==========================================

Responsibilities

- Trend Score
- Fibonacci Score
- Golden Zone Score
- Premium / Discount Score
- Total Setup Score

"""

from strategies.fibonacci_confirmation import (
    confirmation_score,
)

from strategies.fibonacci_engine import (
    price_zone,
    is_golden_zone,
)


# ==================================================
# TREND SCORE
# ==================================================

def trend_score(row):

    ema20 = row.get("EMA20", 0)
    ema50 = row.get("EMA50", 0)
    ema200 = row.get("EMA200", 0)

    if ema20 > ema50 > ema200:

        return 30

    if ema20 < ema50 < ema200:

        return 30

    return 0


# ==================================================
# FIBONACCI SCORE
# ==================================================

def fibonacci_score(row):

    try:

        close = row["close"]

        fib500 = row["FIB_500"]

        fib618 = row["FIB_618"]

        fib786 = row["FIB_786"]

        if fib618 <= close <= fib500:

            return 25

        if fib786 <= close <= fib618:

            return 20

    except Exception:

        pass

    return 0


# ==================================================
# GOLDEN ZONE SCORE
# ==================================================

def golden_zone_score(row):

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

            return 25

    except Exception:

        pass

    return 0


# ==================================================
# PREMIUM / DISCOUNT SCORE
# ==================================================

def zone_score(row):

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

        if zone in ("PREMIUM", "DISCOUNT"):

            return 20

    except Exception:

        pass

    return 0


# ==================================================
# TOTAL SCORE
# ==================================================

def setup_score(row):

    score = 0

    score += confirmation_score(row)

    score += trend_score(row)

    score += fibonacci_score(row)

    score += golden_zone_score(row)

    score += zone_score(row)

    return score