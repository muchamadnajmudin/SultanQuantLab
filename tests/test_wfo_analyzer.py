from optimizer.wfo_analyzer import analyze_wfo



def test_wfo_analyzer():


    results = [

        {

            "validation": {

                "profit_factor": 2.0,

                "net_profit": 100,

            }

        },


        {

            "validation": {

                "profit_factor": 1.5,

                "net_profit": 50,

            }

        },


        {

            "validation": {

                "profit_factor": 0.8,

                "net_profit": -20,

            }

        },

    ]



    analysis = analyze_wfo(
        results
    )



    assert analysis["total_window"] == 3


    assert analysis["average_profit_factor"] == 1.43


    assert analysis["average_net_profit"] == 43.33


    assert analysis["profitable_window"] == 2


    assert analysis["losing_window"] == 1


    assert analysis["stability_score"] == 66.67


    assert analysis["overfitting_risk"] == "MEDIUM"



    print("=" * 50)

    print("WFO ANALYZER TEST PASSED")

    print("=" * 50)