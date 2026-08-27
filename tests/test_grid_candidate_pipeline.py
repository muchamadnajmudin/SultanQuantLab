"""
==========================================
SULTAN QUANT OS
Grid Candidate Pipeline Tests
Version : 1.0.0
==========================================
"""

from copy import deepcopy

from engine.grid_candidate_pipeline import (
    GridCandidatePipeline,
    run_grid_candidate_pipeline,
)


# ==========================================================
# TEST HELPERS
# ==========================================================


class DummyQualityAnalyzer:
    def analyze(self, candidate):
        return {
            "quality_score": 80,
        }


class DummyQualityRunAnalyzer:
    def run(self, candidate):
        return {
            "crypto_quality_score": 75,
        }


class DummyMarketAnalyzer:
    def analyze(self, candidate):
        return {
            "market_regime": "RANGE",
            "volatility": 0.02,
        }


class DummyMarketRunAnalyzer:
    def run(self, candidate):
        return {
            "regime": "SIDEWAYS",
            "normalized_volatility": 0.03,
        }


class DummyGridResearch:
    def analyze(self, candidate):
        return {
            "profitability_score": 85,
            "recovery_score": 90,
            "drawdown": 12,
        }


class DummyGridResearchRun:
    def run(self, candidate):
        return {
            "grid_score": 70,
            "recovery_probability": 80,
            "max_drawdown": 15,
        }


class DummyRanker:
    def rank(self, candidates):
        ranked = deepcopy(candidates)

        for index, candidate in enumerate(ranked, start=1):
            candidate["rank"] = index

        return ranked


class ReverseRanker:
    def rank(self, candidates):
        return list(
            reversed(
                deepcopy(candidates)
            )
        )


class FailingQualityAnalyzer:
    def analyze(self, candidate):
        raise RuntimeError("quality failure")


class FailingMarketAnalyzer:
    def analyze(self, candidate):
        raise RuntimeError("market failure")


class FailingResearchEngine:
    def analyze(self, candidate):
        raise RuntimeError("research failure")


# ==========================================================
# BASIC CONTRACT TESTS
# ==========================================================


def test_pipeline_creation():

    pipeline = GridCandidatePipeline()

    assert pipeline is not None
    assert pipeline.quality_analyzer is None
    assert pipeline.market_analyzer is None
    assert pipeline.grid_research_engine is None
    assert pipeline.ranker is not None


def test_required_result_keys():

    pipeline = GridCandidatePipeline()

    result = pipeline.run([])

    required_keys = {
        "status",
        "candidates",
        "processed_count",
        "failed_count",
        "ranked_count",
        "errors",
        "input",
    }

    assert set(result.keys()) == required_keys


def test_empty_result_contract_is_stable():

    pipeline = GridCandidatePipeline()

    result = pipeline._build_empty_result()

    assert result == {
        "status": "EMPTY",
        "candidates": [],
        "processed_count": 0,
        "failed_count": 0,
        "ranked_count": 0,
        "errors": [],
        "input": None,
    }


# ==========================================================
# EMPTY INPUT TESTS
# ==========================================================


def test_none_candidates_returns_empty():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(None)

    assert result["status"] == "EMPTY"
    assert result["candidates"] == []
    assert result["processed_count"] == 0
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 0
    assert "candidates is None" in result["errors"]


def test_empty_candidates_returns_empty():

    pipeline = GridCandidatePipeline()

    result = pipeline.run([])

    assert result["status"] == "EMPTY"
    assert result["candidates"] == []
    assert result["processed_count"] == 0
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 0
    assert result["errors"] == []


def test_invalid_candidate_container_returns_error():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        {
            "symbol": "BTCUSDT"
        }
    )

    assert result["status"] == "ERROR"
    assert result["candidates"] == []
    assert result["processed_count"] == 0
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 0

    assert "candidates must be a list" in result["errors"]


def test_string_candidates_returns_error():

    pipeline = GridCandidatePipeline()

    result = pipeline.run("BTCUSDT")

    assert result["status"] == "ERROR"
    assert "candidates must be a list" in result["errors"]


# ==========================================================
# BASIC PROCESSING TESTS
# ==========================================================


def test_valid_candidate_is_processed():

    pipeline = GridCandidatePipeline(
        ranker=DummyRanker()
    )

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    result = pipeline.run(candidates)

    assert result["status"] == "SUCCESS"
    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 1

    assert result["candidates"][0]["symbol"] == "BTCUSDT"
    assert result["candidates"][0]["rank"] == 1


