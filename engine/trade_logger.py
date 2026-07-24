"""
==========================================
Sultan Quant Lab
Module : Trade Logger
Version : 2.1
==========================================
"""

from pathlib import Path
import csv


def save_trade_journal(
    trades,
    filename="reports/output/trade_journal.csv",
):

    file_path = Path(filename)

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as csvfile:


        writer = csv.writer(csvfile)


        writer.writerow([

            "Trade No",
            "Entry Time",
            "Exit Time",
            "Duration (Sec)",

            "Symbol",
            "Timeframe",
            "Strategy",
            "Direction",

            "Entry Price",
            "Exit Price",

            "Stop Loss",
            "Take Profit",

            "Risk Reward",

            "Profit",
            "Profit %",

            "ATR",
            "ADX",
            "RSI",

            "EMA20",
            "EMA50",
            "EMA200",

            "Stoch K",
            "Stoch D",

            "Status",
            "Exit Reason",

            "Score",
            "Confidence",

        ])



        for trade in trades:


            writer.writerow([


                trade.trade_number,


                trade.entry_time,

                trade.exit_time,


                round(
                    trade.duration,
                    2
                ),



                trade.symbol,

                trade.timeframe,

                trade.strategy,

                trade.direction,



                round(
                    trade.entry_price,
                    5
                ),


                round(
                    trade.exit_price,
                    5
                ),



                round(
                    trade.stop_loss,
                    5
                ),


                round(
                    trade.take_profit,
                    5
                ),



                round(
                    trade.risk_reward,
                    2
                ),



                round(
                    trade.profit,
                    2
                ),


                round(
                    trade.profit_percent,
                    2
                ),



                round(
                    trade.atr,
                    5
                ),


                round(
                    trade.adx,
                    2
                ),


                round(
                    trade.rsi,
                    2
                ),



                round(
                    trade.ema20,
                    5
                ),


                round(
                    trade.ema50,
                    5
                ),


                round(
                    trade.ema200,
                    5
                ),



                round(
                    trade.stoch_k,
                    2
                ),


                round(
                    trade.stoch_d,
                    2
                ),



                trade.status,


                trade.exit_reason,



                round(
                    trade.score,
                    2
                ),


                round(
                    trade.confidence,
                    2
                ),

            ])


    return file_path