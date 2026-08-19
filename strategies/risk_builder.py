"""
==========================================
SULTAN QUANT OS
Risk Builder
Version : 1.1.0
==========================================

Responsibilities:

- Calculate ATR Stop Loss
- Calculate ATR Take Profit
- Fixed Risk Reward
- Buy Levels
- Sell Levels
- Shared Risk Builder

"""

# ==================================================
# BUY LEVELS
# ==================================================

def calculate_buy_levels(

    entry,
    atr,
    sl_multiplier=1.0,
    rr=2.0,

):

    sl = entry - (atr * sl_multiplier)

    risk = entry - sl

    tp = entry + (risk * rr)

    return round(sl, 5), round(tp, 5)


# ==================================================
# SELL LEVELS
# ==================================================

def calculate_sell_levels(

    entry,
    atr,
    sl_multiplier=1.0,
    rr=2.0,

):

    sl = entry + (atr * sl_multiplier)

    risk = sl - entry

    tp = entry - (risk * rr)

    return round(sl, 5), round(tp, 5)


# ==================================================
# FIXED RR
# ==================================================

def calculate_rr_levels(

    entry,
    stop_loss,
    rr=2.0,
    side="BUY",

):

    side = side.upper()

    if side == "BUY":

        risk = entry - stop_loss

        take_profit = entry + (risk * rr)

        return round(stop_loss, 5), round(take_profit, 5)

    elif side == "SELL":

        risk = stop_loss - entry

        take_profit = entry - (risk * rr)

        return round(stop_loss, 5), round(take_profit, 5)

    raise ValueError("Side must be BUY or SELL")


# ==================================================
# VALIDATE
# ==================================================

def validate_levels(

    entry,
    sl,
    tp,
    side,

):

    side = side.upper()

    if side == "BUY":

        return sl < entry < tp

    elif side == "SELL":

        return tp < entry < sl

    raise ValueError("Side must be BUY or SELL")


# ==================================================
# BUILD RISK
# ==================================================

def build_risk(

    entry,
    atr,
    side,
    sl_multiplier=1.0,
    rr=2.0,

):

    """
    Shared wrapper
    Digunakan oleh seluruh strategi.
    """

    side = side.upper()

    if side == "BUY":

        return calculate_buy_levels(

            entry=entry,
            atr=atr,
            sl_multiplier=sl_multiplier,
            rr=rr,

        )

    elif side == "SELL":

        return calculate_sell_levels(

            entry=entry,
            atr=atr,
            sl_multiplier=sl_multiplier,
            rr=rr,

        )

    raise ValueError("Side must be BUY or SELL")