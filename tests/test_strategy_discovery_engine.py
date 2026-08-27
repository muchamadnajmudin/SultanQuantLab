from engine.strategy_discovery_engine import (
    discover_strategies,
    discover_strategy,
    StrategyDiscoveryEngine,
    DISCOVERY_STATUS_NO_GAP,
    DISCOVERY_STATUS_DISCOVERED,
    DISCOVERY_STATUS_NO_CANDIDATE,
)

from engine.strategy_gap_engine import (
    evaluate_strategy_gap,
)


def _gap_result(
    gap_detected=True,
    qualified=None,
    weak=None,
    market_context=None,
):
    return {
        "gap_detected": gap_detected,
        "qualified_strategies": (
            qualified
            if qualified is not None
            else []
        ),
        "weak_strategies": (
            weak
            if weak is not None
            else []
        ),
        "market_context": (
            market_context
            if market_context is not None
            else {}
        ),
    }


def test_required_result_keys():

    result = discover_strategies(
        {}
    )

    assert set(
        result.keys()
    ) == {
        "status",
        "gap_detected",
        "market_context",
        "candidates",
        "qualified_candidates",
        "rejected_candidates",
    }


def test_returns_dictionary():

    result = discover_strategies(
        {}
    )

    assert isinstance(
        result,
        dict,
    )


def test_no_gap_returns_no_gap_status():

    result = discover_strategies(

        _gap_result(
            gap_detected=False
        )

    )

    assert result[
        "status"
    ] == DISCOVERY_STATUS_NO_GAP

    assert result[
        "candidates"
    ] == []


def test_none_gap_result_is_safe():

    result = discover_strategies(
        None
    )

    assert result[
        "status"
    ] == DISCOVERY_STATUS_NO_GAP

    assert result[
        "gap_detected"
    ] is False


def test_non_dict_gap_result_is_safe():

    result = discover_strategies(
        "invalid"
    )

    assert result[
        "status"
    ] == DISCOVERY_STATUS_NO_GAP


def test_gap_creates_candidate():

    result = discover_strategies(

        _gap_result(

            gap_detected=True,

            market_context={
                "regime": "TREND",
                "confidence": 0.90,
            },

        )

    )

    assert len(
        result[
            "candidates"
        ]
    ) == 1


def test_trend_market_creates_trend_following_candidate():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "STRONG_TREND",
                "confidence": 0.90,
            },

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "TREND_FOLLOWING"


def test_range_market_creates_mean_reversion_candidate():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "RANGE",
                "confidence": 0.90,
            },

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "MEAN_REVERSION"


def test_volatile_market_creates_breakout_candidate():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "VOLATILE",
                "confidence": 0.90,
            },

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "BREAKOUT"


def test_high_trend_strength_infers_trend():

    result = discover_strategies(

        _gap_result(

            market_context={
                "trend_strength": 0.90,
            }

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "TREND_FOLLOWING"


def test_high_volatility_infers_breakout():

    result = discover_strategies(

        _gap_result(

            market_context={
                "volatility": 0.90,
            }

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "BREAKOUT"


def test_unknown_market_creates_hybrid_candidate():

    result = discover_strategies(

        _gap_result(
            market_context={}
        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "HYBRID"


def test_high_confidence_candidate_is_qualified():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "TREND",
                "confidence": 0.90,
            },

        )

    )

    assert result[
        "status"
    ] == DISCOVERY_STATUS_DISCOVERED

    assert len(

        result[
            "qualified_candidates"
        ]

    ) == 1


def test_low_confidence_candidate_can_be_rejected():

    result = discover_strategies(

        _gap_result(

            weak=[
                {"name": "A"},
                {"name": "B"},
                {"name": "C"},
                {"name": "D"},
                {"name": "E"},
            ],

            market_context={
                "confidence": 0.0,
            },

        )

    )

    assert result[
        "status"
    ] == DISCOVERY_STATUS_NO_CANDIDATE

    assert len(

        result[
            "rejected_candidates"
        ]

    ) == 1


def test_candidate_contains_required_keys():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "TREND",
                "confidence": 0.80,
            },

        )

    )

    candidate = result[
        "candidates"
    ][0]

    assert set(
        candidate.keys()
    ) == {
        "name",
        "method_type",
        "market_context",
        "source",
        "discovery_score",
        "status",
    }


