"""
==========================================
SULTAN QUANT OS
Correlation Engine
Version : 1.0.0
==========================================

Responsibilities

- Compare strategy results
- Detect duplicate exposure
- Calculate correlation score

"""


def calculate_correlation(strategy_a, strategy_b):

    if not strategy_a or not strategy_b:
        return 0.0

    trades_a = strategy_a.get(
        "statistics",
        {},
    ).get(
        "total_trade",
        0,
    )

    trades_b = strategy_b.get(
        "statistics",
        {},
    ).get(
        "total_trade",
        0,
    )

    if max(trades_a, trades_b) == 0:
        return 0.0

    difference = abs(
        trades_a - trades_b
    )

    score = 1 - (
        difference /
        max(trades_a, trades_b)
    )

    return round(
        max(0.0, score),
        4,
    )


def build_correlation_matrix(results):

    matrix = []

    for left in results:

        row = []

        for right in results:

            row.append(

                calculate_correlation(
                    left,
                    right,
                )

            )

        matrix.append(row)

    return matrix