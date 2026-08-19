"""
==========================================
SULTAN QUANT OS
Consensus Engine
Version : 1.0.0
==========================================

Responsibilities

- Final institutional consensus
- Confidence calculation
"""


from strategies.ensemble.portfolio_voting import (
    portfolio_vote,
)


def build_consensus(results):

    voting = portfolio_vote(
        results
    )

    total = (

        voting["buy_vote"]

        +

        voting["sell_vote"]

    )

    if total == 0:

        confidence = 0

    else:

        confidence = round(

            max(

                voting["buy_vote"],

                voting["sell_vote"],

            )

            / total

            * 100,

            2,

        )

    return {

        "signal":
            voting["signal"],

        "confidence":
            confidence,

        "buy_vote":
            voting["buy_vote"],

        "sell_vote":
            voting["sell_vote"],

    }