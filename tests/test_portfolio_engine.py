from engine.portfolio_engine import (
    build_portfolio,
)



def test_portfolio_engine():


    result = build_portfolio(

        "TRENDING"

    )


    assert result["regime"] == "TRENDING"


    assert (

        "allocation"

        in result

    )


    assert (

        "risk"

        in result

    )