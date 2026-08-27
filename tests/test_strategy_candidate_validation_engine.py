from engine.strategy_candidate_validation_engine import (
    STATUS_QUALIFIED,
    STATUS_REJECTED,
    STATUS_INSUFFICIENT_DATA,
    StrategyCandidateValidationEngine,
    analyze_strategy_candidate,
    required_result_keys,
    validate_strategy_candidate,
)


def test_required_result_keys():

    keys = required_result_keys()

    assert isinstance(
        keys,
        tuple,
    )

    assert "status" in keys
    assert "qualified" in keys
    assert "promotion_allowed" in keys
    assert "candidate" in keys
    assert "reasons" in keys
    assert "evaluation" in keys


def test_returns_dictionary():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.8,
        }
    )

    assert isinstance(
        result,
        dict,
    )


def test_contract_is_stable():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.8,
        }
    )

    assert set(
        result.keys()
    ) == set(
        required_result_keys()
    )


def test_valid_candidate_is_qualified():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.8,
            "confidence": 0.9,
        },
        minimum_score=0.5,
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )

    assert result["qualified"] is True

    assert (
        result["promotion_allowed"]
        is True
    )


def test_low_score_is_rejected():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.2,
        },
        minimum_score=0.5,
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert result["qualified"] is False

    assert (
        result["promotion_allowed"]
        is False
    )

    assert (
        "score_below_threshold"
        in result["reasons"]
    )


def test_low_confidence_is_rejected():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
            "confidence": 0.2,
        },
        minimum_score=0.5,
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "confidence_below_threshold"
        in result["reasons"]
    )


def test_missing_score_is_insufficient_data():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
        }
    )

    assert (
        result["status"]
        == STATUS_INSUFFICIENT_DATA
    )

    assert result["qualified"] is False

    assert (
        "missing_score"
        in result["reasons"]
    )


def test_confidence_is_optional_when_threshold_zero():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        },
        minimum_confidence=0.0,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_missing_confidence_is_insufficient_when_required():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        },
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_INSUFFICIENT_DATA
    )

    assert (
        "missing_confidence"
        in result["reasons"]
    )


def test_invalid_candidate_is_rejected():

    result = validate_strategy_candidate(
        None
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "invalid_candidate"
        in result["reasons"]
    )


def test_non_dict_candidate_is_safe():

    result = validate_strategy_candidate(
        [
            "trend_following"
        ]
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )


def test_missing_candidate_name_is_rejected():

    result = validate_strategy_candidate(
        {
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "missing_candidate_name"
        in result["reasons"]
    )


def test_name_field_is_supported():

    result = validate_strategy_candidate(
        {
            "name": "trend_following",
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_candidate_field_is_supported():

    result = validate_strategy_candidate(
        {
            "candidate": "trend_following",
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_adaptive_score_is_supported():

    result = validate_strategy_candidate(
        {
            "strategy": "adaptive",
            "adaptive_score": 0.9,
        },
        minimum_score=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_setup_score_is_supported():

    result = validate_strategy_candidate(
        {
            "strategy": "price_action",
            "setup_score": 0.9,
        },
        minimum_score=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_selection_confidence_is_supported():

    result = validate_strategy_candidate(
        {
            "strategy": "adaptive",
            "score": 0.9,
            "selection_confidence": 0.9,
        },
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_evaluation_overrides_candidate_score():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.2,
        },
        evaluation={
            "score": 0.9,
        },
        minimum_score=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_evaluation_overrides_candidate_confidence():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
            "confidence": 0.2,
        },
        evaluation={
            "confidence": 0.9,
        },
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_candidate_embedded_evaluation_is_supported():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "evaluation": {
                "score": 0.9,
                "confidence": 0.9,
            },
        },
        minimum_score=0.5,
        minimum_confidence=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_explicit_evaluation_overrides_embedded_evaluation():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "evaluation": {
                "score": 0.2,
            },
        },
        evaluation={
            "score": 0.9,
        },
        minimum_score=0.5,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_minimum_samples_requires_sample_data():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        },
        minimum_samples=10,
    )

    assert (
        result["status"]
        == STATUS_INSUFFICIENT_DATA
    )

    assert (
        "missing_sample_count"
        in result["reasons"]
    )


def test_insufficient_samples_is_rejected():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
            "trade_count": 5,
        },
        minimum_samples=10,
    )

    assert (
        result["status"]
        == STATUS_REJECTED
    )

    assert (
        "insufficient_sample_count"
        in result["reasons"]
    )


def test_sufficient_samples_is_qualified():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
            "trade_count": 20,
        },
        minimum_samples=10,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_sample_count_from_evaluation_is_supported():

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        },
        evaluation={
            "trade_count": 20,
        },
        minimum_samples=10,
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_input_is_not_modified():

    candidate = {
        "strategy": "trend_following",
        "score": 0.9,
        "evaluation": {
            "confidence": 0.9,
        },
    }

    original = {
        "strategy": "trend_following",
        "score": 0.9,
        "evaluation": {
            "confidence": 0.9,
        },
    }

    validate_strategy_candidate(
        candidate
    )

    assert candidate == original


def test_result_candidate_is_independent():

    candidate = {
        "strategy": "trend_following",
        "score": 0.9,
    }

    result = validate_strategy_candidate(
        candidate
    )

    result["candidate"]["score"] = 0.1

    assert candidate["score"] == 0.9


def test_result_evaluation_is_independent():

    evaluation = {
        "score": 0.9,
    }

    result = validate_strategy_candidate(
        {
            "strategy": "trend_following",
        },
        evaluation=evaluation,
    )

    result["evaluation"]["score"] = 0.1

    assert evaluation["score"] == 0.9


def test_function_alias():

    result = analyze_strategy_candidate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_engine_wrapper_validate():

    engine = (
        StrategyCandidateValidationEngine(
            minimum_score=0.5
        )
    )

    result = engine.validate(
        {
            "strategy": "trend_following",
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_engine_wrapper_run():

    engine = (
        StrategyCandidateValidationEngine(
            minimum_score=0.5
        )
    )

    result = engine.run(
        {
            "strategy": "trend_following",
            "score": 0.9,
        }
    )

    assert (
        result["status"]
        == STATUS_QUALIFIED
    )


def test_status_constants():

    assert STATUS_QUALIFIED == "QUALIFIED"
    assert STATUS_REJECTED == "REJECTED"

    assert (
        STATUS_INSUFFICIENT_DATA
        == "INSUFFICIENT_DATA"
    )