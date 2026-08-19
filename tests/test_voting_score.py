from strategies.ensemble.voting_score import calculate_scores


def test_score():

    votes = [

        {"signal": "BUY", "weight": 0.4},

        {"signal": "BUY", "weight": 0.2},

        {"signal": "SELL", "weight": 0.4},

    ]

    result = calculate_scores(votes)

    assert result["BUY"] == 0.6

    assert result["SELL"] == 0.4