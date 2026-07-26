from reports.monthly_returns import (
    calculate_monthly_returns,
    best_month,
    worst_month,
)



def test_monthly_returns():


    trades = [

        {

            "month": "2026-01",

            "profit": 100,

        },


        {

            "month": "2026-01",

            "profit": 50,

        },


        {

            "month": "2026-02",

            "profit": -75,

        },


        {

            "month": "2026-03",

            "profit": 200,

        },

    ]



    result = calculate_monthly_returns(
        trades
    )



    assert result == {

        "2026-01":150,

        "2026-02":-75,

        "2026-03":200,

    }



    assert best_month(
        result
    ) == "2026-03"



    assert worst_month(
        result
    ) == "2026-02"



    print("=" * 50)

    print("MONTHLY RETURNS TEST PASSED")

    print("=" * 50)