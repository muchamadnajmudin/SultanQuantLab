from optimizer.wfo_report import generate_wfo_report



def test_wfo_report():


    analysis = {

        "total_window": 2,

        "average_profit_factor": 1.5,

        "average_net_profit": 50,

        "stability_score": 100,

        "overfitting_risk": "LOW",

    }



    results = [

        {

            "window": 1,

            "best_parameter": {

                "RSI_OVERSOLD":10

            },

            "validation": {

                "profit_factor":2,

                "net_profit":100,

            }

        }

    ]



    report = generate_wfo_report(

        analysis,

        results,

    )



    assert "WFO REPORT" in report

    assert "Windows Tested" in report

    assert "Validation PF" in report



    print("=" * 50)

    print("WFO REPORT TEST PASSED")

    print("=" * 50)