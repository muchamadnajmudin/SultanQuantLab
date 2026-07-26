"""
==========================================
SULTAN QUANT OS
Monthly Returns Analytics
Version : 4.4.0
==========================================

Responsibilities:

- Group trade results by month
- Calculate monthly performance

"""


from collections import defaultdict



# ==================================================
# MONTHLY RETURNS
# ==================================================

def calculate_monthly_returns(
    trades: list[dict],
):


    if not trades:

        return {}



    monthly = defaultdict(
        float
    )



    for trade in trades:


        month = trade.get(
            "month"
        )


        profit = trade.get(
            "profit",
            0
        )


        if month:

            monthly[month] += profit



    return dict(
        monthly
    )



# ==================================================
# BEST MONTH
# ==================================================

def best_month(
    monthly_returns: dict,
):


    if not monthly_returns:

        return None



    return max(

        monthly_returns,

        key=monthly_returns.get

    )



# ==================================================
# WORST MONTH
# ==================================================

def worst_month(
    monthly_returns: dict,
):


    if not monthly_returns:

        return None



    return min(

        monthly_returns,

        key=monthly_returns.get

    )