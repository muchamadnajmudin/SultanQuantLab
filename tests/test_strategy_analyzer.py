"""
==========================================
SULTAN QUANT OS
Strategy Analyzer Test
==========================================
"""

from analyzer.strategy_analyzer import analyze_strategy



def test_strategy_analyzer():

    statistics = {

        "profit_factor": 2.1,

        "expectancy": 1.5,

        "win_rate": 55,

        "max_drawdown_percent": 15,

        "total_trade": 100,

    }


    result = analyze_strategy(
        statistics
    )


    assert result["score"] == 100

    assert result["grade"] == "INSTITUTIONAL"

    assert len(result["strengths"]) > 0



def test_strategy_analyzer_weak():

    statistics = {

        "profit_factor": 0.8,

        "expectancy": -1,

        "win_rate": 30,

        "max_drawdown_percent": 60,

        "total_trade": 10,

    }


    result = analyze_strategy(
        statistics
    )


    assert result["grade"] == "WEAK"

    assert len(result["weaknesses"]) > 0