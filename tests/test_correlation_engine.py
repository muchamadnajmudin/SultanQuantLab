from strategies.ensemble.correlation_engine import (
    calculate_correlation,
    build_correlation_matrix,
)


def test_correlation():

    a = {

        "statistics": {

            "total_trade": 100,

        }

    }

    b = {

        "statistics": {

            "total_trade": 100,

        }

    }

    assert calculate_correlation(a, b) == 1.0


def test_matrix():

    results = [

        {

            "statistics": {

                "total_trade": 10,

            }

        },

        {

            "statistics": {

                "total_trade": 20,

            }

        },

    ]

    matrix = build_correlation_matrix(
        results
    )

    assert len(matrix) == 2

    assert len(matrix[0]) == 2