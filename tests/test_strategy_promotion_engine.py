"""
==========================================
SULTAN QUANT OS
Strategy Promotion Engine Tests
Version : 1.0.0
==========================================
"""

from copy import deepcopy

from engine.strategy_promotion_engine import (
    STATUS_HOLD,
    STATUS_PROMOTED,
    STATUS_REJECTED,
    REQUIRED_RESULT_KEYS,
    StrategyPromotionEngine,
    process_strategy_promotion,
    promote_strategy_candidate,
    required_result_keys,
)


def _qualified_validation():
    return {
        "status": "QUALIFIED",
        "qualified": True,
        "promotion_allowed": True,
        "candidate": {
            "strategy": "trend_following",
            "score": 85.0,
            "confidence": 0.90,
        },
        "reasons": [
            "candidate_qualified",
        ],
        "evaluation": {
            "score": 85.0,
            "confidence": 0.90,
        },
    }


def _insufficient_validation():
    return {
        "status": "INSUFFICIENT_DATA",
        "qualified": False,
        "promotion_allowed": False,
        "candidate": {
            "strategy": "trend_following",
        },
        "reasons": [
            "missing_score",
        ],
        "evaluation": {},
    }


def _rejected_validation():
    return {
        "status": "REJECTED",
        "qualified": False,
        "promotion_allowed": False,
        "candidate": {
            "strategy": "trend_following",
        },
        "reasons": [
            "score_below_threshold",
        ],
        "evaluation": {
            "score": 10.0,
        },
    }


def test_required_result_keys():

    assert required_result_keys() == (
        REQUIRED_RESULT_KEYS
    )


def test_returns_dictionary():

    result = promote_strategy_candidate(
        _qualified_validation()
    )

    assert isinstance(
        result,
        dict,
    )


def test_contract_is_stable():

    result = promote_strategy_candidate(
        _qualified_validation()
    )

    assert set(
        result.keys()
    ) == set(
        REQUIRED_RESULT_KEYS
    )


def test_qualified_candidate_is_promoted():

    result = promote_strategy_candidate(
        _qualified_validation()
    )

    assert (
        result["status"]
        == STATUS_PROMOTED
    )

    assert result["promoted"] is True

    assert (
        result["promotion_allowed"]
        is True
    )

    assert (
        "candidate_promoted"
        in result["reasons"]
    )


def test_insufficient_data_candidate_is_held():

    result = promote_strategy_candidate(
        _insufficient_validation()
    )

    assert (
        result["status"]
        == STATUS_HOLD
    )

    assert result["promoted"] is False

    assert (
        result["promotion_allowed"]
        is False
    )

    assert (
        "promotion_on_hold"
        in result["reasons"]
    )


def test_hold_preserves_validation_reasons():

    result = promote_strategy_candidate(
        _insufficient_validation()
    )

    assert (
        "missing_score"
        in result["reasons"]
    )


def test_rejected_candidate_remains_rejected():

    result = promote_strategy_candidate(
        _rejected_validation()
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert result["promoted"] is False

    assert (
        result["promotion_allowed"]
        is False
    )

    assert (
        "candidate_rejected"
        in result["reasons"]
    )


def test_rejected_preserves_validation_reasons():

    result = promote_strategy_candidate(
        _rejected_validation()
    )

    assert (
        "score_below_threshold"
        in result["reasons"]
    )


def test_none_validation_is_safe():

    result = promote_strategy_candidate(
        None
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert result["promoted"] is False

    assert (
        result["promotion_allowed"]
        is False
    )

    assert (
        "invalid_validation_result"
        in result["reasons"]
    )


def test_non_dict_validation_is_safe():

    result = promote_strategy_candidate(
        "invalid"
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "invalid_validation_result"
        in result["reasons"]
    )


def test_empty_validation_is_rejected():

    result = promote_strategy_candidate(
        {}
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "invalid_validation_result"
        in result["reasons"]
    )


def test_unknown_validation_status_is_rejected():

    validation = _qualified_validation()

    validation["status"] = "UNKNOWN"

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "unknown_validation_status"
        in result["reasons"]
    )


def test_missing_validation_status_is_rejected():

    validation = _qualified_validation()

    validation.pop(
        "status"
    )

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "unknown_validation_status"
        in result["reasons"]
    )


def test_lowercase_qualified_status_is_supported():

    validation = _qualified_validation()

    validation["status"] = "qualified"

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["status"]
        == STATUS_PROMOTED
    )


