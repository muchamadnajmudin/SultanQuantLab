"""
==================================================
SULTAN QUANT OS
Institutional Portfolio Engine Contract Tests
==================================================

Purpose:

- Validate institutional portfolio contract
- Validate result normalization
- Validate SUCCESS / FAILED / INSUFFICIENT_DATA
- Validate allocation
- Validate risk
- Validate exposure
- Validate decision
- Validate backward compatibility

These tests intentionally mock lower-level engines so
that Institutional Portfolio Engine can be tested as
an isolated orchestration layer.
==================================================
"""

import pandas as pd
import pytest

import engine.institutional_portfolio_engine as institutional


# ==================================================
# TEST DATA
# ==================================================

def _sample_dataframe():
    """
    Minimal market dataframe.
    """

    return pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0],
            "close": [101.0, 102.0, 103.0],
            "volume": [1000, 1100, 1200],
        }
    )


# ==================================================
# SAMPLE STRATEGY RESULTS
# ==================================================

def _successful_result(
    name="strategy_a",
):
    return {
        "name": name,
        "market_regime": "TRENDING",
        "statistics": {
            "total_trade": 10,
            "profit_factor": 2.0,
            "win_rate": 60.0,
        },
        "trades": [1, 2, 3],
        "score": 80.0,
        "rank": 1,
        "grade": "A",
        "weight": 0.5,
        "router_recommended": True,
    }


def _failed_result(
    name="strategy_failed",
):
    return {
        "name": name,
        "error": "strategy execution failed",
    }


def _empty_result(
    name="strategy_empty",
):
    return {
        "name": name,
        "statistics": {
            "total_trade": 0,
        },
        "trades": [],
    }


# ==================================================
# NORMALIZATION
# ==================================================

def test_normalize_success_result():

    results = [
        _successful_result()
    ]

    normalized = (
        institutional._normalize_portfolio_results(
            results
        )
    )

    assert len(normalized) == 1

    result = normalized[0]

    assert result[
        "evaluation_status"
    ] == "SUCCESS"

    assert result[
        "market_regime"
    ] == "TRENDING"

    assert result[
        "rank"
    ] == 1

    assert result[
        "score"
    ] == 80.0

    assert result[
        "grade"
    ] == "A"

    assert result[
        "weight"
    ] == 0.5

    assert result[
        "router_recommended"
    ] is True


def test_normalize_failed_result():

    results = [
        _failed_result()
    ]

    normalized = (
        institutional._normalize_portfolio_results(
            results
        )
    )

    assert len(normalized) == 1

    assert normalized[0][
        "evaluation_status"
    ] == "FAILED"


def test_normalize_insufficient_data_result():

    results = [
        _empty_result()
    ]

    normalized = (
        institutional._normalize_portfolio_results(
            results
        )
    )

    assert len(normalized) == 1

    assert normalized[0][
        "evaluation_status"
    ] == "INSUFFICIENT_DATA"


def test_normalize_missing_metadata():

    result = {
        "name": "legacy_strategy",
        "statistics": {
            "total_trade": 5,
        },
    }

    normalized = (
        institutional._normalize_portfolio_results(
            [result]
        )
    )

    item = normalized[0]

    assert item[
        "evaluation_status"
    ] == "SUCCESS"

    assert item[
        "rank"
    ] == 0

    assert item[
        "score"
    ] == 0.0

    assert item[
        "grade"
    ] == "N/A"

    assert item[
        "market_regime"
    ] == "UNKNOWN"

    assert item[
        "weight"
    ] == 0.0

    assert item[
        "router_recommended"
    ] is False


def test_normalize_ignores_invalid_items():

    results = [
        None,
        "invalid",
        123,
        _successful_result(),
    ]

    normalized = (
        institutional._normalize_portfolio_results(
            results
        )
    )

    assert len(normalized) == 1

    assert normalized[0][
        "name"
    ] == "strategy_a"


# ==================================================
# MARKET REGIME
# ==================================================

