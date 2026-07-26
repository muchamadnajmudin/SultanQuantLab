from engine.optimizer_engine import rank_results


def test_optimizer_ranking():

    results = [

        {
            "ema": 20,
            "profit_factor": 1.7,
            "net_profit": 68
        },

        {
            "ema": 30,
            "profit_factor": 2.1,
            "net_profit": 90
        },

        {
            "ema": 50,
            "profit_factor": 1.4,
            "net_profit": 55
        }

    ]


    ranking = rank_results(results)


    assert ranking[0]["ema"] == 30
    assert ranking[1]["ema"] == 20
    assert ranking[2]["ema"] == 50