def test_symbol_is_stripped():

    pipeline = GridCandidatePipeline(
        ranker=DummyRanker()
    )

    result = pipeline.run(
        [
            {
                "symbol": "  BTCUSDT  ",
            }
        ]
    )

    assert result["status"] == "SUCCESS"

    assert (
        result["candidates"][0]["symbol"]
        == "BTCUSDT"
    )


def test_multiple_candidates_are_processed():

    pipeline = GridCandidatePipeline(
        ranker=DummyRanker()
    )

    candidates = [
        {
            "symbol": "BTCUSDT",
        },
        {
            "symbol": "ETHUSDT",
        },
        {
            "symbol": "SOLUSDT",
        },
    ]

    result = pipeline.run(candidates)

    assert result["status"] == "SUCCESS"
    assert result["processed_count"] == 3
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 3

    assert (
        result["candidates"][0]["symbol"]
        == "BTCUSDT"
    )

    assert (
        result["candidates"][1]["symbol"]
        == "ETHUSDT"
    )

    assert (
        result["candidates"][2]["symbol"]
        == "SOLUSDT"
    )


# ==========================================================
# INVALID CANDIDATE TESTS
# ==========================================================


def test_non_dict_candidate_is_failed():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            "BTCUSDT",
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1
    assert result["ranked_count"] == 0


def test_candidate_without_symbol_is_failed():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "price": 100,
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_symbol_must_be_string():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "symbol": 123,
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_empty_symbol_is_failed():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "symbol": "",
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_whitespace_symbol_is_failed():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "symbol": "   ",
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_mixed_valid_and_invalid_candidates_are_partial():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            },
            {
                "symbol": "",
            },
            "ETHUSDT",
        ]
    )

    assert result["status"] == "PARTIAL"
    assert result["processed_count"] == 1
    assert result["failed_count"] == 2
    assert result["ranked_count"] == 1


# ==========================================================
# QUALITY ANALYZER TESTS
# ==========================================================


