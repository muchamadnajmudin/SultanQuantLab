"""
==========================================
SULTAN QUANT OS
Portfolio Voting Engine
Version : 1.0.0
==========================================

Responsibilities

- Collect strategy votes
- Weighted voting
- Portfolio consensus
"""


def portfolio_vote(results):

    buy = 0.0
    sell = 0.0

    for item in results:

        statistics = item.get(
            "statistics",
            {}
        )

        weight = item.get(
            "weight",
            1.0
        )

        pf = statistics.get(
            "profit_factor",
            0
        )

        if pf >= 1.50:

            buy += weight

        else:

            sell += weight

    if buy > sell:

        signal = "BUY"

    elif sell > buy:

        signal = "SELL"

    else:

        signal = "NEUTRAL"

    return {

        "signal": signal,

        "buy_vote": round(
            buy,
            4,
        ),

        "sell_vote": round(
            sell,
            4,
        ),

    }