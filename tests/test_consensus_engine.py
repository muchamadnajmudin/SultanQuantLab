from strategies.ensemble.consensus_engine import (
    build_consensus,
)


def test_consensus():

    results = [

        {

            "weight": 1,

            "statistics": {

                "profit_factor": 2,

            }

        },

        {

            "weight": 1,

            "statistics": {

                "profit_factor": 2,

            }

        },

    ]

    result = build_consensus(
        results
    )

    assert result["signal"] == "BUY"

    assert result["confidence"] == 100