def test_detect_regime():

    results = [
        {
            "name": "strategy_a",
            "market_regime": "TRENDING",
        }
    ]

    regime = institutional._detect_regime(
        results
    )

    assert regime == "TRENDING"


def test_detect_regime_unknown():

    regime = institutional._detect_regime(
        []
    )

    assert regime == "UNKNOWN"


# ==================================================
# ALLOCATION NORMALIZATION
# ==================================================

def test_normalize_allocation_list():

    allocation = [
        {
            "name": "strategy_a",
            "allocation": 0.6,
        },
        {
            "name": "strategy_b",
            "allocation": 0.4,
        },
    ]

    normalized = (
        institutional._normalize_allocation(
            allocation
        )
    )

    assert isinstance(
        normalized,
        list,
    )

    assert len(
        normalized
    ) == 2

    assert (
        normalized[0][
            "allocation"
        ]
        == 0.6
    )


def test_normalize_allocation_dict():

    allocation = {
        "strategy_a": 0.7,
        "strategy_b": 0.3,
    }

    normalized = (
        institutional._normalize_allocation(
            allocation
        )
    )

    assert isinstance(
        normalized,
        list,
    )

    assert len(
        normalized
    ) == 2

    total = sum(
        item["allocation"]
        for item in normalized
    )

    assert total == pytest.approx(
        1.0
    )


def test_allocation_exposure():

    allocation = [
        {
            "name": "strategy_a",
            "allocation": 0.6,
        },
        {
            "name": "strategy_b",
            "allocation": 0.4,
        },
    ]

    exposure = (
        institutional._calculate_exposure(
            allocation
        )
    )

    assert exposure == pytest.approx(
        1.0
    )


# ==================================================
# EMPTY / SAFE CONTRACT
# ==================================================

def test_empty_dataframe_contract():

    result = (
        institutional.build_institutional_portfolio(
            None
        )
    )

    assert isinstance(
        result,
        dict,
    )

    assert result[
        "regime"
    ] == "UNKNOWN"

    assert result[
        "portfolio"
    ] == []

    assert result[
        "best"
    ] is None

    assert result[
        "allocation"
    ] == []

    assert result[
        "risk"
    ] == {}

    assert result[
        "decision"
    ] == {}

    assert result[
        "exposure"
    ] == 0.0

    assert result[
        "summary"
    ] == {}


# ==================================================
# FULL INSTITUTIONAL CONTRACT
# ==================================================

def test_institutional_portfolio_full_contract(
    monkeypatch,
):

    results = [
        _successful_result()
    ]

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: results,
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda values: values[0],
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda values, top_n=3: [
            {
                "name": "strategy_a",
                "allocation": 1.0,
            }
        ],
    )

    monkeypatch.setattr(
        institutional,
        "calculate_portfolio_risk",
        lambda allocation: {
            "risk_score": 20.0,
            "risk_level": "LOW",
        },
    )

    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, values: {
            "status": "READY FOR FORWARD TEST",
        },
    )

    monkeypatch.setattr(
        institutional,
        "portfolio_summary",
        lambda values: {
            "strategies": 1,
        },
    )

    result = (
        institutional.build_institutional_portfolio(
            _sample_dataframe()
        )
    )

    # --------------------------------------------------
    # TOP LEVEL CONTRACT
    # --------------------------------------------------

    expected_keys = {
        "regime",
        "portfolio",
        "best",
        "allocation",
        "risk",
        "decision",
        "exposure",
        "summary",
    }

    assert expected_keys.issubset(
        result.keys()
    )

    # --------------------------------------------------
    # REGIME
    # --------------------------------------------------

    assert result[
        "regime"
    ] == "TRENDING"

    # --------------------------------------------------
    # PORTFOLIO
    # --------------------------------------------------

    assert len(
        result["portfolio"]
    ) == 1

    item = result[
        "portfolio"
    ][0]

    assert item[
        "evaluation_status"
    ] == "SUCCESS"

    # --------------------------------------------------
    # BEST
    # --------------------------------------------------

    assert result[
        "best"
    ]["name"] == "strategy_a"

    # --------------------------------------------------
    # ALLOCATION
    # --------------------------------------------------

    assert result[
        "allocation"
    ][0]["allocation"] == 1.0

    # --------------------------------------------------
    # RISK
    # --------------------------------------------------

    assert result[
        "risk"
    ]["risk_level"] == "LOW"

    # --------------------------------------------------
    # DECISION
    # --------------------------------------------------

    assert result[
        "decision"
    ]["status"] == (
        "READY FOR FORWARD TEST"
    )

    # --------------------------------------------------
    # EXPOSURE
    # --------------------------------------------------

    assert result[
        "exposure"
    ] == pytest.approx(
        1.0
    )

    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    assert result[
        "summary"
    ]["strategies"] == 1


