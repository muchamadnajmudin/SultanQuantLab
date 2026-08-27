"""
==========================================
SULTAN QUANT OS
Grid Candidate Pipeline
Version : 1.0.1
==========================================

Responsibilities:

- Process crypto candidates for grid trading
- Analyze market conditions
- Run grid research
- Combine crypto quality and grid metrics
- Rank grid candidates
- Preserve stable result contracts
- Handle invalid or failed candidates safely

Pipeline:

Crypto Universe
      ↓
Crypto Quality Analyzer
      ↓
Market Analyzer
      ↓
Grid Research
      ↓
Grid Pair Ranker
      ↓
Ranked Grid Candidates
"""

from copy import deepcopy

from engine.grid_pair_ranker import GridPairRanker


class GridCandidatePipeline:
    """
    End-to-end pipeline for evaluating and ranking
    crypto pairs as grid trading candidates.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    def __init__(
        self,
        quality_analyzer=None,
        market_analyzer=None,
        grid_research_engine=None,
        ranker=None,
    ):
        self.quality_analyzer = quality_analyzer
        self.market_analyzer = market_analyzer
        self.grid_research_engine = grid_research_engine
        self.ranker = ranker or GridPairRanker()

    def run(self, candidates):
        """
        Run the complete grid candidate pipeline.

        Parameters
        ----------
        candidates : list
            List of candidate dictionaries.

        Returns
        -------
        dict
            Stable pipeline result contract.
        """

        original_candidates = deepcopy(candidates)

        result = self._build_empty_result()

        if candidates is None:
            result["status"] = self.STATUS_EMPTY
            result["errors"].append("candidates is None")
            return deepcopy(result)

        if not isinstance(candidates, list):
            result["status"] = self.STATUS_ERROR
            result["errors"].append(
                "candidates must be a list"
            )
            return deepcopy(result)

        if not candidates:
            result["status"] = self.STATUS_EMPTY
            return deepcopy(result)

        processed_candidates = []

        for candidate in candidates:

            processed = self._process_candidate(
                candidate
            )

            if processed is None:
                result["failed_count"] += 1
                continue

            processed_candidates.append(
                deepcopy(processed)
            )

        result["processed_count"] = len(
            processed_candidates
        )

        result["failed_count"] = (
            len(candidates)
            - len(processed_candidates)
        )

        if not processed_candidates:
            result["status"] = self.STATUS_EMPTY
            result["input"] = original_candidates

            return deepcopy(result)

        ranked_candidates = self._rank_candidates(
            processed_candidates
        )

        result["candidates"] = deepcopy(
            ranked_candidates
        )

        result["ranked_count"] = len(
            ranked_candidates
        )

        if result["failed_count"] > 0:
            result["status"] = self.STATUS_PARTIAL
        else:
            result["status"] = self.STATUS_SUCCESS

        result["input"] = original_candidates

        return deepcopy(result)

    def process(self, candidates):
        """
        Alias for run().
        """

        return self.run(candidates)

    def execute(self, candidates):
        """
        Alias for run().
        """

        return self.run(candidates)

    def _process_candidate(self, candidate):
        """
        Process a single crypto candidate safely.
        """

        if not isinstance(candidate, dict):
            return None

        data = deepcopy(candidate)

        symbol = data.get("symbol")

        if not isinstance(symbol, str):
            return None

        symbol = symbol.strip()

        if not symbol:
            return None

        data["symbol"] = symbol

        try:

            quality_result = self._analyze_quality(
                data
            )

            if isinstance(quality_result, dict):

                data["quality"] = deepcopy(
                    quality_result
                )

                self._merge_quality_result(
                    data,
                    quality_result,
                )

            market_result = self._analyze_market(
                data
            )

            if isinstance(market_result, dict):

                data["market"] = deepcopy(
                    market_result
                )

                self._merge_market_result(
                    data,
                    market_result,
                )

            research_result = self._run_grid_research(
                data
            )

            if isinstance(research_result, dict):

                data["grid_research"] = deepcopy(
                    research_result
                )

                self._merge_research_result(
                    data,
                    research_result,
                )

            return deepcopy(data)

        except Exception:
            return None

    def _analyze_quality(self, candidate):
        """
        Run crypto quality analysis if an analyzer exists.
        """

        if self.quality_analyzer is None:
            return None

        analyzer = self.quality_analyzer

        if hasattr(analyzer, "analyze"):
            return analyzer.analyze(
                deepcopy(candidate)
            )

        if hasattr(analyzer, "run"):
            return analyzer.run(
                deepcopy(candidate)
            )

        if callable(analyzer):
            return analyzer(
                deepcopy(candidate)
            )

        return None

    def _analyze_market(self, candidate):
        """
        Run market analysis if an analyzer exists.
        """

        if self.market_analyzer is None:
            return None

        analyzer = self.market_analyzer

        if hasattr(analyzer, "analyze"):
            return analyzer.analyze(
                deepcopy(candidate)
            )

        if hasattr(analyzer, "run"):
            return analyzer.run(
                deepcopy(candidate)
            )

        if callable(analyzer):
            return analyzer(
                deepcopy(candidate)
            )

        return None

    def _run_grid_research(self, candidate):
        """
        Run grid research if a research engine exists.
        """

        if self.grid_research_engine is None:
            return None

        engine = self.grid_research_engine

        if hasattr(engine, "analyze"):
            return engine.analyze(
                deepcopy(candidate)
            )

        if hasattr(engine, "run"):
            return engine.run(
                deepcopy(candidate)
            )

        if callable(engine):
            return engine(
                deepcopy(candidate)
            )

        return None

    def _merge_quality_result(
        self,
        candidate,
        quality_result,
    ):
        """
        Merge quality analysis into candidate data.
        """

        for key in (
            "quality_score",
            "crypto_quality_score",
            "score",
        ):
            if key in quality_result:

                candidate["quality_score"] = (
                    quality_result[key]
                )

                break

    def _merge_market_result(
        self,
        candidate,
        market_result,
    ):
        """
        Merge market analysis into candidate data.
        """

        for key in (
            "market_regime",
            "regime",
        ):
            if key in market_result:

                candidate["market_regime"] = (
                    market_result[key]
                )

                break

        for key in (
            "volatility",
            "normalized_volatility",
        ):
            if key in market_result:

                candidate["volatility"] = (
                    market_result[key]
                )

                break

    def _merge_research_result(
        self,
        candidate,
        research_result,
    ):
        """
        Merge grid research metrics into candidate data.
        """

        for key in (
            "profitability_score",
            "grid_score",
            "score",
        ):
            if key in research_result:

                candidate["profitability_score"] = (
                    research_result[key]
                )

                break

        for key in (
            "recovery_score",
            "recovery_probability",
            "conditional_recovery",
        ):
            if key in research_result:

                candidate["recovery_score"] = (
                    research_result[key]
                )

                break

        for key in (
            "drawdown",
            "max_drawdown",
        ):
            if key in research_result:

                candidate["drawdown"] = (
                    research_result[key]
                )

                break

    def _rank_candidates(self, candidates):
        """
        Rank processed candidates using GridPairRanker.

        The order returned by the ranker is preserved.

        Upstream analysis data is restored from the
        original processed candidate using the symbol
        as the identity key, so ranker defaults cannot
        overwrite analyzer or research results.
        """

        original_candidates = deepcopy(candidates)

        if self.ranker is None:
            return deepcopy(original_candidates)

        ranker = self.ranker

        ranked_result = None

        try:

            if hasattr(ranker, "rank"):

                ranked_result = ranker.rank(
                    deepcopy(original_candidates)
                )

            elif callable(ranker):

                ranked_result = ranker(
                    deepcopy(original_candidates)
                )

        except Exception:
            return deepcopy(original_candidates)

        if not isinstance(ranked_result, list):
            return deepcopy(original_candidates)

        original_by_symbol = {}

        for candidate in original_candidates:

            if not isinstance(candidate, dict):
                continue

            symbol = candidate.get("symbol")

            if not isinstance(symbol, str):
                continue

            original_by_symbol[symbol] = deepcopy(
                candidate
            )

        merged_candidates = []

        protected_keys = {
            "symbol",
            "quality",
            "quality_score",
            "market",
            "market_regime",
            "volatility",
            "grid_research",
            "profitability_score",
            "recovery_score",
            "drawdown",
            "metadata",
        }

        ranking_keys = {
            "grid_score",
            "rank",
            "status",
            "drawdown_score",
            "market_score",
            "volatility_score",
            "details",
        }

        for ranked_candidate in ranked_result:

            if not isinstance(
                ranked_candidate,
                dict,
            ):
                continue

            ranked_symbol = ranked_candidate.get(
                "symbol"
            )

            if (
                not isinstance(
                    ranked_symbol,
                    str,
                )
                or ranked_symbol
                not in original_by_symbol
            ):
                merged_candidates.append(
                    deepcopy(ranked_candidate)
                )
                continue

            original_candidate = deepcopy(
                original_by_symbol[
                    ranked_symbol
                ]
            )

            merged_candidate = deepcopy(
                original_candidate
            )

            for key in ranking_keys:

                if key in ranked_candidate:

                    merged_candidate[key] = deepcopy(
                        ranked_candidate[key]
                    )

            for key, value in (
                ranked_candidate.items()
            ):

                if key in protected_keys:
                    continue

                if key in ranking_keys:
                    continue

                if key not in merged_candidate:

                    merged_candidate[key] = deepcopy(
                        value
                    )

            merged_candidates.append(
                deepcopy(merged_candidate)
            )

        if not merged_candidates:
            return deepcopy(original_candidates)

        return deepcopy(merged_candidates)

    def _build_empty_result(self):
        """
        Build stable pipeline result contract.
        """

        return {
            "status": self.STATUS_EMPTY,
            "candidates": [],
            "processed_count": 0,
            "failed_count": 0,
            "ranked_count": 0,
            "errors": [],
            "input": None,
        }


def run_grid_candidate_pipeline(
    candidates,
    quality_analyzer=None,
    market_analyzer=None,
    grid_research_engine=None,
    ranker=None,
):
    """
    Convenience function for running
    the Grid Candidate Pipeline.
    """

    pipeline = GridCandidatePipeline(
        quality_analyzer=quality_analyzer,
        market_analyzer=market_analyzer,
        grid_research_engine=grid_research_engine,
        ranker=ranker,
    )

    return pipeline.run(candidates)