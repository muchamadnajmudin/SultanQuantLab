"""
==========================================
SULTAN QUANT OS
Strategy Portfolio Manager
Version : 1.1.0
==========================================

Responsibilities:

- Execute multiple strategies
- Analyze strategy quality
- Rank strategies
- Select best strategy
- Return complete strategy result
"""

from copy import deepcopy

from engine.strategy_engine import run_strategy
from engine.backtest_engine import run_backtest
from engine.statistics_engine import calculate_statistics

from analyzer.strategy_analyzer import analyze_strategy
from analyzer.strategy_ranker import rank_strategies

from strategies.registry import list_strategies


# ==================================================
# STRATEGY MANAGER
# ==================================================

class StrategyManager:

    def __init__(self):

        self.strategies = list_strategies()

    # ==================================================

    def available(self):

        return self.strategies

    # ==================================================

    def evaluate(

        self,

        dataframe,

        strategy,

        **params,

    ):

        df = deepcopy(dataframe)

        df = run_strategy(

            df,

            strategy=strategy,

            **params,

        )

        trades = run_backtest(

            df,

        )

        statistics = calculate_statistics(

            trades,

        )

        analysis = analyze_strategy(

            statistics,

        )

        return {

            "name": strategy,

            "dataframe": df,

            "trades": trades,

            "statistics": statistics,

            "analysis": analysis,

        }

    # ==================================================

    def evaluate_all(

        self,

        dataframe,

    ):

        results = []

        for strategy in self.strategies:

            result = self.evaluate(

                dataframe,

                strategy,

            )

            results.append(

                result

            )

        return results

    # ==================================================

    def rank(

        self,

        dataframe,

    ):

        results = self.evaluate_all(

            dataframe,

        )

        return rank_strategies(

            results,

        )

    # ==================================================

    def best(

        self,

        dataframe,

    ):

        ranking = self.rank(

            dataframe,

        )

        if not ranking:

           return None

        return ranking[0]