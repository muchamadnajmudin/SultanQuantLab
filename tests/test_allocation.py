from strategies.allocation import (
    default_allocation,
)



def test_allocation():


    result = default_allocation(

        "TRENDING"

    )


    assert (

        result["TREND_FOLLOWING"]

        ==

        0.5

    )