def test_whitespace_status_is_supported():

    validation = _qualified_validation()

    validation["status"] = "  QUALIFIED  "

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["status"]
        == STATUS_PROMOTED
    )


def test_candidate_is_resolved_from_validation():

    validation = _qualified_validation()

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["candidate"]
        == validation["candidate"]
    )


def test_explicit_candidate_overrides_validation_candidate():

    validation = _qualified_validation()

    explicit_candidate = {
        "strategy": "breakout",
        "score": 90.0,
    }

    result = promote_strategy_candidate(
        validation,
        candidate=explicit_candidate,
    )

    assert (
        result["candidate"]
        == explicit_candidate
    )

    assert (
        result["candidate"]["strategy"]
        == "breakout"
    )


def test_invalid_explicit_candidate_falls_back_to_validation_candidate():

    validation = _qualified_validation()

    result = promote_strategy_candidate(
        validation,
        candidate="invalid",
    )

    assert (
        result["candidate"]
        == validation["candidate"]
    )


def test_missing_candidate_is_safe():

    validation = _qualified_validation()

    validation.pop(
        "candidate"
    )

    result = promote_strategy_candidate(
        validation
    )

    assert (
        result["candidate"]
        == {}
    )


def test_input_validation_is_not_modified():

    validation = _qualified_validation()

    original = deepcopy(
        validation
    )

    promote_strategy_candidate(
        validation
    )

    assert validation == original


def test_explicit_candidate_is_not_modified():

    validation = _qualified_validation()

    candidate = {
        "strategy": "breakout",
        "nested": {
            "score": 90.0,
        },
    }

    original = deepcopy(
        candidate
    )

    promote_strategy_candidate(
        validation,
        candidate=candidate,
    )

    assert candidate == original


def test_result_candidate_is_independent():

    validation = _qualified_validation()

    result = promote_strategy_candidate(
        validation
    )

    result["candidate"]["strategy"] = (
        "modified"
    )

    assert (
        validation["candidate"]["strategy"]
        == "trend_following"
    )


def test_result_validation_is_independent():

    validation = _qualified_validation()

    result = promote_strategy_candidate(
        validation
    )

    result["validation"]["candidate"][
        "strategy"
    ] = "modified"

    assert (
        validation["candidate"]["strategy"]
        == "trend_following"
    )


def test_result_reasons_are_independent():

    validation = _insufficient_validation()

    result = promote_strategy_candidate(
        validation
    )

    result["reasons"].append(
        "modified"
    )

    assert (
        "modified"
        not in validation["reasons"]
    )


def test_qualified_result_has_promoted_flags():

    result = promote_strategy_candidate(
        _qualified_validation()
    )

    assert result["promoted"] is True

    assert (
        result["promotion_allowed"]
        is True
    )


def test_hold_result_has_disabled_flags():

    result = promote_strategy_candidate(
        _insufficient_validation()
    )

    assert result["promoted"] is False

    assert (
        result["promotion_allowed"]
        is False
    )


def test_rejected_result_has_disabled_flags():

    result = promote_strategy_candidate(
        _rejected_validation()
    )

    assert result["promoted"] is False

    assert (
        result["promotion_allowed"]
        is False
    )


def test_function_alias():

    validation = _qualified_validation()

    result = process_strategy_promotion(
        validation
    )

    assert (
        result["status"]
        == STATUS_PROMOTED
    )


def test_function_alias_matches_main_function():

    validation = _qualified_validation()

    expected = promote_strategy_candidate(
        validation
    )

    actual = process_strategy_promotion(
        validation
    )

    assert actual == expected


def test_engine_wrapper_promote():

    engine = StrategyPromotionEngine()

    result = engine.promote(
        _qualified_validation()
    )

    assert (
        result["status"]
        == STATUS_PROMOTED
    )


def test_engine_wrapper_run():

    engine = StrategyPromotionEngine()

    result = engine.run(
        _insufficient_validation()
    )

    assert (
        result["status"]
        == STATUS_HOLD
    )


def test_engine_wrapper_rejected():

    engine = StrategyPromotionEngine()

    result = engine.run(
        _rejected_validation()
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )


def test_status_constants():

    assert (
        STATUS_PROMOTED
        == "PROMOTED"
    )

    assert (
        STATUS_HOLD
        == "HOLD"
    )

    assert (
        STATUS_REJECTED
        == "REJECTED"
    )