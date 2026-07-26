from engine.loader import load_data
from engine.indicator_engine import calculate_indicators
from engine.strategy_engine import run_strategy


def test_strategy_engine():

    df = load_data(
        "data/XAUUSDc_M1.csv"
    )

    df = calculate_indicators(
        df
    )

    df = run_strategy(
        df
    )


    assert "BUY" in df.columns
    assert "SELL" in df.columns


    assert len(df) > 0


    buy_signal = int(
        df["BUY"].sum()
    )

    sell_signal = int(
        df["SELL"].sum()
    )


    assert buy_signal >= 0
    assert sell_signal >= 0