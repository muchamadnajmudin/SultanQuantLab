from copy import deepcopy

import engine.portfolio_lifecycle_engine as lifecycle


def build_valid_portfolio():

    return {
        "portfolio": [
            {
                "strategy": "xau_strategy",
                "status": "SUCCESS",
            }
        ],
        "allocation": [
            {
                "strategy": "xau_strategy",
                "weight": 1.0,
            }
        ],
        "exposure": {
            "total": 1.0,
        },
        "risk": {
            "risk_score": 80,
            "approved": True,
        },
        "decision": {
            "approved": True,
        },
        "best_strategy": "xau_strategy",
    }


def test_required_lifecycle_keys():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert lifecycle.REQUIRED_LIFECYCLE_KEYS.issubset(
        result.keys()
    )


def test_lifecycle_returns_dictionary():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


def test_lifecycle_contract_is_stable():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert set(
        result.keys()
    ) == lifecycle.REQUIRED_LIFECYCLE_KEYS


def test_valid_portfolio_is_approved():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["approved"] is True
    assert result["blocked"] is False


def test_valid_portfolio_reaches_approved_state():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["status"] == lifecycle.STATUS_APPROVED


def test_validation_failure_blocks_portfolio():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert result["blocked"] is True


def test_validation_failure_is_not_approved():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert result["approved"] is False


def test_invalid_input_is_safe():

    result = lifecycle.run_portfolio_lifecycle(
        None
    )

    assert isinstance(
        result,
        dict,
    )

    assert result["blocked"] is True


def test_list_input_is_safe():

    result = lifecycle.run_portfolio_lifecycle(
        []
    )

    assert isinstance(
        result,
        dict,
    )


def test_string_input_is_safe():

    result = lifecycle.run_portfolio_lifecycle(
        "invalid"
    )

    assert isinstance(
        result,
        dict,
    )


def test_input_portfolio_is_not_modified():

    portfolio = build_valid_portfolio()

    original = deepcopy(
        portfolio
    )

    lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert portfolio == original


def test_result_portfolio_is_independent():

    portfolio = build_valid_portfolio()

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    result["portfolio"]["new_key"] = True

    assert "new_key" not in portfolio


def test_validation_result_is_preserved():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result["validation"],
        dict,
    )


def test_governance_result_is_preserved():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result["governance"],
        dict,
    )


def test_state_result_is_preserved():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result["state"],
        dict,
    )


def test_state_contains_history():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert "history" in result["state"]


def test_blocked_lifecycle_has_blocked_status():

    portfolio = build_valid_portfolio()

    portfolio["allocation"] = []

    result = lifecycle.run_portfolio_lifecycle(
        portfolio
    )

    assert result["status"] == lifecycle.STATUS_BLOCKED


def test_warnings_are_list():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result["warnings"],
        list,
    )


def test_reasons_are_list():

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert isinstance(
        result["reasons"],
        list,
    )


def test_duplicate_reasons_are_removed(monkeypatch):

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        lambda portfolio: {
            "valid": False,
            "reasons": [
                "duplicate",
                "duplicate",
            ],
            "warnings": [],
        },
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["reasons"].count(
        "duplicate"
    ) == 1


def test_execute_lifecycle_alias():

    portfolio = build_valid_portfolio()

    result = lifecycle.execute_portfolio_lifecycle(
        portfolio
    )

    assert isinstance(
        result,
        dict,
    )


def test_process_lifecycle_alias():

    portfolio = build_valid_portfolio()

    result = lifecycle.process_portfolio_lifecycle(
        portfolio
    )

    assert isinstance(
        result,
        dict,
    )


def test_engine_wrapper_run():

    engine = lifecycle.PortfolioLifecycleEngine()

    result = engine.run(
        build_valid_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


def test_engine_wrapper_execute():

    engine = lifecycle.PortfolioLifecycleEngine()

    result = engine.execute(
        build_valid_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


def test_engine_wrapper_process():

    engine = lifecycle.PortfolioLifecycleEngine()

    result = engine.process(
        build_valid_portfolio()
    )

    assert isinstance(
        result,
        dict,
    )


def test_validation_engine_exception_blocks(monkeypatch):

    def raise_error(portfolio):

        raise RuntimeError(
            "validation failure"
        )

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        raise_error,
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["blocked"] is True
    assert result["approved"] is False


def test_governance_engine_exception_blocks(monkeypatch):

    def raise_error(portfolio):

        raise RuntimeError(
            "governance failure"
        )

    monkeypatch.setattr(
        lifecycle,
        "govern_portfolio",
        raise_error,
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["blocked"] is True


def test_warning_governance_moves_to_warning(monkeypatch):

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        lambda portfolio: {
            "valid": True,
            "warnings": [],
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        lifecycle,
        "govern_portfolio",
        lambda portfolio: {
            "approved": True,
            "blocked": False,
            "warnings": [
                "risk warning"
            ],
            "reasons": [],
        },
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["status"] == lifecycle.STATUS_WARNING


def test_warning_portfolio_remains_approved(monkeypatch):

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        lambda portfolio: {
            "valid": True,
            "warnings": [],
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        lifecycle,
        "govern_portfolio",
        lambda portfolio: {
            "approved": True,
            "blocked": False,
            "warnings": [
                "warning"
            ],
            "reasons": [],
        },
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["approved"] is True
    assert result["blocked"] is False


def test_governance_block_moves_to_blocked(monkeypatch):

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        lambda portfolio: {
            "valid": True,
            "warnings": [],
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        lifecycle,
        "govern_portfolio",
        lambda portfolio: {
            "approved": False,
            "blocked": True,
            "warnings": [],
            "reasons": [
                "governance blocked",
            ],
        },
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["status"] == lifecycle.STATUS_BLOCKED


def test_unknown_governance_result_blocks(monkeypatch):

    monkeypatch.setattr(
        lifecycle,
        "validate_portfolio",
        lambda portfolio: {
            "valid": True,
            "warnings": [],
            "reasons": [],
        },
    )

    monkeypatch.setattr(
        lifecycle,
        "govern_portfolio",
        lambda portfolio: {},
    )

    result = lifecycle.run_portfolio_lifecycle(
        build_valid_portfolio()
    )

    assert result["blocked"] is True


def test_lifecycle_status_constants():

    assert lifecycle.STATUS_NEW == "NEW"
    assert lifecycle.STATUS_VALIDATING == "VALIDATING"
    assert lifecycle.STATUS_VALIDATED == "VALIDATED"
    assert lifecycle.STATUS_RISK_CHECK == "RISK_CHECK"
    assert lifecycle.STATUS_DECISION_CHECK == "DECISION_CHECK"
    assert lifecycle.STATUS_APPROVED == "APPROVED"
    assert lifecycle.STATUS_ACTIVE == "ACTIVE"
    assert lifecycle.STATUS_WARNING == "WARNING"
    assert lifecycle.STATUS_BLOCKED == "BLOCKED"