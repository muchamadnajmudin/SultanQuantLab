from strategies.ensemble.voting_summary import voting_summary


def test_summary():

    result = {

        "decision": "BUY",

        "confidence": 75,

        "scores": {

            "BUY": 0.75,

            "SELL": 0.25,

        }

    }

    summary = voting_summary(result)

    assert summary["decision"] == "BUY"

    assert summary["buy_score"] == 0.75