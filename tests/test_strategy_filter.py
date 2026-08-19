from engine.strategy_filter import (
    filter_strategies,
)


def test_strategy_filter():

    market = {

        "trend": "UPTREND",

        "volatility": "HIGH",

        "session": "LONDON",

    }

    candidates = filter_strategies(

        market,

    )

    assert isinstance(

        candidates,

        list,

    )

    assert len(

        candidates,

    ) > 0

    assert "score" in candidates[0]