# ==================================================
# FAILED STRATEGY MUST SURVIVE NORMALIZATION
# ==================================================

def test_failed_strategy_preserved_in_portfolio(
    monkeypatch,
):

    results = [
        _failed_result()
    ]

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: results,
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda values: None,
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda values, top_n=3: [],
    )

    monkeypatch.setattr(
        institutional,
        "calculate_portfolio_risk",
        lambda allocation: {},
    )

    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, values: {
            "status": "NOT RECOMMENDED",
        },
    )

    monkeypatch.setattr(
        institutional,
        "portfolio_summary",
        lambda values: {},
    )

    result = (
        institutional.build_institutional_portfolio(
            _sample_dataframe()
        )
    )

    assert len(
        result["portfolio"]
    ) == 1

    assert result[
        "portfolio"
    ][0][
        "evaluation_status"
    ] == "FAILED"

    assert result[
        "decision"
    ]["status"] == "NOT RECOMMENDED"


# ==================================================
# INSUFFICIENT DATA MUST NOT BECOME SUCCESS
# ==================================================

def test_insufficient_data_strategy(
    monkeypatch,
):

    results = [
        _empty_result()
    ]

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: results,
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda values: None,
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda values, top_n=3: [],
    )

    monkeypatch.setattr(
        institutional,
        "calculate_portfolio_risk",
        lambda allocation: {},
    )

    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, values: {
            "status": "NOT RECOMMENDED",
        },
    )

    monkeypatch.setattr(
        institutional,
        "portfolio_summary",
        lambda values: {},
    )

    result = (
        institutional.build_institutional_portfolio(
            _sample_dataframe()
        )
    )

    assert result[
        "portfolio"
    ][0][
        "evaluation_status"
    ] == "INSUFFICIENT_DATA"


# ==================================================
# BACKWARD COMPATIBILITY
# ==================================================

def test_run_portfolio_backward_compatible(
    monkeypatch,
):

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [
            _successful_result()
        ],
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda values: values[0],
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda values, top_n=3: [
            {
                "name": "strategy_a",
                "allocation": 1.0,
            }
        ],
    )

    monkeypatch.setattr(
        institutional,
        "calculate_portfolio_risk",
        lambda allocation: {},
    )

    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, values: {},
    )

    monkeypatch.setattr(
        institutional,
        "portfolio_summary",
        lambda values: {},
    )

    result = (
        institutional.run_institutional_portfolio(
            _sample_dataframe()
        )
    )

    assert isinstance(
        result,
        dict,
    )

    assert "portfolio" in result

    assert "allocation" in result

    assert "risk" in result

    assert "decision" in result


# ==================================================
# TOP N COMPATIBILITY
# ==================================================

def test_top_n_forwarded_to_allocation(
    monkeypatch,
):

    captured = {}

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [
            _successful_result()
        ],
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda values: values[0],
    )

    def fake_build_allocation(
        values,
        top_n=3,
    ):

        captured[
            "top_n"
        ] = top_n

        return [
            {
                "name": "strategy_a",
                "allocation": 1.0,
            }
        ]

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        fake_build_allocation,
    )

    monkeypatch.setattr(
        institutional,
        "calculate_portfolio_risk",
        lambda allocation: {},
    )

    monkeypatch.setattr(
        institutional,
        "evaluate_decision",
        lambda risk, values: {},
    )

    monkeypatch.setattr(
        institutional,
        "portfolio_summary",
        lambda values: {},
    )

    institutional.build_institutional_portfolio(
        _sample_dataframe(),
        top_n=5,
    )

    assert captured[
        "top_n"
    ] == 5


