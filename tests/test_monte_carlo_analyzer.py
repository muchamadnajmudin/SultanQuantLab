from optimizer.monte_carlo_analyzer import analyze_monte_carlo



def test_monte_carlo_analyzer():


    results = [

        {

            "final_balance": 12000,

            "max_drawdown": 500,

        },


        {

            "final_balance": 15000,

            "max_drawdown": 800,

        },


        {

            "final_balance": 10000,

            "max_drawdown": 1200,

        },

    ]



    analysis = analyze_monte_carlo(
        results
    )


    assert analysis["simulation_count"] == 3


    assert analysis["best_balance"] == 15000


    assert analysis["worst_balance"] == 10000


    assert analysis["worst_drawdown"] == 1200


    assert analysis["risk_level"] == "MEDIUM"



    print("=" * 50)

    print("MONTE CARLO ANALYZER TEST PASSED")

    print("=" * 50)