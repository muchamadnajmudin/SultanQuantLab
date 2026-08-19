"""
==========================================
SULTAN QUANT OS
Ensemble Voting Engine
Version : 1.0.0
==========================================
"""

from strategies.ensemble.voting_score import (
    calculate_scores,
)


def ensemble_vote(votes):

    if not votes:

        return {

            "decision": "NO_TRADE",

            "confidence": 0,

            "scores": {},

        }

    scores = calculate_scores(votes)

    buy = scores.get("BUY", 0)

    sell = scores.get("SELL", 0)

    hold = scores.get("NO_TRADE", 0)

    total = buy + sell + hold

    if total == 0:

        return {

            "decision": "NO_TRADE",

            "confidence": 0,

            "scores": scores,

        }

    if buy > sell:

        decision = "BUY"

        confidence = round(
            buy / total * 100,
            2,
        )

    elif sell > buy:

        decision = "SELL"

        confidence = round(
            sell / total * 100,
            2,
        )

    else:

        decision = "NO_TRADE"

        confidence = 50

    return {

        "decision": decision,

        "confidence": confidence,

        "scores": scores,

    }