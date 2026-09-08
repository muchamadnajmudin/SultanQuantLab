"""
SULTAN QUANT OS
Institutional End-to-End Governance / Lifecycle Integration Tests

Purpose:
    FINAL DECISION -> PORTFOLIO LIFECYCLE -> APPROVED/WARNING/BLOCKED

Grid is intentionally not referenced or modified.
"""

from copy import deepcopy

import pandas as pd

import engine.institutional_engine as institutional


def _portfolio_result():
    return {
        "regime": "TRENDING",
        "portfolio": [
            {
                "name": "xau_strategy",
                "evaluation_status": "SUCCESS",
                "statistics": {
                    "profit_factor": 2.5,
                    "total_trades": 100,
                },
                "score": 90.0,
                "rank": 1,
            }
        ],
        "best": {
            "name": "xau_strategy",
            "evaluation_status": "SUCCESS",
            "score": 90.0,
        },
        "allocation": [
            {"strategy": "xau_strategy", "weight": 1.0}
        ],
        "risk": {
            "status": "LOW",
            "risk_score": 20.0,
        },
        "decision": {
            "decision": "PRELIMINARY",
            "live_ready": False,
        },
        "exposure": {"total": 1.0},
        "summary": {"strategy_count": 1},
    }


def _patch_pipeline(monkeypatch, final_decision):
    df = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [1000, 1100, 1200],
        }
    )

    trades = [{"profit": 100.0, "return": 0.10}]

    statistics = {
        "profit_factor": 2.5,
        "total_trades": 100,
        "net_profit": 1000.0,
        "max_drawdown": 5.0,
    }

    wfo_analysis = {
        "stability_score": 90.0,
        "wfo_robustness_score": 95.0,
        "overfitting_risk": "LOW",
    }

    mc_analysis = {
        "risk_level": "LOW",
        "robustness_score": 95.0,
    }

    risk_dashboard = {
        "status": "LOW",
        "risk_score": 20.0,
    }

    monkeypatch.setattr(
        institutional,
        "load_data",
        lambda data_file: df.copy(deep=True),
    )
    monkeypatch.setattr(
        institutional,
        "calculate_indicators",
        lambda value: value.copy(deep=True),
    )
    monkeypatch.setattr(
        institutional,
        "_run_portfolio_from_dataframe",
        lambda value, top_n=3: deepcopy(_portfolio_result()),
    )
    monkeypatch.setattr(
        institutional,
        "run_strategy",
        lambda value, strategy=None: value.copy(deep=True),
    )
    monkeypatch.setattr(
        institutional,
        "run_backtest",
        lambda value: deepcopy(trades),
    )
    monkeypatch.setattr(
        institutional,
        "calculate_statistics",
        lambda value: deepcopy(statistics),
    )
    monkeypatch.setattr(
        institutional,
        "run_monte_carlo_pipeline",
        lambda value: {
            "simulation": {"runs": 1000},
            "analysis": deepcopy(mc_analysis),
        },
    )
    monkeypatch.setattr(
        institutional,
        "run_wfo_pipeline",
        lambda data_file: {
            "results": [],
            "analysis": deepcopy(wfo_analysis),
        },
    )
    monkeypatch.setattr(
        institutional,
        "run_risk_pipeline",
        lambda statistics, monte_carlo=None, wfo=None:
            deepcopy(risk_dashboard),
    )
    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, results: deepcopy(final_decision),
    )
    monkeypatch.setattr(
        institutional,
        "generate_reports",
        lambda *args, **kwargs: {"report": "ok"},
    )
    monkeypatch.setattr(
        institutional,
        "generate_visual_reports",
        lambda value: {"equity": "ok"},
    )
    monkeypatch.setattr(
        institutional,
        "run_institutional_report",
        lambda *args, **kwargs: {"institutional": "ok"},
    )


