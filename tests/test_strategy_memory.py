from strategies.intelligence.strategy_memory import StrategyMemory



def test_memory_update():


    memory = StrategyMemory()


    memory.update(

        "TREND_FOLLOWING",

        "TRENDING",

        100,

        True

    )


    result = memory.get(

        "TREND_FOLLOWING",

        "TRENDING"

    )


    assert result["trades"] == 1

    assert result["wins"] == 1

    assert result["profit"] == 100