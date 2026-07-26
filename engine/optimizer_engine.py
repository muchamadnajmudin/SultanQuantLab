"""
==========================================
SULTAN QUANT OS
Optimizer Engine
Version : 3.1.0
==========================================

Support:

- File based optimizer (legacy)
- DataFrame optimizer (WFO)
- Grid Search
- Ranking

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
    Menjalankan satu kombinasi parameter
    menggunakan file data.

    Legacy optimizer.
    """

    df = load_data(
        data_file
    )


    return run_dataframe_test(
        df=df,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
    )



# =====================================================
# DATAFRAME BACKTEST TEST
# =====================================================

def run_dataframe_test(
    df,
    rsi_oversold: int,
    rsi_overbought: int,
) -> dict:
    """
    Menjalankan satu kombinasi parameter
    menggunakan dataframe.

    Digunakan oleh Walk Forward Optimization.
    """


    data = df.copy()



    data = calculate_indicators(
        data
    )



    data = run_strategy(
        data,
        rsi_oversold=rsi_oversold,
        rsi_overbought=rsi_overbought,
    )



    trades = run_backtest(
        data
    )



    stats = calculate_statistics(
        trades
    )



    stats["RSI_OVERSOLD"] = (
        rsi_oversold
    )


    stats["RSI_OVERBOUGHT"] = (
        rsi_overbought
    )



    return stats



# =====================================================
# GRID SEARCH FILE MODE
# =====================================================

def optimize(
    data_file: str,
    parameter_grid: dict,
) -> list[dict]:
    """
    Grid Search menggunakan file.

    Digunakan optimizer lama.
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
# GRID SEARCH DATAFRAME MODE
# =====================================================

def optimize_dataframe(
    df,
    parameter_grid: dict,
) -> list[dict]:
    """
    Grid Search menggunakan dataframe.

    Digunakan oleh Walk Forward Optimization.

    Data sudah dipisahkan menjadi
    training window.
    """


    results = []



    combinations = product(

        parameter_grid["RSI_OVERSOLD"],

        parameter_grid["RSI_OVERBOUGHT"],

    )



    for oversold, overbought in combinations:


        result = run_dataframe_test(

            df=df,

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