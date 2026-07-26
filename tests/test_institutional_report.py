from optimizer.institutional_report import generate_institutional_report



def test_institutional_report():


    report = generate_institutional_report(

        {

            "total_trade":100,

            "win_rate":60,

            "profit_factor":2,

            "net_profit":500,

        },


        {

            "total_window":10,

            "stability_score":80,

            "overfitting_risk":"LOW",

        },


        {

            "simulation_count":1000,

            "worst_drawdown":1500,

            "risk_level":"LOW",

        },


        {

            "quality_score":90,

            "risk_level":"INSTITUTIONAL",

        },

    )


    assert "INSTITUTIONAL STRATEGY REPORT" in report

    assert "PERFORMANCE" in report

    assert "WALK FORWARD VALIDATION" in report

    assert "MONTE CARLO VALIDATION" in report

    assert "FINAL SCORE" in report



    print("=" * 50)

    print("INSTITUTIONAL REPORT TEST PASSED")

    print("=" * 50)