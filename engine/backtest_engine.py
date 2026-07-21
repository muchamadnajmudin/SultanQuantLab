"""
==========================================
Sultan Quant Lab
Module : Backtest Engine
Version : 2.2
==========================================
"""

from engine.trade import Trade
from engine.risk_engine import (
    calculate_buy_levels,
    calculate_sell_levels,
)


def run_backtest(df):

    trades = []

    current_trade = None

    trade_number = 1

    total_rows = len(df)

    for i in range(total_rows - 1):

        candle = df.iloc[i]
        next_candle = df.iloc[i + 1]

        # ==========================================
        # BELUM ADA POSISI
        # ==========================================

        if current_trade is None:

            # ---------------- BUY ----------------

            if candle["BUY"]:

                entry_price = next_candle["open"]

                sl, tp = calculate_buy_levels(
                    entry_price,
                    candle["ATR"]
                )

                current_trade = Trade(
                    trade_number=trade_number,
                    direction="BUY",

                    entry_time=next_candle["time"],
                    entry_price=entry_price,

                    stop_loss=sl,
                    take_profit=tp,

                    atr=float(candle["ATR"]),
                    adx=float(candle["ADX"]),
                    rsi=float(candle["RSI"]),

                    ema20=float(candle["EMA20"]),
                    ema50=float(candle["EMA50"]),
                    ema200=float(candle["EMA200"]),

                    stoch_k=float(candle["%K"]),
                    stoch_d=float(candle["%D"]),
                )

            # ---------------- SELL ----------------

            elif candle["SELL"]:

                entry_price = next_candle["open"]

                sl, tp = calculate_sell_levels(
                    entry_price,
                    candle["ATR"]
                )

                current_trade = Trade(
                    trade_number=trade_number,
                    direction="SELL",

                    entry_time=next_candle["time"],
                    entry_price=entry_price,

                    stop_loss=sl,
                    take_profit=tp,

                    atr=float(candle["ATR"]),
                    adx=float(candle["ADX"]),
                    rsi=float(candle["RSI"]),

                    ema20=float(candle["EMA20"]),
                    ema50=float(candle["EMA50"]),
                    ema200=float(candle["EMA200"]),

                    stoch_k=float(candle["%K"]),
                    stoch_d=float(candle["%D"]),
                )

        # ==========================================
        # SUDAH ADA POSISI
        # ==========================================

        else:

            if current_trade.direction == "BUY":

                # STOP LOSS

                if candle["low"] <= current_trade.stop_loss:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.stop_loss

                    current_trade.profit = (
                        current_trade.exit_price
                        - current_trade.entry_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "SL"

                    current_trade.duration = (
                        current_trade.exit_time
                        - current_trade.entry_time
                    ).total_seconds()

                    trades.append(current_trade)

                    trade_number += 1
                    current_trade = None

                # TAKE PROFIT

                elif candle["high"] >= current_trade.take_profit:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.take_profit

                    current_trade.profit = (
                        current_trade.exit_price
                        - current_trade.entry_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "TP"

                    current_trade.duration = (
                        current_trade.exit_time
                        - current_trade.entry_time
                    ).total_seconds()

                    trades.append(current_trade)

                    trade_number += 1
                    current_trade = None

            else:

                # STOP LOSS

                if candle["high"] >= current_trade.stop_loss:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.stop_loss

                    current_trade.profit = (
                        current_trade.entry_price
                        - current_trade.exit_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "SL"

                    current_trade.duration = (
                        current_trade.exit_time
                        - current_trade.entry_time
                    ).total_seconds()

                    trades.append(current_trade)

                    trade_number += 1
                    current_trade = None

                # TAKE PROFIT

                elif candle["low"] <= current_trade.take_profit:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.take_profit

                    current_trade.profit = (
                        current_trade.entry_price
                        - current_trade.exit_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "TP"

                    current_trade.duration = (
                        current_trade.exit_time
                        - current_trade.entry_time
                    ).total_seconds()

                    trades.append(current_trade)

                    trade_number += 1
                    current_trade = None

    return trades