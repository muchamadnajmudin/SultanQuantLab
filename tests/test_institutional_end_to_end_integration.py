from copy import deepcopy

import pandas as pd

import engine.institutional_engine as institutional


def _sample_df():
    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.5, 101.5, 102.5],
            "volume": [10.0, 11.0, 12.0],
        }
    )


def _strategy_result():
    return {
        "name": "xau_strategy",
        "evaluation_status": "SUCCESS",
        "score": 95.0,
        "statistics": {
            "profit_factor": 2.5,
            "max_drawdown_percent": 10.0,
            "total_trades": 20,
        },
    }


def _portfolio_result():
    strategy = _strategy_result()
    return {
        "regime": "TRENDING",
        "portfolio": [deepcopy(strategy)],
        "best": deepcopy(strategy),
        "allocation": [
            {
                "name": "xau_strategy",
                "allocation": 1.0,
            }
        ],
        "risk": {"status": "LOW"},
        "decision": {
            "decision": "PRELIMINARY",
            "live_ready": False,
        },
        "exposure": 1.0,
        "summary": {},
    }


def _patch_pipeline(monkeypatch, decision_spy):
    df = _sample_df()
    trades = [{"pnl": 10.0}]
    statistics = {
        "profit_factor": 2.5,
        "max_drawdown_percent": 10.0,
        "total_trades": 20,
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
        lambda statistics, monte_carlo=None, wfo=None: deepcopy(risk_dashboard),
    )
    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        decision_spy,
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

    return {
        "statistics": statistics,
        "wfo": wfo_analysis,
        "monte_carlo": mc_analysis,
        "risk": risk_dashboard,
    }


def test_final_decision_receives_complete_institutional_evidence(monkeypatch):
    captured = {}

    def decision_spy(risk, results):
        captured["risk"] = deepcopy(risk)
        captured["results"] = deepcopy(results)
        return {
            "decision": "APPROVED",
            "live_ready": True,
            "failed_gates": [],
        }

    expected = _patch_pipeline(
        monkeypatch,
        decision_spy,
    )

    institutional.execute_pipeline("dummy.csv")

    assert captured["risk"]["status"] == "LOW"
    assert captured["risk"]["wfo"] == expected["wfo"]
    assert captured["risk"]["monte_carlo"] == expected["monte_carlo"]
    assert captured["risk"]["statistics"] == expected["statistics"]
    assert captured["results"][0]["name"] == "xau_strategy"


def test_final_decision_replaces_preliminary_portfolio_decision(monkeypatch):
    final_decision = {
        "decision": "APPROVED",
        "live_ready": True,
        "failed_gates": [],
    }

    _patch_pipeline(
        monkeypatch,
        lambda risk, results: deepcopy(final_decision),
    )

    result = institutional.execute_pipeline("dummy.csv")

    assert result["decision"] == final_decision
    assert result["portfolio_result"]["decision"] == final_decision
    assert result["portfolio_result"]["decision"]["decision"] != "PRELIMINARY"


def test_complete_pipeline_preserves_existing_public_outputs(monkeypatch):
    final_decision = {
        "decision": "NEEDS OPTIMIZATION",
        "live_ready": False,
        "failed_gates": ["WFO robustness below threshold"],
    }

    _patch_pipeline(
        monkeypatch,
        lambda risk, results: deepcopy(final_decision),
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
    assert result["strategy_name"] == "xau_strategy"
    assert result["decision"] == final_decision
