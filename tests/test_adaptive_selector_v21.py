from strategies.intelligence.adaptive_selector import (
    select_best_strategy,
    rank_strategies,
    calculate_selection_confidence,
    select_strategy_details,
    get_top_strategies,
    has_qualified_strategy,
)


def test_select_best_strategy_backward_compatible():

    weights = {
        "price_action": 0.40,
        "breakout": 0.60,
    }

    assert (
        select_best_strategy(weights)
        == "breakout"
    )


def test_candidate_restriction():

    weights = {
        "price_action": 0.40,
        "breakout": 0.60,
        "fibonacci": 0.80,
    }

    result = select_best_strategy(
        weights,
        candidates=[
            "price_action",
            "breakout",
        ],
    )

    assert result == "breakout"


def test_minimum_weight():

    weights = {
        "price_action": 0.10,
        "breakout": 0.40,
    }

    result = select_best_strategy(
        weights,
        minimum_weight=0.30,
    )

    assert result == "breakout"


def test_minimum_weight_no_candidate():

    weights = {
        "price_action": 0.10,
        "breakout": 0.20,
    }

    result = select_best_strategy(
        weights,
        minimum_weight=0.50,
    )

    assert result is None


def test_fallback():

    weights = {
        "price_action": 0.10,
        "breakout": 0.20,
    }

    result = select_best_strategy(
        weights,
        minimum_weight=0.50,
        fallback="price_action",
    )

    assert result == "price_action"


def test_rank_strategies():

    weights = {
        "price_action": 0.40,
        "breakout": 0.60,
        "fibonacci": 0.20,
    }

    ranked = rank_strategies(
        weights
    )

    assert ranked[0]["strategy"] == "breakout"
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    assert ranked[2]["rank"] == 3


def test_selection_confidence():

    weights = {
        "price_action": 0.80,
        "breakout": 0.20,
    }

    confidence = calculate_selection_confidence(
        weights
    )

    assert confidence == 0.80


def test_selection_details():

    weights = {
        "price_action": 0.70,
        "breakout": 0.30,
    }

    details = select_strategy_details(
        weights
    )

    assert details["strategy"] == "price_action"
    assert details["weight"] == 0.70
    assert details["rank"] == 1
    assert details["confidence"] == 0.70
    assert details["candidate_count"] == 2
    assert details["fallback_used"] is False


def test_top_strategies():

    weights = {
        "price_action": 0.20,
        "breakout": 0.50,
        "fibonacci": 0.30,
    }

    top = get_top_strategies(
        weights,
        top_n=2,
    )

    assert len(top) == 2
    assert top[0]["strategy"] == "breakout"
    assert top[1]["strategy"] == "fibonacci"


def test_has_qualified_strategy():

    weights = {
        "price_action": 0.20,
        "breakout": 0.50,
    }

    assert has_qualified_strategy(
        weights,
        minimum_weight=0.40,
    )

    assert not has_qualified_strategy(
        weights,
        minimum_weight=0.60,
    )


def test_invalid_weights():

    assert (
        select_best_strategy(
            None
        )
        is None
    )

    assert (
        rank_strategies(
            None
        )
        == []
    )