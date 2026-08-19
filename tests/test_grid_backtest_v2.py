import pandas as pd

from engine.grid_backtest import GridBacktest, GridCostModel


def sample_data():
    return pd.DataFrame({
        "time": pd.date_range("2026-01-01", periods=8, freq="5min"),
        "open": [100, 100, 99, 98, 99, 100, 101, 101],
        "high": [100, 100, 99, 98.5, 99.5, 101.2, 102, 102],
        "low": [100, 98.5, 97.5, 97, 98.5, 99.5, 100.5, 100],
        "close": [100, 99, 98, 98.5, 99.5, 101, 101.5, 101],
    })


def test_flexible_capital_and_layers():
    engine = GridBacktest(
        spacing=[0.01, 0.02],
        tp_percent=0.01,
        capital=30,
        layers=3,
        costs=GridCostModel(0, 0),
    )
    result = engine.run(sample_data())
    assert result.max_capital_used <= 30
    assert result.cycles >= 1


def test_fees_reduce_net_profit():
    df = pd.DataFrame({
        "open": [100, 100, 101],
        "high": [100, 101.2, 101.2],
        "low": [100, 99.9, 100.5],
        "close": [100, 101, 101],
    })
    free = GridBacktest(
        spacing=[0.02],
        tp_percent=0.01,
        capital=100,
        layers=2,
        costs=GridCostModel(0, 0),
    ).run(df)
    costly = GridBacktest(
        spacing=[0.02],
        tp_percent=0.01,
        capital=100,
        layers=2,
        costs=GridCostModel(0.001, 0.001),
    ).run(df)
    assert costly.net_profit < free.net_profit


def test_result_contains_real_costs():
    result = GridBacktest(
        spacing=[0.01],
        tp_percent=0.005,
        capital=30,
        layers=2,
        costs=GridCostModel(0.001, 0.001, 0.0005, 0.0005),
    ).run(sample_data())
    assert result.fees >= 0
    assert result.slippage_cost >= 0
