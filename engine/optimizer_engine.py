"""
==========================================
SULTAN QUANT OS
Optimizer Engine
Version : 2.5.0
==========================================
"""

from itertools import product

from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics



# =====================================================
# SINGLE BACKTEST TEST
# =====================================================

def run_single_test(
    data_file: str,
    rsi_oversold: int,
    rsi_overbought: int,
) -> dict:
    """
    Menjalankan satu kombinasi parameter.
    """

    df = load_data(
        data_file
    )


    df = calculate_indicators(
        df
    )


    df = run_strategy(
        df,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
    )


    trades = run_backtest(
        df
    )


    stats = calculate_statistics(
        trades
    )


    stats["RSI_OVERSOLD"] = rsi_oversold
    stats["RSI_OVERBOUGHT"] = rsi_overbought


    return stats



# =====================================================
# GRID SEARCH
# =====================================================

def optimize(
    data_file: str,
    parameter_grid: dict,
) -> list[dict]:
    """
    Grid Search Optimizer.

    Input:

    {
        "RSI_OVERSOLD":[5,10,15],
        "RSI_OVERBOUGHT":[85,90,95]
    }


    Output:

    list hasil statistik
    """


    results = []


    combinations = product(

        parameter_grid["RSI_OVERSOLD"],

        parameter_grid["RSI_OVERBOUGHT"],

    )


    for oversold, overbought in combinations:


        result = run_single_test(

            data_file=data_file,

            rsi_oversold=oversold,

            rsi_overbought=overbought,

        )


        results.append(
            result
        )


    return rank_results(
        results
    )



# =====================================================
# RANKING
# =====================================================

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

            x.get(
                "profit_factor",
                0
            ),

            x.get(
                "net_profit",
                0
            ),

        ),

        reverse=True,

    )



# =====================================================
# BEST RESULT
# =====================================================

def get_best_result(
    results: list[dict],
) -> dict:
    """
    Mengambil hasil terbaik.
    """


    if not results:

        return {}


    return results[0]