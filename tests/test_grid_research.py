import numpy as np
import pandas as pd
import pytest

from engine.grid_research import (
    GridResearchEngine,
)


def make_test_data():

    return pd.DataFrame(
        {
            "time": pd.date_range(
                "2026-01-01",
                periods=10,
                freq="5min",
            ),

            "open": [
                100,
                100,
                99,
                98,
                97,
                98,
                99,
                100,
                101,
                102,
            ],

            "high": [
                100.5,
                100.2,
                99.5,
                98.5,
                98.0,
                99.0,
                100.0,
                101.0,
                102.0,
                103.0,
            ],

            "low": [
                99.5,
                98.8,
                97.5,
                96.5,
                96.0,
                97.0,
                98.0,
                99.0,
                100.0,
                101.0,
            ],

            "close": [
                100,
                99,
                98,
                97,
                98,
                99,
                100,
                101,
                102,
                103,
            ],
        }
    )


def test_engine_initializes():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=5,
    )

    assert len(engine.df) == 10

    assert engine.horizon_bars == 5


def test_mae():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=5,
    )

    mae = engine.calculate_mae()

    assert mae.name == "MAE"

    assert len(mae) == 10

    assert mae.iloc[0] < 0


def test_mfe():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=5,
    )

    mfe = engine.calculate_mfe()

    assert mfe.name == "MFE"

    assert len(mfe) == 10

    assert mfe.iloc[0] > 0


def test_drawdown_probability():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=5,
    )

    mae = engine.calculate_mae()

    result = (
        engine.calculate_drawdown_probability(
            mae,
            [
                0.01,
                0.02,
            ],
        )
    )

    assert 0.01 in result

    assert 0.02 in result

    assert 0 <= result[0.01] <= 100

    assert 0 <= result[0.02] <= 100


def test_conditional_recovery():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=8,
    )

    probabilities, recovery_bars = (
        engine.calculate_conditional_recovery(
            drawdown_levels=[
                0.01,
            ],
            recovery_levels=[
                0.01,
            ],
        )
    )

    key = (
        0.01,
        0.01,
    )

    assert key in probabilities

    assert key in recovery_bars

    assert (
        0 <= probabilities[key] <= 100
    )


def test_full_research():

    df = make_test_data()

    engine = GridResearchEngine(
        df,
        horizon_bars=5,
    )

    result = engine.research(
        drawdown_levels=[
            0.01,
            0.02,
        ],
        recovery_levels=[
            0.005,
            0.01,
        ],
    )

    assert result.entries > 0

    assert result.horizon_bars == 5

    assert len(
        result.drawdown_probability
    ) == 2

    assert len(
        result.recovery_probability
    ) == 4


def test_invalid_horizon():

    df = make_test_data()

    with pytest.raises(ValueError):

        GridResearchEngine(
            df,
            horizon_bars=0,
        )


def test_missing_columns():

    df = pd.DataFrame(
        {
            "close": [100, 101],
        }
    )

    with pytest.raises(ValueError):

        GridResearchEngine(
            df
        )