def test_final_decision_flows_into_lifecycle(monkeypatch):
    """
    Lifecycle must receive the portfolio containing the FINAL decision,
    not the preliminary Portfolio Engine decision.
    """
    final_decision = {
        "decision": "APPROVED",
        "live_ready": True,
        "failed_gates": [],
    }

    captured = {}

    def lifecycle_spy(portfolio):
        captured["portfolio"] = deepcopy(portfolio)

        assert portfolio["decision"] == final_decision

        return {
            "status": "APPROVED",
            "approved": True,
            "blocked": False,
            "warnings": [],
            "reasons": [],
            "state": {"state": "APPROVED"},
            "governance": {
                "approved": True,
                "blocked": False,
                "warnings": [],
                "reasons": [],
            },
        }

    _patch_pipeline(monkeypatch, final_decision)

    # raising=False deliberately makes this a contract test:
    # before production wiring exists, the test fails by missing output
    # rather than failing during monkeypatch setup.
    monkeypatch.setattr(
        institutional,
        "run_portfolio_lifecycle",
        lifecycle_spy,
        raising=False,
    )

    result = institutional.execute_pipeline("dummy.csv")

    assert "lifecycle" in result
    assert captured["portfolio"]["decision"] == final_decision
    assert result["lifecycle"]["status"] == "APPROVED"
    assert result["lifecycle"]["approved"] is True


def test_blocked_decision_blocks_lifecycle(monkeypatch):
    """
    A rejected final institutional decision must not become an approved
    lifecycle state.
    """
    final_decision = {
        "decision": "REJECTED",
        "live_ready": False,
        "failed_gates": ["WFO robustness below threshold"],
    }

    captured = {}

    def lifecycle_spy(portfolio):
        captured["portfolio"] = deepcopy(portfolio)

        assert portfolio["decision"] == final_decision

        return {
            "status": "BLOCKED",
            "approved": False,
            "blocked": True,
            "warnings": [],
            "reasons": ["Final institutional decision rejected"],
            "state": {"state": "BLOCKED"},
            "governance": {
                "approved": False,
                "blocked": True,
                "warnings": [],
                "reasons": ["Final institutional decision rejected"],
            },
        }

    _patch_pipeline(monkeypatch, final_decision)

    monkeypatch.setattr(
        institutional,
        "run_portfolio_lifecycle",
        lifecycle_spy,
        raising=False,
    )

    result = institutional.execute_pipeline("dummy.csv")

    assert "lifecycle" in result
    assert captured["portfolio"]["decision"] == final_decision
    assert result["lifecycle"]["status"] == "BLOCKED"
    assert result["lifecycle"]["approved"] is False
    assert result["lifecycle"]["blocked"] is True


def test_lifecycle_preserves_existing_pipeline_outputs(monkeypatch):
    """
    Lifecycle integration must extend, not remove, the existing public
    execute_pipeline() output contract.
    """
    final_decision = {
        "decision": "APPROVED",
        "live_ready": True,
        "failed_gates": [],
    }

    lifecycle_result = {
        "status": "APPROVED",
        "approved": True,
        "blocked": False,
        "warnings": [],
        "reasons": [],
        "state": {"state": "APPROVED"},
        "governance": {
            "approved": True,
            "blocked": False,
            "warnings": [],
            "reasons": [],
        },
    }

    _patch_pipeline(monkeypatch, final_decision)

    monkeypatch.setattr(
        institutional,
        "run_portfolio_lifecycle",
        lambda portfolio: deepcopy(lifecycle_result),
        raising=False,
    )

    result = institutional.execute_pipeline("dummy.csv")

    required_keys = {
        "portfolio",
        "portfolio_result",
        "best",
        "decision",
        "strategy_name",
        "data",
        "trades",
        "statistics",
        "reports",
        "visual_reports",
        "monte_carlo",
        "wfo",
        "risk_dashboard",
        "institutional_report",
    }

    assert required_keys.issubset(result.keys())
    assert "lifecycle" in result
    assert result["decision"] == final_decision
    assert result["portfolio_result"]["decision"] == final_decision
    assert result["lifecycle"] == lifecycle_result
    assert result["strategy_name"] == "xau_strategy"
