"""
==========================================
SULTAN QUANT OS
Optimizer Engine
Version : 2.1
==========================================
"""

from itertools import product

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics


def run_single_test(
    data_file: str,
    rsi_oversold: int,
    rsi_overbought: int,
) -> dict:
    """
    Menjalankan satu kali backtest.
    """

    df = load_data(data_file)

    df = calculate_indicators(df)

    df = run_strategy(
        df,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
    )

    trades = run_backtest(df)

    stats = calculate_statistics(trades)

    stats["RSI_OVERSOLD"] = rsi_oversold
    stats["RSI_OVERBOUGHT"] = rsi_overbought

    return stats


def optimize(
    data_file: str,
    parameter_grid: dict,
) -> list[dict]:
    """
    Grid Search Optimizer.
    """

    results = []

    for oversold, overbought in product(
        parameter_grid["RSI_OVERSOLD"],
        parameter_grid["RSI_OVERBOUGHT"],
    ):

        result = run_single_test(
            data_file=data_file,
            rsi_oversold=oversold,
            rsi_overbought=overbought,
        )

        results.append(result)

    return rank_results(results)


def rank_results(
    results: list[dict],
) -> list[dict]:
    """
    Ranking berdasarkan:
    1. Profit Factor
    2. Net Profit
    """

    return sorted(
        results,
        key=lambda x: (
            x["profit_factor"],
            x["net_profit"],
        ),
        reverse=True,
    )


def get_best_result(
    results: list[dict],
) -> dict:

    if not results:
        return {}

    return results[0]