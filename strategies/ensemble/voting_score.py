"""
==========================================
SULTAN QUANT OS
Voting Score Engine
Version : 1.1.0
==========================================

Responsibilities:

- Calculate weighted vote
- Normalize vote score
"""


# ==================================================
# CALCULATE SCORES
# ==================================================

def calculate_scores(votes):

    scores = {
        "BUY": 0.0,
        "SELL": 0.0,
        "HOLD": 0.0,
    }

    for vote in votes:

        signal = vote["signal"]

        weight = vote.get(
            "weight",
            1.0,
        )

        if signal in scores:

            scores[signal] += weight

    # ------------------------------------------
    # Floating Point Cleanup
    # ------------------------------------------

    for key in scores:

        scores[key] = round(
            scores[key],
            4,
        )

    return scores