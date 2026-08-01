"""
==========================================
SULTAN QUANT OS
Test : Institutional Risk Dashboard
Version : 3.5.0
==========================================

Testing:

- Institutional scoring calculation
- Profit Factor weighting
- WFO stability weighting
- Monte Carlo weighting
- Drawdown weighting

"""


from optimizer.risk_dashboard import build_risk_dashboard



# ==================================================
# TEST FULL SCORE
# ==================================================

def test_risk_dashboard_full_score():


    statistics = {

        "profit_factor": 2.1,

        "max_drawdown_percent": 10,

    }


    wfo_analysis = {

        "stability_score": 80,

    }


    monte_carlo_analysis = {

        "risk_level": "LOW",
        "robustness_score": 100,

    }



    dashboard = build_risk_dashboard(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )



    assert dashboard["quality_score"] == 100


    assert dashboard["risk_level"] == "EXCELLENT"



    assert dashboard["summary"]["profit_factor"] == 2.1


    assert dashboard["summary"]["wfo_stability"] == 80


    assert dashboard["summary"]["monte_carlo"] == "LOW"


    assert dashboard["summary"]["drawdown"] == 10



    print("=" * 50)

    print("FULL SCORE RISK DASHBOARD TEST PASSED")

    print("=" * 50)




# ==================================================
# TEST WFO BAD SHOULD REDUCE SCORE
# ==================================================

def test_risk_dashboard_wfo_failure():


    statistics = {

        "profit_factor": 2.1,

        "max_drawdown_percent": 10,

    }


    wfo_analysis = {

        "stability_score": 40,

    }


    monte_carlo_analysis = {

        "risk_level": "LOW",
        "robustness_score": 100,

    }



    dashboard = build_risk_dashboard(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )



    assert dashboard["quality_score"] == 80


    assert dashboard["risk_level"] == "GOOD"



    print("=" * 50)

    print("WFO FAILURE PENALTY TEST PASSED")

    print("=" * 50)




# ==================================================
# TEST HIGH DRAWDOWN PENALTY
# ==================================================

def test_risk_dashboard_drawdown_penalty():


    statistics = {

        "profit_factor": 2.1,

        "max_drawdown_percent": 45,

    }


    wfo_analysis = {

        "stability_score": 80,

    }


    monte_carlo_analysis = {

        "risk_level": "LOW",
        "robustness_score": 100,

    }



    dashboard = build_risk_dashboard(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )



    assert dashboard["quality_score"] == 85


    assert dashboard["risk_level"] == "GOOD"



    print("=" * 50)

    print("DRAWDOWN PENALTY TEST PASSED")

    print("=" * 50)




# ==================================================
# TEST EMPTY STATISTICS
# ==================================================

def test_empty_dashboard():


    dashboard = build_risk_dashboard(

        {},

        {},

        {},

    )



    assert dashboard["quality_score"] == 0


    assert dashboard["risk_level"] == "UNKNOWN"



    print("=" * 50)

    print("EMPTY DASHBOARD TEST PASSED")

    print("=" * 50)