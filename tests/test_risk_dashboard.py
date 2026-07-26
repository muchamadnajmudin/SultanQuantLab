from optimizer.risk_dashboard import build_risk_dashboard



def test_risk_dashboard():


    statistics = {

        "profit_factor": 2.1,

    }


    wfo_analysis = {

        "stability_score": 80,

    }


    monte_carlo_analysis = {

        "risk_level": "LOW",

    }



    dashboard = build_risk_dashboard(

        statistics,

        wfo_analysis,

        monte_carlo_analysis,

    )



    assert dashboard["quality_score"] == 100


    assert dashboard["risk_level"] == "INSTITUTIONAL"


    assert dashboard["summary"]["profit_factor"] == 2.1


    assert dashboard["summary"]["wfo_stability"] == 80


    assert dashboard["summary"]["monte_carlo"] == "LOW"



    print("=" * 50)

    print("RISK DASHBOARD TEST PASSED")

    print("=" * 50)