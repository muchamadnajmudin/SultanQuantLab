"""
==========================================
SULTAN QUANT OS
Price Action Patterns
Version : 2.0.0
==========================================

Responsibilities

- Bullish Engulfing
- Bearish Engulfing
- Pin Bar
- Inside Bar
- Outside Bar

"""


# ==================================================
# BULLISH ENGULFING
# ==================================================

def bullish_engulfing(prev_open, prev_close, open_price, close_price):

    return (

        prev_close < prev_open

        and close_price > open_price

        and close_price >= prev_open

        and open_price <= prev_close

    )


# ==================================================
# BEARISH ENGULFING
# ==================================================

def bearish_engulfing(prev_open, prev_close, open_price, close_price):

    return (

        prev_close > prev_open

        and close_price < open_price

        and open_price >= prev_close

        and close_price <= prev_open

    )


# ==================================================
# PIN BAR BUY
# ==================================================

def bullish_pinbar(open_price, high, low, close_price):

    body = abs(close_price - open_price)

    if body == 0:
        body = 0.0000001

    upper = high - max(open_price, close_price)

    lower = min(open_price, close_price) - low

    return (

        lower > body * 2

        and upper < body

    )


# ==================================================
# PIN BAR SELL
# ==================================================

def bearish_pinbar(open_price, high, low, close_price):

    body = abs(close_price - open_price)

    if body == 0:
        body = 0.0000001

    upper = high - max(open_price, close_price)

    lower = min(open_price, close_price) - low

    return (

        upper > body * 2

        and lower < body

    )


# ==================================================
# INSIDE BAR
# ==================================================

def inside_bar(

    previous_high,
    previous_low,
    high,
    low,

):

    return (

        high < previous_high

        and low > previous_low

    )


# ==================================================
# OUTSIDE BAR
# ==================================================

def outside_bar(

    previous_high,
    previous_low,
    high,
    low,

):

    return (

        high > previous_high

        and low < previous_low

    )


# ==================================================
# COLUMN ADAPTER
# ==================================================

def get_price(row, upper_name, lower_name):

    if upper_name in row.index:
        return row[upper_name]

    return row[lower_name]


# ==================================================
# DETECT PATTERNS
# ==================================================

def detect_patterns(df):

    bullish = []
    bearish = []
    bullish_pin = []
    bearish_pin = []
    inside = []
    outside = []

    for i in range(len(df)):

        if i == 0:

            bullish.append(False)
            bearish.append(False)
            bullish_pin.append(False)
            bearish_pin.append(False)
            inside.append(False)
            outside.append(False)

            continue

        prev = df.iloc[i - 1]
        row = df.iloc[i]

        prev_open = get_price(prev, "Open", "open")
        prev_high = get_price(prev, "High", "high")
        prev_low = get_price(prev, "Low", "low")
        prev_close = get_price(prev, "Close", "close")

        open_price = get_price(row, "Open", "open")
        high = get_price(row, "High", "high")
        low = get_price(row, "Low", "low")
        close_price = get_price(row, "Close", "close")

        bullish.append(

            bullish_engulfing(

                prev_open,
                prev_close,
                open_price,
                close_price,

            )

        )

        bearish.append(

            bearish_engulfing(

                prev_open,
                prev_close,
                open_price,
                close_price,

            )

        )

        bullish_pin.append(

            bullish_pinbar(

                open_price,
                high,
                low,
                close_price,

            )

        )

        bearish_pin.append(

            bearish_pinbar(

                open_price,
                high,
                low,
                close_price,

            )

        )

        inside.append(

            inside_bar(

                prev_high,
                prev_low,
                high,
                low,

            )

        )

        outside.append(

            outside_bar(

                prev_high,
                prev_low,
                high,
                low,

            )

        )

    df["BULLISH_ENGULFING"] = bullish
    df["BEARISH_ENGULFING"] = bearish
    df["BULLISH_PINBAR"] = bullish_pin
    df["BEARISH_PINBAR"] = bearish_pin
    df["INSIDE_BAR"] = inside
    df["OUTSIDE_BAR"] = outside

    return df