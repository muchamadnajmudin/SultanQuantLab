"""
==========================================
SULTAN QUANT OS
Profit Distribution Analytics
Version : 4.3.0
==========================================

Responsibilities:

- Analyze trade profit distribution
- Separate winners and losers
- Calculate average performance

"""


# ==================================================
# PROFIT DISTRIBUTION
# ==================================================

def analyze_profit_distribution(
    trades: list[float],
):


    if not trades:

        return empty_distribution()



    winners = [

        trade

        for trade in trades

        if trade > 0

    ]


    losers = [

        trade

        for trade in trades

        if trade < 0

    ]



    average_win = (

        sum(winners)

        /

        len(winners)

        if winners

        else 0

    )


    average_loss = (

        sum(losers)

        /

        len(losers)

        if losers

        else 0

    )



    return {


        "total_trade":

            len(trades),


        "winning_trade":

            len(winners),


        "losing_trade":

            len(losers),


        "average_win":

            round(
                average_win,
                2
            ),


        "average_loss":

            round(
                average_loss,
                2
            ),


        "largest_win":

            max(winners)
            if winners
            else 0,


        "largest_loss":

            min(losers)
            if losers
            else 0,

    }



# ==================================================
# EMPTY RESULT
# ==================================================

def empty_distribution():

    return {


        "total_trade": 0,

        "winning_trade": 0,

        "losing_trade": 0,

        "average_win": 0,

        "average_loss": 0,

        "largest_win": 0,

        "largest_loss": 0,

    }