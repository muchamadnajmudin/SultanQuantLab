import pandas as pd


from strategies.regime.market_regime import (
    detect_market_regime,
    recommended_strategy,
    regime_summary,
)


from strategies.regime.regime_score import (
    regime_score,
)



def test_market_regime():


    row = pd.Series({

        "EMA20":200,

        "EMA50":180,

        "EMA200":150,

        "ADX":30,

        "ATR":5,

        "close":2000,

    })


    result = detect_market_regime(
        row
    )


    assert result == "TRENDING"



def test_strategy_router():


    row = pd.Series({

        "EMA20":200,

        "EMA50":180,

        "EMA200":150,

        "ADX":30,

        "ATR":5,

        "close":2000,

    })


    result = recommended_strategy(
        row
    )


    assert result == "TREND_FOLLOWING"



def test_regime_score():


    row = pd.Series({

        "EMA20":200,

        "EMA50":180,

        "EMA200":150,

        "ADX":30,

        "ATR":5,

        "close":2000,

    })


    score = regime_score(
        row
    )


    assert score > 0



def test_regime_summary():


    row = pd.Series({

        "EMA20":200,

        "EMA50":180,

        "EMA200":150,

        "ADX":30,

        "ATR":5,

        "close":2000,

    })


    result = regime_summary(
        row
    )


    assert "regime" in result