def test_quality_analyzer_analyze_method():

    pipeline = GridCandidatePipeline(
        quality_analyzer=DummyQualityAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["quality"] == {
        "quality_score": 80,
    }

    assert candidate["quality_score"] == 80


def test_quality_analyzer_run_method():

    pipeline = GridCandidatePipeline(
        quality_analyzer=DummyQualityRunAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["quality"] == {
        "crypto_quality_score": 75,
    }

    assert candidate["quality_score"] == 75


def test_quality_analyzer_callable():

    def analyzer(candidate):
        return {
            "score": 60,
        }

    pipeline = GridCandidatePipeline(
        quality_analyzer=analyzer
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["quality"]["score"] == 60
    assert candidate["quality_score"] == 60


def test_quality_score_priority():

    pipeline = GridCandidatePipeline(
        quality_analyzer=lambda candidate: {
            "quality_score": 90,
            "crypto_quality_score": 80,
            "score": 70,
        }
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert (
        result["candidates"][0]["quality_score"]
        == 90
    )


def test_invalid_quality_result_is_safe():

    pipeline = GridCandidatePipeline(
        quality_analyzer=lambda candidate: "invalid"
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert "quality" not in candidate
    assert "quality_score" not in candidate


# ==========================================================
# MARKET ANALYZER TESTS
# ==========================================================


def test_market_analyzer_analyze_method():

    pipeline = GridCandidatePipeline(
        market_analyzer=DummyMarketAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["market"] == {
        "market_regime": "RANGE",
        "volatility": 0.02,
    }

    assert candidate["market_regime"] == "RANGE"
    assert candidate["volatility"] == 0.02


def test_market_analyzer_run_method():

    pipeline = GridCandidatePipeline(
        market_analyzer=DummyMarketRunAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["market_regime"] == "SIDEWAYS"

    assert (
        candidate["volatility"]
        == 0.03
    )


def test_market_analyzer_callable():

    def analyzer(candidate):
        return {
            "regime": "NEUTRAL",
            "normalized_volatility": 0.04,
        }

    pipeline = GridCandidatePipeline(
        market_analyzer=analyzer
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["market_regime"] == "NEUTRAL"

    assert (
        candidate["volatility"]
        == 0.04
    )


def test_market_result_priority():

    pipeline = GridCandidatePipeline(
        market_analyzer=lambda candidate: {
            "market_regime": "RANGE",
            "regime": "TREND",
            "volatility": 0.02,
            "normalized_volatility": 0.10,
        }
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["market_regime"] == "RANGE"
    assert candidate["volatility"] == 0.02


def test_invalid_market_result_is_safe():

    pipeline = GridCandidatePipeline(
        market_analyzer=lambda candidate: [
            "invalid"
        ]
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert "market" not in candidate
    assert "market_regime" not in candidate
    assert "volatility" not in candidate


# ==========================================================
# GRID RESEARCH TESTS
# ==========================================================


def test_grid_research_analyze_method():

    pipeline = GridCandidatePipeline(
        grid_research_engine=DummyGridResearch()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert candidate["grid_research"] == {
        "profitability_score": 85,
        "recovery_score": 90,
        "drawdown": 12,
    }

    assert (
        candidate["profitability_score"]
        == 85
    )

    assert candidate["recovery_score"] == 90
    assert candidate["drawdown"] == 12


def test_grid_research_run_method():

    pipeline = GridCandidatePipeline(
        grid_research_engine=DummyGridResearchRun()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert (
        candidate["profitability_score"]
        == 70
    )

    assert candidate["recovery_score"] == 80
    assert candidate["drawdown"] == 15


def test_grid_research_callable():

    def research(candidate):
        return {
            "score": 95,
            "conditional_recovery": 88,
            "max_drawdown": 10,
        }

    pipeline = GridCandidatePipeline(
        grid_research_engine=research
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert (
        candidate["profitability_score"]
        == 95
    )

    assert candidate["recovery_score"] == 88
    assert candidate["drawdown"] == 10


def test_research_result_priority():

    pipeline = GridCandidatePipeline(
        grid_research_engine=lambda candidate: {
            "profitability_score": 90,
            "grid_score": 80,
            "score": 70,
            "recovery_score": 85,
            "recovery_probability": 75,
            "conditional_recovery": 65,
            "drawdown": 10,
            "max_drawdown": 20,
        }
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert (
        candidate["profitability_score"]
        == 90
    )

    assert candidate["recovery_score"] == 85
    assert candidate["drawdown"] == 10


def test_invalid_research_result_is_safe():

    pipeline = GridCandidatePipeline(
        grid_research_engine=lambda candidate: 100
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    candidate = result["candidates"][0]

    assert "grid_research" not in candidate
    assert "profitability_score" not in candidate
    assert "recovery_score" not in candidate
    assert "drawdown" not in candidate


# ==========================================================
# FULL PIPELINE TEST
# ==========================================================


def test_full_pipeline():

    pipeline = GridCandidatePipeline(
        quality_analyzer=DummyQualityAnalyzer(),
        market_analyzer=DummyMarketAnalyzer(),
        grid_research_engine=DummyGridResearch(),
        ranker=DummyRanker(),
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "SUCCESS"

    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 1

    candidate = result["candidates"][0]

    assert candidate["symbol"] == "BTCUSDT"

    assert candidate["quality_score"] == 80

    assert (
        candidate["market_regime"]
        == "RANGE"
    )

    assert candidate["volatility"] == 0.02

    assert (
        candidate["profitability_score"]
        == 85
    )

    assert candidate["recovery_score"] == 90
    assert candidate["drawdown"] == 12

    assert candidate["rank"] == 1


# ==========================================================
# RANKER TESTS
# ==========================================================


def test_ranker_is_called():

    pipeline = GridCandidatePipeline(
        ranker=ReverseRanker()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            },
            {
                "symbol": "ETHUSDT",
            },
        ]
    )

    assert (
        result["candidates"][0]["symbol"]
        == "ETHUSDT"
    )

    assert (
        result["candidates"][1]["symbol"]
        == "BTCUSDT"
    )


def test_callable_ranker_is_supported():

    def ranker(candidates):
        result = deepcopy(candidates)

        for candidate in result:
            candidate["ranked"] = True

        return result

    pipeline = GridCandidatePipeline(
        ranker=ranker
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert (
        result["candidates"][0]["ranked"]
        is True
    )


def test_invalid_ranker_result_falls_back_to_candidates():

    class InvalidRanker:
        def rank(self, candidates):
            return {
                "invalid": True
            }

    pipeline = GridCandidatePipeline(
        ranker=InvalidRanker()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "SUCCESS"

    assert (
        result["candidates"][0]["symbol"]
        == "BTCUSDT"
    )


def test_none_ranker_uses_default_ranker():

    pipeline = GridCandidatePipeline(
        ranker=None
    )

    assert pipeline.ranker is not None


# ==========================================================
# EXCEPTION SAFETY TESTS
# ==========================================================


def test_quality_exception_fails_candidate():

    pipeline = GridCandidatePipeline(
        quality_analyzer=FailingQualityAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_market_exception_fails_candidate():

    pipeline = GridCandidatePipeline(
        market_analyzer=FailingMarketAnalyzer()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_research_exception_fails_candidate():

    pipeline = GridCandidatePipeline(
        grid_research_engine=FailingResearchEngine()
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            }
        ]
    )

    assert result["status"] == "EMPTY"
    assert result["processed_count"] == 0
    assert result["failed_count"] == 1


def test_partial_failure_is_reported():

    def analyzer(candidate):

        if candidate["symbol"] == "ETHUSDT":
            raise RuntimeError("failure")

        return {
            "quality_score": 80,
        }

    pipeline = GridCandidatePipeline(
        quality_analyzer=analyzer
    )

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
            },
            {
                "symbol": "ETHUSDT",
            },
        ]
    )

    assert result["status"] == "PARTIAL"

    assert result["processed_count"] == 1
    assert result["failed_count"] == 1
    assert result["ranked_count"] == 1

    assert (
        result["candidates"][0]["symbol"]
        == "BTCUSDT"
    )


# ==========================================================
# INPUT IMMUTABILITY TESTS
# ==========================================================


def test_input_is_not_modified():

    candidates = [
        {
            "symbol": " BTCUSDT ",
            "metadata": {
                "source": "test",
            },
        }
    ]

    original = deepcopy(candidates)

    pipeline = GridCandidatePipeline(
        quality_analyzer=DummyQualityAnalyzer(),
        market_analyzer=DummyMarketAnalyzer(),
        grid_research_engine=DummyGridResearch(),
    )

    pipeline.run(candidates)

    assert candidates == original


def test_result_input_preserves_original_candidates():

    candidates = [
        {
            "symbol": " BTCUSDT ",
        }
    ]

    pipeline = GridCandidatePipeline()

    result = pipeline.run(candidates)

    assert result["input"] == candidates

    assert (
        result["input"][0]["symbol"]
        == " BTCUSDT "
    )


def test_result_is_independent():

    pipeline = GridCandidatePipeline()

    result = pipeline.run(
        [
            {
                "symbol": "BTCUSDT",
                "metadata": {
                    "source": "test",
                },
            }
        ]
    )

    result["candidates"][0]["symbol"] = "CHANGED"

    assert (
        result["input"][0]["symbol"]
        == "BTCUSDT"
    )


def test_candidate_result_is_independent_from_input():

    candidates = [
        {
            "symbol": "BTCUSDT",
            "metadata": {
                "source": "test",
            },
        }
    ]

    pipeline = GridCandidatePipeline()

    result = pipeline.run(candidates)

    result["candidates"][0]["metadata"]["source"] = (
        "changed"
    )

    assert (
        candidates[0]["metadata"]["source"]
        == "test"
    )


# ==========================================================
# ALIAS TESTS
# ==========================================================


def test_process_alias():

    pipeline = GridCandidatePipeline()

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    result = pipeline.process(candidates)

    assert result["status"] == "SUCCESS"
    assert result["processed_count"] == 1


def test_execute_alias():

    pipeline = GridCandidatePipeline()

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    result = pipeline.execute(candidates)

    assert result["status"] == "SUCCESS"
    assert result["processed_count"] == 1


def test_process_alias_matches_run():

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    pipeline = GridCandidatePipeline()

    run_result = pipeline.run(candidates)

    process_result = pipeline.process(
        candidates
    )

    assert run_result == process_result


def test_execute_alias_matches_run():

    candidates = [
        {
            "symbol": "BTCUSDT",
        }
    ]

    pipeline = GridCandidatePipeline()

    run_result = pipeline.run(candidates)

    execute_result = pipeline.execute(
        candidates
    )

    assert run_result == execute_result


# ==========================================================
# CONVENIENCE FUNCTION TEST
# ==========================================================


def test_run_grid_candidate_pipeline_function():

    result = run_grid_candidate_pipeline(
        [
            {
                "symbol": "BTCUSDT",
            }
        ],
        quality_analyzer=DummyQualityAnalyzer(),
        market_analyzer=DummyMarketAnalyzer(),
        grid_research_engine=DummyGridResearch(),
        ranker=DummyRanker(),
    )

    assert result["status"] == "SUCCESS"

    assert result["processed_count"] == 1
    assert result["failed_count"] == 0
    assert result["ranked_count"] == 1

    candidate = result["candidates"][0]

    assert candidate["quality_score"] == 80
    assert candidate["market_regime"] == "RANGE"

    assert (
        candidate["profitability_score"]
        == 85
    )

    assert candidate["rank"] == 1