"""
==========================================
SULTAN QUANT LAB
Module : Risk Engine
Version : 0.3
==========================================
"""

from config.settings import (
    ATR_SL_MULTIPLIER,
    ATR_TP_MULTIPLIER,
    RISK_PER_TRADE,
)


# =====================================================
# ATR STOP LOSS & TAKE PROFIT
# =====================================================

def calculate_buy_levels(
    entry_price: float,
    atr: float,
    sl_multiplier: float = ATR_SL_MULTIPLIER,
    tp_multiplier: float = ATR_TP_MULTIPLIER,
):
    """
    Menghitung Stop Loss & Take Profit BUY
    berdasarkan ATR.
    """

    if atr <= 0:
        raise ValueError("ATR tidak valid.")

    stop_loss = entry_price - (atr * sl_multiplier)
    take_profit = entry_price + (atr * tp_multiplier)

    return stop_loss, take_profit


def calculate_sell_levels(
    entry_price: float,
    atr: float,
    sl_multiplier: float = ATR_SL_MULTIPLIER,
    tp_multiplier: float = ATR_TP_MULTIPLIER,
):
    """
    Menghitung Stop Loss & Take Profit SELL
    berdasarkan ATR.
    """

    if atr <= 0:
        raise ValueError("ATR tidak valid.")

    stop_loss = entry_price + (atr * sl_multiplier)
    take_profit = entry_price - (atr * tp_multiplier)

    return stop_loss, take_profit


# =====================================================
# RISK
# =====================================================

def calculate_risk_amount(
    balance: float,
    risk_percent: float = RISK_PER_TRADE,
) -> float:
    """
    Menghitung nominal uang yang dirisikokan.
    """

    if balance <= 0:
        raise ValueError("Balance harus lebih besar dari nol.")

    return balance * risk_percent


# =====================================================
# POSITION SIZE
# =====================================================

def calculate_position_size(
    balance: float,
    entry_price: float,
    stop_loss: float,
    value_per_point: float = 1.0,
    risk_percent: float = RISK_PER_TRADE,
    minimum_lot: float = 0.01,
) -> float:
    """
    Menghitung ukuran lot berdasarkan risk.

    value_per_point
        Nilai uang setiap 1 point untuk 1 lot.

    minimum_lot
        Lot minimum broker.
    """

    if balance <= 0:
        raise ValueError("Balance harus lebih besar dari nol.")

    risk_amount = calculate_risk_amount(
        balance,
        risk_percent,
    )

    stop_distance = abs(entry_price - stop_loss)

    if stop_distance <= 0:
        raise ValueError("Stop Loss tidak valid.")

    lot = risk_amount / (
        stop_distance * value_per_point
    )

    lot = round(lot, 2)

    return max(lot, minimum_lot)


# =====================================================
# RISK REWARD
# =====================================================

def calculate_risk_reward(
    entry_price: float,
    stop_loss: float,
    take_profit: float,
) -> float:
    """
    Menghitung Risk Reward Ratio.
    """

    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)

    if risk <= 0:
        raise ValueError("Risk tidak boleh nol.")

    return round(
        reward / risk,
        2,
    )