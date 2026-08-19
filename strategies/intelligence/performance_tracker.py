"""
==========================================

SULTAN QUANT OS

Performance Tracker

==========================================

"""


def calculate_performance(data):


    trades = data.get(

        "trades",

        0

    )


    wins = data.get(

        "wins",

        0

    )


    profit = data.get(

        "profit",

        0

    )


    if trades == 0:

        win_rate = 0

    else:

        win_rate = (

            wins / trades

        ) * 100



    return {


        "trades":

            trades,


        "wins":

            wins,


        "win_rate":

            win_rate,


        "profit":

            profit,

    }