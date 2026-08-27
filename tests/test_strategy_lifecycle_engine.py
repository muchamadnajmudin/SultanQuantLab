"""
==========================================
SULTAN QUANT OS
Strategy Lifecycle Engine Tests
Version : 1.1.0
==========================================
"""

from copy import deepcopy

import engine.strategy_lifecycle_engine as lifecycle


def _valid_candidate():

    return {
        "name": "valid_candidate",
        "score": 0.90,
        "confidence": 0.90,
        "sample_count": 100,
    }


def _low_score_candidate():

    return {
        "name": "low_score_candidate",
        "score": 0.10,
        "confidence": 0.90,
        "sample_count": 100,
    }


def _insufficient_sample_candidate():

    return {
        "name": "insufficient_sample_candidate",
        "score": 0.90,
        "confidence": 0.90,
        "sample_count": 1,
    }


def test_required_result_keys():

    keys = lifecycle.required_result_keys()

    assert isinstance(keys, tuple)

    assert "status" in keys
    assert "candidate" in keys
    assert "validation" in keys
    assert "promotion" in keys
    assert "reasons" in keys
    assert "state_history" in keys


def test_lifecycle_returns_dictionary():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    assert isinstance(result, dict)


def test_lifecycle_contract_is_stable():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    for key in lifecycle.required_result_keys():

        assert key in result


def test_valid_candidate_is_promoted():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_valid_candidate_passes_validation():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["validation"]["status"]
        == "QUALIFIED"
    )


def test_valid_candidate_state_history():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["state_history"]
        == [
            lifecycle.STATUS_DISCOVERED,
            lifecycle.STATUS_VALIDATING,
            lifecycle.STATUS_QUALIFIED,
            lifecycle.STATUS_PROMOTED,
        ]
    )


def test_low_score_candidate_is_rejected():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_low_score_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_REJECTED
    )


def test_rejected_candidate_preserves_validation():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_low_score_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["validation"]["status"]
        == "REJECTED"
    )


def test_rejected_candidate_state_history():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_low_score_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["state_history"]
        == [
            lifecycle.STATUS_DISCOVERED,
            lifecycle.STATUS_VALIDATING,
            lifecycle.STATUS_REJECTED,
        ]
    )


def test_insufficient_samples_goes_to_hold():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_insufficient_sample_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_HOLD
    )


def test_hold_state_history():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_insufficient_sample_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["state_history"]
        == [
            lifecycle.STATUS_DISCOVERED,
            lifecycle.STATUS_VALIDATING,
            lifecycle.STATUS_HOLD,
        ]
    )


def test_invalid_candidate_is_rejected():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=None,
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_REJECTED
    )


def test_non_dict_candidate_is_safe():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate="invalid",
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert isinstance(
        result["candidate"],
        dict,
    )

    assert (
        result["status"]
        == lifecycle.STATUS_REJECTED
    )


def test_empty_candidate_is_rejected():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate={},
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_REJECTED
    )


def test_low_confidence_candidate_is_rejected():

    candidate = _valid_candidate()

    candidate["confidence"] = 0.10

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate,
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_REJECTED
    )


def test_evaluation_is_forwarded_to_validation():

    candidate = {
        "name": "evaluation_candidate",
        "score": 0.10,
        "confidence": 0.10,
        "sample_count": 1,
    }

    evaluation = {
        "score": 0.90,
        "confidence": 0.90,
        "sample_count": 100,
    }

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate,
            evaluation=evaluation,
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_candidate_is_preserved():

    candidate = _valid_candidate()

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate
        )
    )

    assert (
        result["candidate"]
        == candidate
    )


def test_input_candidate_is_not_modified():

    candidate = _valid_candidate()

    original = deepcopy(candidate)

    lifecycle.process_strategy_lifecycle(
        candidate=candidate
    )

    assert candidate == original


def test_result_candidate_is_independent():

    candidate = _valid_candidate()

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate
        )
    )

    result["candidate"]["score"] = 999

    assert (
        candidate["score"]
        != 999
    )


def test_result_validation_is_independent():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    validation = result["validation"]

    validation["modified"] = True

    result_again = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    assert (
        "modified"
        not in result_again["validation"]
    )


def test_result_promotion_is_independent():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    promotion = result["promotion"]

    assert isinstance(
        promotion,
        dict,
    )

    promotion["modified"] = True

    result_again = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    assert (
        "modified"
        not in result_again["promotion"]
    )


def test_reasons_are_list():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    assert isinstance(
        result["reasons"],
        list,
    )


def test_state_history_is_list():

    result = (
        lifecycle.process_strategy_lifecycle(
            candidate=_valid_candidate()
        )
    )

    assert isinstance(
        result["state_history"],
        list,
    )


def test_function_alias_run():

    result = (
        lifecycle.run_strategy_lifecycle(
            candidate=_valid_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_function_alias_execute():

    result = (
        lifecycle.execute_strategy_lifecycle(
            candidate=_valid_candidate(),
            min_score=0.50,
            min_confidence=0.50,
            min_samples=10,
        )
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_run_alias_matches_main_function():

    candidate = _valid_candidate()

    main_result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate
        )
    )

    run_result = (
        lifecycle.run_strategy_lifecycle(
            candidate=candidate
        )
    )

    assert (
        run_result
        == main_result
    )


def test_execute_alias_matches_main_function():

    candidate = _valid_candidate()

    main_result = (
        lifecycle.process_strategy_lifecycle(
            candidate=candidate
        )
    )

    execute_result = (
        lifecycle.execute_strategy_lifecycle(
            candidate=candidate
        )
    )

    assert (
        execute_result
        == main_result
    )


def test_engine_wrapper_run():

    engine = (
        lifecycle.StrategyLifecycleEngine()
    )

    result = engine.run(
        candidate=_valid_candidate(),
        min_score=0.50,
        min_confidence=0.50,
        min_samples=10,
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_engine_wrapper_process():

    engine = (
        lifecycle.StrategyLifecycleEngine()
    )

    result = engine.process(
        candidate=_valid_candidate(),
        min_score=0.50,
        min_confidence=0.50,
        min_samples=10,
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_engine_wrapper_execute():

    engine = (
        lifecycle.StrategyLifecycleEngine()
    )

    result = engine.execute(
        candidate=_valid_candidate(),
        min_score=0.50,
        min_confidence=0.50,
        min_samples=10,
    )

    assert (
        result["status"]
        == lifecycle.STATUS_PROMOTED
    )


def test_status_constants():

    assert (
        lifecycle.STATUS_DISCOVERED
        == "DISCOVERED"
    )

    assert (
        lifecycle.STATUS_VALIDATING
        == "VALIDATING"
    )

    assert (
        lifecycle.STATUS_QUALIFIED
        == "QUALIFIED"
    )

    assert (
        lifecycle.STATUS_PROMOTED
        == "PROMOTED"
    )

    assert (
        lifecycle.STATUS_HOLD
        == "HOLD"
    )

    assert (
        lifecycle.STATUS_REJECTED
        == "REJECTED"
    )