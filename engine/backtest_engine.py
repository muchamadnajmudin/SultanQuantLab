"""
==========================================
Sultan Quant Lab
Module : Backtest Engine
Version : 2.0
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

    total_rows = len(df)

    # mulai dari candle ke-1
    # karena entry menggunakan OPEN candle berikutnya
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
                    direction="BUY",
                    entry_time=next_candle["time"],
                    entry_price=entry_price,
                    stop_loss=sl,
                    take_profit=tp,
                )

            # ---------------- SELL ----------------

            elif candle["SELL"]:

                entry_price = next_candle["open"]

                sl, tp = calculate_sell_levels(
                    entry_price,
                    candle["ATR"]
                )

                current_trade = Trade(
                    direction="SELL",
                    entry_time=next_candle["time"],
                    entry_price=entry_price,
                    stop_loss=sl,
                    take_profit=tp,
                )

        # ==========================================
        # SUDAH ADA POSISI
        # ==========================================

        else:

            # ======================================
            # BUY
            # ======================================

            if current_trade.direction == "BUY":

                # Stop Loss

                if candle["low"] <= current_trade.stop_loss:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.stop_loss
                    current_trade.profit = (
                        current_trade.exit_price
                        - current_trade.entry_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "SL"

                    trades.append(current_trade)

                    current_trade = None

                # Take Profit

                elif candle["high"] >= current_trade.take_profit:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.take_profit
                    current_trade.profit = (
                        current_trade.exit_price
                        - current_trade.entry_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "TP"

                    trades.append(current_trade)

                    current_trade = None

            # ======================================
            # SELL
            # ======================================

            else:

                # Stop Loss

                if candle["high"] >= current_trade.stop_loss:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.stop_loss
                    current_trade.profit = (
                        current_trade.entry_price
                        - current_trade.exit_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "SL"

                    trades.append(current_trade)

                    current_trade = None

                # Take Profit

                elif candle["low"] <= current_trade.take_profit:

                    current_trade.exit_time = candle["time"]
                    current_trade.exit_price = current_trade.take_profit
                    current_trade.profit = (
                        current_trade.entry_price
                        - current_trade.exit_price
                    )

                    current_trade.status = "CLOSED"
                    current_trade.exit_reason = "TP"

                    trades.append(current_trade)

                    current_trade = None

    return trades