from strategies.intelligence.strategy_weight import (
    normalize_weights
)



def test_weight():


    result = normalize_weights({

        "A":50,

        "B":50,

    })


    assert result["A"] == 0.5

    assert result["B"] == 0.5