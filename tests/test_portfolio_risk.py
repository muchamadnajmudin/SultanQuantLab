from risk.portfolio_risk import (
    calculate_portfolio_risk,
)



def test_portfolio_risk():


    result = calculate_portfolio_risk({

        "A":0.5,

        "B":0.5,

    })


    assert result["status"] == "NORMAL"