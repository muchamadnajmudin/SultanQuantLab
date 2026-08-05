"""
==========================================
SULTAN QUANT OS
Strategy Ranking Engine
Version : 3.2.0
==========================================

Responsibilities:

- Rank multiple strategies
- Compare strategy quality
- Sort by institutional score
"""

from copy import deepcopy


def rank_strategies(strategy_results: list[dict]):

    """
    Rank strategies from best to worst.

    Parameters
    ----------
    strategy_results : list[dict]

    Returns
    -------
    list[dict]
    """

    if not strategy_results:
        return []

    ranking = deepcopy(strategy_results)

    ranking.sort(

        key=lambda x: (

            x["analysis"].get("score", 0),

            x["statistics"].get("profit_factor", 0),

            -x["statistics"].get("max_drawdown_percent", 100),

            x["statistics"].get("win_rate", 0),

        ),

        reverse=True,

    )

    results = []

    for index, strategy in enumerate(ranking, start=1):

        results.append(

            {

                "rank": index,

                "name": strategy["name"],

                "score": strategy["analysis"].get("score"),

                "grade": strategy["analysis"].get("grade"),

                "profit_factor": strategy["statistics"].get(
                    "profit_factor"
                ),

                "drawdown": strategy["statistics"].get(
                    "max_drawdown_percent"
                ),

                "win_rate": strategy["statistics"].get(
                    "win_rate"
                ),

            }

        )

    return results