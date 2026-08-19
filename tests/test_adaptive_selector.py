from strategies.intelligence.adaptive_selector import (
    select_best_strategy
)



def test_selector():


    result = select_best_strategy({

        "A":0.3,

        "B":0.7,

    })


    assert result == "B"