def test_market_context_argument_is_merged():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "RANGE",
            }

        ),

        {
            "confidence": 0.90,
        },

    )

    context = result[
        "market_context"
    ]

    assert context[
        "regime"
    ] == "RANGE"

    assert context[
        "confidence"
    ] == 0.90


def test_market_context_argument_overrides_gap_context():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "RANGE",
                "confidence": 0.20,
            }

        ),

        {
            "regime": "TREND",
            "confidence": 0.90,
        },

    )

    candidate = result[
        "candidates"
    ][0]

    assert candidate[
        "method_type"
    ] == "TREND_FOLLOWING"


def test_input_is_not_modified():

    gap = _gap_result(

        market_context={
            "regime": "TREND",
            "confidence": 0.90,
        }

    )

    original_context = gap[
        "market_context"
    ].copy()

    discover_strategies(
        gap
    )

    assert gap[
        "market_context"
    ] == original_context


def test_result_is_independent():

    result = discover_strategies(

        _gap_result(

            market_context={
                "regime": "TREND",
                "confidence": 0.90,
            }

        )

    )

    result[
        "market_context"
    ][
        "regime"
    ] = "CHANGED"


    fresh = discover_strategies(

        _gap_result(

            market_context={
                "regime": "TREND",
                "confidence": 0.90,
            }

        )

    )

    assert fresh[
        "market_context"
    ][
        "regime"
    ] == "TREND"


def test_function_alias():

    gap = _gap_result(

        market_context={
            "confidence": 0.90,
        }

    )

    assert discover_strategy(
        gap
    ) == discover_strategies(
        gap
    )


def test_engine_wrapper_discover():

    engine = StrategyDiscoveryEngine()

    result = engine.discover(

        _gap_result(

            market_context={
                "confidence": 0.90,
            }

        )

    )

    assert isinstance(
        result,
        dict,
    )


def test_engine_wrapper_run():

    engine = StrategyDiscoveryEngine()

    result = engine.run(

        _gap_result(

            market_context={
                "confidence": 0.90,
            }

        )

    )

    assert isinstance(
        result,
        dict,
    )


# ==================================================
# STRATEGY GAP ENGINE INTEGRATION
# ==================================================

def test_accepts_strategy_gap_engine_contract():

    gap_result = evaluate_strategy_gap(

        [
            {
                "name": "strategy_a",
                "score": 0.20,
                "confidence": 0.20,
            },
        ],

        market_context={
            "regime": "TREND",
            "confidence": 0.90,
        },

        minimum_score=0.60,

        minimum_confidence=0.60,

    )


    assert gap_result[
        "discovery_required"
    ] is True


    result = discover_strategies(
        gap_result
    )


    assert result[
        "gap_detected"
    ] is True


    assert result[
        "status"
    ] == DISCOVERY_STATUS_DISCOVERED


    assert len(

        result[
            "candidates"
        ]

    ) == 1


    candidate = result[
        "candidates"
    ][0]


    assert candidate[
        "method_type"
    ] == "TREND_FOLLOWING"


def test_strategy_gap_covered_does_not_trigger_discovery():

    gap_result = evaluate_strategy_gap(

        [
            {
                "name": "strategy_a",
                "score": 0.90,
                "confidence": 0.90,
            },
        ],

        market_context={
            "regime": "TREND",
            "confidence": 0.90,
        },

        minimum_score=0.60,

        minimum_confidence=0.60,

    )


    assert gap_result[
        "discovery_required"
    ] is False


    result = discover_strategies(
        gap_result
    )


    assert result[
        "status"
    ] == DISCOVERY_STATUS_NO_GAP


    assert result[
        "gap_detected"
    ] is False


    assert result[
        "candidates"
    ] == []