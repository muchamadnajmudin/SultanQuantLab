"""
==========================================
SULTAN QUANT OS
Voting Summary
==========================================
"""


def voting_summary(result):

    return {

        "decision": result["decision"],

        "confidence": result["confidence"],

        "buy_score": result["scores"].get("BUY", 0),

        "sell_score": result["scores"].get("SELL", 0),

        "hold_score": result["scores"].get("NO_TRADE", 0),

    }