# ==================================================
# INSTITUTIONAL PORTFOLIO CONTRACT TESTS
# ==================================================

def test_institutional_portfolio_contract_keys(
    monkeypatch,
):

    import engine.institutional_portfolio_engine as institutional

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [],
    )

    result = (
        institutional.build_institutional_portfolio(
            object()
        )
    )

    expected_keys = {

        "regime",

        "portfolio",

        "best",

        "allocation",

        "risk",

        "decision",

        "exposure",

        "summary",

    }

    assert set(
        result.keys()
    ) == expected_keys


def test_best_strategy_comes_from_normalized_portfolio(
    monkeypatch,
):

    import engine.institutional_portfolio_engine as institutional

    raw_results = [

        {
            "name":
                "failed_strategy",

            "error":
                "strategy failed",
        },

        {
            "name":
                "working_strategy",

            "statistics":
                {
                    "total_trade":
                        10,
                },

            "score":
                100,
        },

    ]

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: raw_results,
    )

    monkeypatch.setattr(
        institutional,
        "get_best_strategy",
        lambda results: results[1],
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda *args, **kwargs: [],
    )

    result = (
        institutional.build_institutional_portfolio(
            object()
        )
    )

    assert result[
        "best"
    ] is not None

    assert result[
        "best"
    ][
        "name"
    ] == "working_strategy"

    assert result[
        "best"
    ][
        "evaluation_status"
    ] == institutional.STATUS_SUCCESS


def test_failed_strategy_preserves_normalized_contract(
    monkeypatch,
):

    import engine.institutional_portfolio_engine as institutional

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [

            {
                "name":
                    "broken_strategy",

                "error":
                    "execution failed",
            }

        ],
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda *args, **kwargs: [],
    )

    result = (
        institutional.build_institutional_portfolio(
            object()
        )
    )

    strategy = result[
        "portfolio"
    ][0]

    assert strategy[
        "evaluation_status"
    ] == institutional.STATUS_FAILED

    assert "rank" in strategy

    assert "score" in strategy

    assert "grade" in strategy

    assert "market_regime" in strategy

    assert "weight" in strategy

    assert "router_recommended" in strategy


def test_exposure_matches_normalized_allocation(
    monkeypatch,
):

    import engine.institutional_portfolio_engine as institutional

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [

            {
                "name":
                    "strategy_a",

                "statistics":
                    {
                        "total_trade":
                            10,
                    },
            }

        ],
    )

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        lambda *args, **kwargs: [

            {
                "name":
                    "strategy_a",

                "allocation":
                    0.60,
            },

            {
                "name":
                    "strategy_b",

                "weight":
                    0.40,
            },

        ],
    )

    result = (
        institutional.build_institutional_portfolio(
            object()
        )
    )

    assert result[
        "exposure"
    ] == 1.0


def test_regime_is_forwarded_to_allocation(
    monkeypatch,
):

    import engine.institutional_portfolio_engine as institutional

    captured = {}

    monkeypatch.setattr(
        institutional,
        "run_portfolio",
        lambda df: [

            {
                "name":
                    "trend_strategy",

                "statistics":
                    {
                        "total_trade":
                            10,
                    },

                "market_regime":
                    "TRENDING",
            }

        ],
    )

    def fake_build_allocation(
        results,
        max_strategies=3,
        regime=None,
    ):

        captured[
            "regime"
        ] = regime

        captured[
            "max_strategies"
        ] = max_strategies

        return []

    monkeypatch.setattr(
        institutional,
        "build_allocation",
        fake_build_allocation,
    )

    institutional.build_institutional_portfolio(
        object(),
        top_n=2,
    )

    assert captured[
        "regime"
    ] == "TRENDING"

    assert captured[
        "max_strategies"
    ] == 2    