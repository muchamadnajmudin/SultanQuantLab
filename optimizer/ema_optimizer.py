"""
==========================================
SULTAN QUANT OS
EMA Optimizer
Version : 2.0
==========================================
"""

from itertools import product


def generate_ema_list(
    start: int = 20,
    stop: int = 100,
    step: int = 5,
) -> list[int]:
    """
    Generate daftar EMA.
    """

    return list(
        range(
            start,
            stop + 1,
            step,
        )
    )


def generate_ema_combinations(
    fast_list: list[int],
    middle_list: list[int],
    slow_list: list[int],
) -> list[tuple]:
    """
    Membuat kombinasi EMA
    dengan syarat:
    EMA Fast < EMA Middle < EMA Slow
    """

    combinations = []

    for fast, middle, slow in product(
        fast_list,
        middle_list,
        slow_list,
    ):

        if fast < middle < slow:

            combinations.append(
                (
                    fast,
                    middle,
                    slow,
                )
            )

    return combinations


if __name__ == "__main__":

    fast = generate_ema_list(
        10,
        40,
        5,
    )

    middle = generate_ema_list(
        30,
        100,
        5,
    )

    slow = generate_ema_list(
        100,
        300,
        10,
    )

    result = generate_ema_combinations(
        fast,
        middle,
        slow,
    )

    print(
        f"Total Combination : {len(result)}"
    )

    print(result[:20])