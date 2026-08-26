"""
==========================================
SULTAN QUANT OS
Strategy Gap Engine Tests
Version : 1.0.0
==========================================
"""

from copy import deepcopy

from engine.strategy_gap_engine import (
    REQUIRED_RESULT_KEYS,
    STATUS_COVERED,
    STATUS_GAP,
    STATUS_INSUFFICIENT_DATA,
    STATUS_WEAK,
    StrategyGapEngine,
    analyze_strategy_gap,
    evaluate_strategy_gap,
    required_result_keys,
)


def sample_strategies():
    return [
        {
            "strategy": "trend_following",
            "score": 80,
            "confidence": 0.9,
        },
        {
            "strategy": "price_action",
            "score": 60,
            "confidence": 0.7,
        },
    ]


def test_required_result_keys():
    assert required_result_keys() == REQUIRED_RESULT_KEYS


def test_returns_dictionary():
    result = evaluate_strategy_gap([])
    assert isinstance(result, dict)


def test_contract_is_stable():
    result = evaluate_strategy_gap([])
    assert set(result.keys()) == set(
        REQUIRED_RESULT_KEYS
    )


def test_empty_strategies_require_discovery():
    result = evaluate_strategy_gap([])

    assert result["status"] == STATUS_INSUFFICIENT_DATA
    assert result["discovery_required"] is True


def test_none_strategies_is_safe():
    result = evaluate_strategy_gap(None)

    assert result["status"] == STATUS_INSUFFICIENT_DATA


def test_non_list_strategies_is_safe():
    result = evaluate_strategy_gap("invalid")

    assert result["status"] == STATUS_INSUFFICIENT_DATA


def test_qualified_strategies_cover_market():
    result = evaluate_strategy_gap(
        sample_strategies(),
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert result["status"] == STATUS_COVERED
    assert result["discovery_required"] is False


def test_all_weak_strategies_create_gap():
    strategies = [
        {
            "strategy": "trend_following",
            "score": 20,
            "confidence": 0.2,
        },
        {
            "strategy": "price_action",
            "score": 30,
            "confidence": 0.3,
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert result["status"] == STATUS_GAP
    assert result["discovery_required"] is True


def test_partial_coverage_is_weak():
    strategies = [
        {
            "strategy": "trend_following",
            "score": 90,
            "confidence": 0.9,
        },
        {
            "strategy": "price_action",
            "score": 10,
            "confidence": 0.1,
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert result["status"] == STATUS_WEAK
    assert result["discovery_required"] is False


def test_qualified_strategies_are_separated():
    result = evaluate_strategy_gap(
        sample_strategies(),
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert len(result["qualified_strategies"]) == 2
    assert result["weak_strategies"] == []


def test_weak_strategies_are_separated():
    strategies = [
        {
            "strategy": "weak_strategy",
            "score": 10,
            "confidence": 0.1,
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert len(result["weak_strategies"]) == 1


def test_missing_score_is_weak():
    strategies = [
        {
            "strategy": "unknown_strategy",
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
    )

    assert result["status"] == STATUS_GAP

    assert result["weak_strategies"][0]["reasons"] == [
        "missing_score"
    ]


def test_confidence_is_optional():
    strategies = [
        {
            "strategy": "trend_following",
            "score": 80,
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
        minimum_confidence=0.9,
    )

    assert result["status"] == STATUS_COVERED


def test_adaptive_score_is_supported():
    strategies = [
        {
            "strategy": "adaptive",
            "adaptive_score": 80,
            "selection_confidence": 0.9,
        },
    ]

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
        minimum_confidence=0.5,
    )

    assert result["status"] == STATUS_COVERED


def test_market_context_is_preserved():
    context = {
        "regime": "TRENDING",
    }

    result = evaluate_strategy_gap(
        sample_strategies(),
        market_context=context,
    )

    assert result["market_context"] == context


def test_market_context_is_independent():
    context = {
        "regime": "TRENDING",
    }

    result = evaluate_strategy_gap(
        sample_strategies(),
        market_context=context,
    )

    result["market_context"]["regime"] = "RANGE"

    assert context["regime"] == "TRENDING"


def test_input_is_not_modified():
    strategies = sample_strategies()
    original = deepcopy(strategies)

    evaluate_strategy_gap(
        strategies,
        minimum_score=50,
    )

    assert strategies == original


def test_result_is_independent():
    strategies = sample_strategies()

    result = evaluate_strategy_gap(
        strategies,
        minimum_score=50,
    )

    result["qualified_strategies"][0]["strategy"] = "changed"

    assert (
        strategies[0]["strategy"]
        == "trend_following"
    )


def test_function_alias():
    result = analyze_strategy_gap(
        sample_strategies(),
        minimum_score=50,
    )

    assert result["status"] == STATUS_COVERED


def test_engine_wrapper_evaluate():
    engine = StrategyGapEngine(
        minimum_score=50,
        minimum_confidence=0.5,
    )

    result = engine.evaluate(
        sample_strategies()
    )

    assert result["status"] == STATUS_COVERED


def test_engine_wrapper_run():
    engine = StrategyGapEngine(
        minimum_score=50,
    )

    result = engine.run(
        sample_strategies()
    )

    assert result["status"] == STATUS_COVERED