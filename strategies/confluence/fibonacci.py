"""
==========================================
SULTAN QUANT OS
Fibonacci Confluence Engine
Version : 2.0.0
==========================================

Responsibilities

- Fibonacci Confluence Score
- Fibonacci Bias
- Fibonacci Strength
- Institutional Decision
- Support Row / Price Input

"""

from strategies.fibonacci_engine import (

    is_discount,
    is_premium,
    is_golden_zone,
    is_deep_discount,
    is_deep_premium,

    retracement_strength,
    extension_strength,

)


# ==================================================
# PRICE EXTRACTOR
# ==================================================

def _price(row):

    """
    Support:

    - pandas Series
    - dataframe row
    - direct numeric price

    """

    if isinstance(row, (int, float)):

        return float(row)


    if hasattr(row, "get"):

        return row.get(

            "close",

            row.get(

                "Close",

                0

            )

        )


    return 0



# ==================================================
# FIBONACCI SCORE
# ==================================================

def fibonacci_score(

    price,

    levels,

):


    price = _price(price)


    score = 0



    # ------------------------------------------
    # Discount
    # ------------------------------------------

    if is_discount(

        price,

        levels,

    ):

        score += 20



    # ------------------------------------------
    # Premium
    # ------------------------------------------

    if is_premium(

        price,

        levels,

    ):

        score -= 20



    # ------------------------------------------
    # Golden Zone
    # ------------------------------------------

    if is_golden_zone(

        price,

        levels,

    ):

        score += 30



    # ------------------------------------------
    # Deep Discount
    # ------------------------------------------

    if is_deep_discount(

        price,

        levels,

    ):

        score += 30



    # ------------------------------------------
    # Deep Premium
    # ------------------------------------------

    if is_deep_premium(

        price,

        levels,

    ):

        score -= 30



    return score




# ==================================================
# RETRACEMENT SCORE
# ==================================================

def retracement_score(

    price,

    levels,

):


    price = _price(price)


    return retracement_strength(

        price,

        levels,

    )




# ==================================================
# EXTENSION SCORE
# ==================================================

def extension_score(

    price,

    levels,

):


    price = _price(price)


    return extension_strength(

        price,

        levels,

    )




# ==================================================
# TOTAL SCORE
# ==================================================

def total_score(

    price,

    levels,

):


    price = _price(price)


    return (

        fibonacci_score(

            price,

            levels,

        )

        +

        retracement_score(

            price,

            levels,

        )

        +

        extension_score(

            price,

            levels,

        )

    )




# ==================================================
# BIAS
# ==================================================

def fibonacci_bias(

    price,

    levels,

):


    price = _price(price)


    score = total_score(

        price,

        levels,

    )



    if score >= 120:

        return "STRONG_BUY"



    if score >= 60:

        return "BUY"



    if score <= -120:

        return "STRONG_SELL"



    if score <= -60:

        return "SELL"



    return "NEUTRAL"




# ==================================================
# DECISION BUY
# ==================================================

def should_buy(

    price,

    levels,

):


    price = _price(price)


    return fibonacci_bias(

        price,

        levels,

    ) in (

        "BUY",

        "STRONG_BUY",

    )




# ==================================================
# DECISION SELL
# ==================================================

def should_sell(

    price,

    levels,

):


    price = _price(price)


    return fibonacci_bias(

        price,

        levels,

    ) in (

        "SELL",

        "STRONG_SELL",

    )




# ==================================================
# SUMMARY
# ==================================================

def confluence_summary(

    price,

    levels,

):


    price = _price(price)



    fib_score = fibonacci_score(

        price,

        levels,

    )



    retr_score = retracement_score(

        price,

        levels,

    )



    ext_score = extension_score(

        price,

        levels,

    )



    total = (

        fib_score

        +

        retr_score

        +

        ext_score

    )



    return {


        "fibonacci_score":

            fib_score,


        "retracement_score":

            retr_score,


        "extension_score":

            ext_score,


        "total_score":

            total,


        "bias":

            fibonacci_bias(

                price,

                levels,

            ),


        "buy":

            should_buy(

                price,

                levels,

            ),


        "sell":

            should_sell(

                price,

                levels,

            ),

    }