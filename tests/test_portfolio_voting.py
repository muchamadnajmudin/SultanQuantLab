from strategies.ensemble.portfolio_voting import (
    portfolio_vote,
)


def test_portfolio_vote():

    results = [

        {

            "weight": 1.0,

            "statistics": {

                "profit_factor": 2.0,

            }

        },

        {

            "weight": 0.5,

            "statistics": {

                "profit_factor": 1.8,

            }

        },

        {

            "weight": 1.0,

            "statistics": {

                "profit_factor": 0.9,

            }

        },

    ]

    vote = portfolio_vote(
        results
    )

    assert vote["signal"] == "BUY"