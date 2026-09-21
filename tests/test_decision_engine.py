from engine.decision_engine import (
    evaluate_decision,
)


def _strategy(
    pf=2.5,
    drawdown=10,
    score=90,
    name="test_strategy",
    status="SUCCESS",
    wfo=None,
    monte_carlo=None,
):

    result = {

        "name":
            name,

        "score":
            score,

        "evaluation_status":
            status,

        "statistics": {

            "profit_factor":
                pf,

            "max_drawdown_percent":
                drawdown,

        },

    }

    if wfo is not None:

        result["wfo"] = wfo

    if monte_carlo is not None:

        result["monte_carlo"] = monte_carlo

    return result


def _risk(
    status="LOW",
    wfo=None,
    monte_carlo=None,
):

    result = {

        "status":
            status,

    }

    if wfo is not None:

        result["wfo"] = wfo

    if monte_carlo is not None:

        result["monte_carlo"] = monte_carlo

    return result


def test_no_strategy():

    result = evaluate_decision(
        {},
        [],
    )

    assert result["decision"] == "NO TRADE"

    assert (
        result["live_ready"]
        is False
    )

    assert (
        result["readiness"]
        == "NOT READY FOR LIVE TRADING"
    )


def test_institutional_gate_passes():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={

                "stability_score":
                    85,

                "wfo_robustness_score":
                    95,

                "overfitting_risk":
                    "LOW",

            },

            monte_carlo={

                "risk_level":
                    "LOW",

                "robustness_score":
                    95,

            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is True
    )

    assert (
        result["readiness"]
        == "READY FOR LIVE TRADING"
    )

    assert (
        result["decision"]
        == "APPROVED"
    )

    assert (
        result["failed_gates"]
        == []
    )


def test_allocation_gate_blocks_when_no_strategy_is_allocatable():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={

                "stability_score":
                    85,

                "wfo_robustness_score":
                    95,

                "overfitting_risk":
                    "LOW",

            },

            monte_carlo={

                "risk_level":
                    "LOW",

                "robustness_score":
                    95,

            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
                score=90,
            )

        ],

        allocation=[],

    )

    assert (
        result["decision"]
        == "NEEDS OPTIMIZATION"
    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        result["gate_results"]["allocation"]
        is False
    )

    assert (
        "No allocatable strategy available"
        in result["failed_gates"]
    )


def test_allocation_gate_passes_with_allocatable_strategy():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={

                "stability_score":
                    85,

                "wfo_robustness_score":
                    95,

                "overfitting_risk":
                    "LOW",

            },

            monte_carlo={

                "risk_level":
                    "LOW",

                "robustness_score":
                    95,

            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
                score=90,
            )

        ],

        allocation=[

            {
                "name":
                    "test_strategy",

                "allocation":
                    1.0,
            }

        ],

    )

    assert (
        result["decision"]
        == "APPROVED"
    )

    assert (
        result["live_ready"]
        is True
    )

    assert (
        result["gate_results"]["allocation"]
        is True
    )


def test_legacy_decision_without_allocation_remains_compatible():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={

                "stability_score":
                    85,

                "wfo_robustness_score":
                    95,

                "overfitting_risk":
                    "LOW",

            },

            monte_carlo={

                "risk_level":
                    "LOW",

                "robustness_score":
                    95,

            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
                score=90,
            )

        ],

    )

    assert (
        result["decision"]
        == "APPROVED"
    )

    assert (
        result["live_ready"]
        is True
    )

    assert (
        result["gate_results"]["allocation"]
        is True
    )


def test_profit_factor_blocks_live():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=1.8,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "Profit Factor below 2.0"
        in result["failed_gates"]
    )


def test_drawdown_blocks_live():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=16,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "Drawdown above 15%"
        in result["failed_gates"]
    )


def test_wfo_blocks_live():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={
                "stability_score": 70,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "WFO stability below 80%"
        in result["failed_gates"]
    )


def test_overfitting_blocks_live():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "HIGH",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "WFO overfitting risk is high"
        in result["failed_gates"]
    )


def test_monte_carlo_blocks_live():

    result = evaluate_decision(

        _risk(

            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "MEDIUM",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "Monte Carlo risk is not LOW"
        in result["failed_gates"]
    )


def test_portfolio_risk_blocks_live():

    result = evaluate_decision(

        _risk(

            status="HIGH",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },

        ),

        [

            _strategy(
                pf=2.5,
                drawdown=10,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert (
        "Portfolio risk is HIGH or CRITICAL"
        in result["failed_gates"]
    )




def test_failed_strategy_is_not_selected_as_best_strategy():

    result = evaluate_decision(

        _risk(
            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },
        ),

        [
            _strategy(
                pf=5.0,
                score=100,
                name="failed_strategy",
                status="FAILED",
            ),

            _strategy(
                pf=2.5,
                score=90,
                name="valid_strategy",
                status="SUCCESS",
            ),
        ],

    )

    assert (
        result["best_strategy"]
        == "valid_strategy"
    )


def test_insufficient_strategy_is_not_selected_as_best_strategy():

    result = evaluate_decision(

        _risk(
            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },
        ),

        [
            _strategy(
                pf=5.0,
                score=100,
                name="insufficient_strategy",
                status="INSUFFICIENT_DATA",
            ),

            _strategy(
                pf=2.5,
                score=90,
                name="valid_strategy",
                status="SUCCESS",
            ),
        ],

    )

    assert (
        result["best_strategy"]
        == "valid_strategy"
    )


def test_successful_strategy_ranking_is_preserved():

    result = evaluate_decision(

        _risk(
            status="LOW",

            wfo={
                "stability_score": 90,
                "wfo_robustness_score": 95,
                "overfitting_risk": "LOW",
            },

            monte_carlo={
                "risk_level": "LOW",
                "robustness_score": 95,
            },
        ),

        [
            _strategy(
                pf=3.0,
                score=90,
                name="lower_score",
                status="SUCCESS",
            ),

            _strategy(
                pf=2.5,
                score=95,
                name="higher_score",
                status="SUCCESS",
            ),

            _strategy(
                pf=4.0,
                score=90,
                name="same_score_higher_pf",
                status="SUCCESS",
            ),
        ],

    )

    assert (
        result["best_strategy"]
        == "higher_score"
    )


def test_multiple_failed_gates_are_reported():

    result = evaluate_decision(

        _risk(

            status="HIGH",

            wfo={
                "stability_score": 40,
                "wfo_robustness_score": 30,
                "overfitting_risk": "HIGH",
            },

            monte_carlo={
                "risk_level": "HIGH",
                "robustness_score": 40,
            },

        ),

        [

            _strategy(
                pf=1.5,
                drawdown=25,
            )

        ],

    )

    assert (
        result["live_ready"]
        is False
    )

    assert len(
        result["failed_gates"]
    ) >= 5