from strategies.ensemble.voting_engine import ensemble_vote


def test_buy_vote():

    votes = [

        {"signal": "BUY", "weight": 0.4},

        {"signal": "BUY", "weight": 0.3},

        {"signal": "SELL", "weight": 0.3},

    ]

    result = ensemble_vote(votes)

    assert result["decision"] == "BUY"


def test_sell_vote():

    votes = [

        {"signal": "SELL", "weight": 0.6},

        {"signal": "BUY", "weight": 0.4},

    ]

    result = ensemble_vote(votes)

    assert result["decision"] == "SELL"


def test_draw_vote():

    votes = [

        {"signal": "BUY", "weight": 0.5},

        {"signal": "SELL", "weight": 0.5},

    ]

    result = ensemble_vote(votes)

    assert result["decision"] == "NO_TRADE"