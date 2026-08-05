from analyzer.strategy_ranker import rank_strategies


def test_strategy_ranker():

    strategies = [

        {
            "name": "Strategy A",
            "statistics": {
                "profit_factor": 2.1,
                "max_drawdown_percent": 12,
                "win_rate": 45,
            },
            "analysis": {
                "score": 90,
                "grade": "INSTITUTIONAL",
            },
        },

        {
            "name": "Strategy B",
            "statistics": {
                "profit_factor": 1.8,
                "max_drawdown_percent": 20,
                "win_rate": 48,
            },
            "analysis": {
                "score": 75,
                "grade": "GOOD",
            },
        },

        {
            "name": "Strategy C",
            "statistics": {
                "profit_factor": 1.2,
                "max_drawdown_percent": 45,
                "win_rate": 35,
            },
            "analysis": {
                "score": 40,
                "grade": "WEAK",
            },
        },

    ]

    ranking = rank_strategies(strategies)

    assert ranking[0]["name"] == "Strategy A"
    assert ranking[1]["name"] == "Strategy B"
    assert ranking[2]["name"] == "Strategy C"
    assert ranking[0]["rank"] == 1


def test_strategy_ranker_empty():

    ranking = rank_strategies([])

    assert ranking == []