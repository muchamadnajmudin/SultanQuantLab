import numpy as np
import pandas as pd

from optimizer.grid_optimizer import (
    optimize_flexible_grid,
    best_by_capital_and_layers,
)


def sample_df():
    n = 120
    close = np.linspace(100, 102, n)
    return pd.DataFrame({
        "open": close,
        "high": close * 1.003,
        "low": close * 0.997,
        "close": close,
    })


def test_flexible_optimizer_returns_capital_and_layer_matrix():
    result = optimize_flexible_grid(
        sample_df(),
        capitals=[15, 30],
        layer_counts=[2, 3],
        spacing_levels=[0.005, 0.01],
        tp_percents=[0.005],
        allocation_modes=["equal"],
        min_cycles=1,
    )

    assert not result.empty
    assert set(result["capital"]) == {15.0, 30.0}
    assert set(result["layers"]) == {2, 3}


def test_spacing_has_layers_minus_one_values():
    result = optimize_flexible_grid(
        sample_df(),
        capitals=[30],
        layer_counts=[3],
        spacing_levels=[0.005, 0.01],
        tp_percents=[0.005],
        allocation_modes=["equal"],
        min_cycles=1,
    )

    for value in result["spacing"]:
        assert len(value.split(",")) == 2


def test_best_by_capital_and_layers():
    result = optimize_flexible_grid(
        sample_df(),
        capitals=[15],
        layer_counts=[2, 3],
        spacing_levels=[0.005],
        tp_percents=[0.005],
        allocation_modes=["equal"],
        min_cycles=1,
    )

    best = best_by_capital_and_layers(result)

    assert len(best) == 2
    assert set(best["layers"]) == {2, 3}
