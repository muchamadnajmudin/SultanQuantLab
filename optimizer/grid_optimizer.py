"""
SULTAN QUANT OS
Module : Grid Auto Optimizer
Version: 2.1.0

Automatically researches:
- flexible total capital
- flexible number of layers
- per-layer capital allocation
- per-layer downward spacing
- TP percentage
- maker/taker fees
- slippage

The existing optimize_grid() API is preserved.
"""

from __future__ import annotations

from itertools import combinations_with_replacement, product
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from engine.grid_backtest import GridBacktest, GridCostModel


def _validate_positive(values, name):
    values = [float(x) for x in values]
    if not values or any(x <= 0 for x in values):
        raise ValueError(f"{name} must contain positive values")
    return values


def _spacing_candidates(
    spacing_levels: Sequence[float],
    layer_count: int,
) -> list[list[float]]:
    """
    Generate every non-decreasing spacing sequence of length
    layer_count - 1.

    Example levels:
        [0.75%, 1.0%, 1.5%, 2.0%, 2.5%, 3.0%]

    For 4 layers, the optimizer tests:
        [0.75,0.75,0.75]
        [0.75,0.75,1.00]
        ...
        [3.00,3.00,3.00]

    Non-decreasing spacing prevents the optimizer from producing
    obviously contradictory grids where deeper layers are closer
    together than earlier layers.
    """
    if layer_count <= 1:
        return [[]]

    levels = sorted(set(_validate_positive(spacing_levels, "spacing_levels")))
    return [
        list(x)
        for x in combinations_with_replacement(
            levels,
            layer_count - 1,
        )
    ]


def _allocation_from_mode(
    capital: float,
    layers: int,
    mode: str = "equal",
    growth: float = 1.0,
) -> list[float]:
    """
    Build layer capital automatically.

    equal:
        all layers equal.

    deeper:
        later layers receive progressively more capital.
        growth=1.25 means each next layer gets 25% more
        than the previous layer before normalization.
    """
    if capital <= 0 or layers <= 0:
        raise ValueError("capital and layers must be > 0")

    if mode == "equal":
        weights = np.ones(layers, dtype=float)
    elif mode == "deeper":
        if growth < 1.0:
            raise ValueError("growth must be >= 1 for deeper mode")
        weights = np.array(
            [growth ** i for i in range(layers)],
            dtype=float,
        )
    else:
        raise ValueError("allocation mode must be 'equal' or 'deeper'")

    weights /= weights.sum()
    return (weights * capital).tolist()


def _score(
    result,
    min_cycles: int,
    drawdown_penalty: float = 1.0,
) -> float:
    """
    Ranking score intentionally rewards net profitability and PF,
    while penalizing drawdown.

    This is NOT a live-trading decision threshold.
    """
    if result.cycles < min_cycles:
        return -1e12

    pf = float(result.profit_factor)
    if not np.isfinite(pf):
        pf_component = 10.0
    else:
        pf_component = min(max(pf, 0.0), 10.0)

    net = float(result.net_profit)
    dd = abs(float(result.max_drawdown_pct))

    return (
        net
        * max(pf_component, 0.01)
        / (1.0 + drawdown_penalty * dd / 10.0)
    )


def optimize_grid(
    df: pd.DataFrame,
    spacing_sets: Sequence[Sequence[float]] | None = None,
    tp_percents: Sequence[float] | None = None,
    capital_per_layer: float = 100.0,
    fee_rate: float = 0.0010,
):
    """
    Backward-compatible optimizer.

    Existing callers can continue to pass spacing_sets and
    capital_per_layer.
    """
    if spacing_sets is None:
        raise ValueError("spacing_sets is required")

    tp_percents = _validate_positive(
        tp_percents or [0.005, 0.006, 0.0075, 0.01],
        "tp_percents",
    )

    rows = []

    for spacing in spacing_sets:
        spacing = _validate_positive(spacing, "spacing")
        layers = len(spacing) + 1
        capital = float(capital_per_layer) * layers

        costs = GridCostModel(
            maker_fee_rate=float(fee_rate),
            taker_fee_rate=float(fee_rate),
        )

        for tp in tp_percents:
            result = GridBacktest(
                spacing=spacing,
                tp_percent=tp,
                capital=capital,
                layers=layers,
                costs=costs,
            ).run(df)

            rows.append({
                "spacing": ",".join(f"{x:.5f}" for x in spacing),
                "layers": layers,
                "tp_percent": tp,
                "capital": capital,
                "layer_capital": capital / layers,
                "cycles": result.cycles,
                "win_rate": result.win_rate,
                "gross_profit": result.gross_profit,
                "fees": result.fees,
                "slippage_cost": result.slippage_cost,
                "net_profit": result.net_profit,
                "profit_factor": result.profit_factor,
                "max_drawdown_pct": result.max_drawdown_pct,
                "max_capital_used": result.max_capital_used,
                "avg_layers": result.avg_layers,
                "avg_return_pct": result.avg_return_pct,
                "median_return_pct": result.median_return_pct,
                "score": _score(result, min_cycles=1),
            })

    return (
        pd.DataFrame(rows)
        .sort_values("score", ascending=False)
        .reset_index(drop=True)
    )


def optimize_flexible_grid(
    df: pd.DataFrame,
    capitals: Sequence[float] = (15, 30, 50, 100, 250, 500),
    layer_counts: Sequence[int] = (2, 3, 4, 5),
    spacing_levels: Sequence[float] = (
        0.005,
        0.0075,
        0.010,
        0.0125,
        0.015,
        0.020,
        0.025,
        0.030,
    ),
    tp_percents: Sequence[float] = (
        0.005,
        0.006,
        0.0075,
        0.010,
        0.0125,
        0.015,
        0.020,
    ),
    allocation_modes: Sequence[str] = ("equal", "deeper"),
    deeper_growth: float = 1.25,
    maker_fee_rate: float = 0.0010,
    taker_fee_rate: float = 0.0010,
    buy_slippage_rate: float = 0.0,
    sell_slippage_rate: float = 0.0,
    entry_fee_type: str = "maker",
    exit_fee_type: str = "maker",
    min_cycles: int = 10,
    drawdown_penalty: float = 1.0,
) -> pd.DataFrame:
    """
    Main automatic optimizer.

    It does NOT assume a fixed $15 first order.

    For each total capital:
        test each layer count
        test every non-decreasing spacing sequence
        test every TP
        test equal and deeper-weighted allocation

    The result therefore answers:

        "For this amount of capital and this number of layers,
         what spacing between layers and TP performed best
         after trading costs?"
    """
    capitals = _validate_positive(capitals, "capitals")
    tp_percents = _validate_positive(tp_percents, "tp_percents")
    spacing_levels = _validate_positive(spacing_levels, "spacing_levels")

    layer_counts = sorted(set(int(x) for x in layer_counts))
    if not layer_counts or any(x < 1 for x in layer_counts):
        raise ValueError("layer_counts must contain integers >= 1")

    costs = GridCostModel(
        maker_fee_rate=float(maker_fee_rate),
        taker_fee_rate=float(taker_fee_rate),
        buy_slippage_rate=float(buy_slippage_rate),
        sell_slippage_rate=float(sell_slippage_rate),
    )

    rows = []

    for capital in capitals:
        for layers in layer_counts:
            if layers == 1:
                spacing_candidates = [[]]
            else:
                spacing_candidates = _spacing_candidates(
                    spacing_levels,
                    layers,
                )

            for spacing in spacing_candidates:
                for tp in tp_percents:
                    for allocation_mode in allocation_modes:
                        allocations = _allocation_from_mode(
                            capital=capital,
                            layers=layers,
                            mode=allocation_mode,
                            growth=deeper_growth,
                        )

                        result = GridBacktest(
                            spacing=spacing or [0.01] * max(layers - 1, 1),
                            tp_percent=tp,
                            capital=capital,
                            layers=layers,
                            layer_capital=allocations,
                            costs=costs,
                            entry_fee_type=entry_fee_type,
                            exit_fee_type=exit_fee_type,
                        ).run(df)

                        rows.append({
                            "capital": capital,
                            "layers": layers,
                            "allocation_mode": allocation_mode,
                            "layer_capital": ",".join(
                                f"{x:.4f}" for x in allocations
                            ),
                            "spacing": ",".join(
                                f"{x:.5f}" for x in spacing
                            ) if spacing else "",
                            "tp_percent": tp,
                            "cycles": result.cycles,
                            "wins": result.wins,
                            "losses": result.losses,
                            "win_rate": result.win_rate,
                            "gross_profit": result.gross_profit,
                            "fees": result.fees,
                            "slippage_cost": result.slippage_cost,
                            "net_profit": result.net_profit,
                            "profit_factor": result.profit_factor,
                            "avg_trade": result.avg_trade,
                            "max_drawdown_pct": result.max_drawdown_pct,
                            "max_capital_used": result.max_capital_used,
                            "avg_layers": result.avg_layers,
                            "avg_return_pct": result.avg_return_pct,
                            "median_return_pct": result.median_return_pct,
                            "score": _score(
                                result,
                                min_cycles=min_cycles,
                                drawdown_penalty=drawdown_penalty,
                            ),
                        })

    result_df = pd.DataFrame(rows)

    if result_df.empty:
        return result_df

    return (
        result_df
        .sort_values(
            ["capital", "score"],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )


def best_by_capital_and_layers(result_df: pd.DataFrame) -> pd.DataFrame:
    """Return the best configuration for every capital/layer pair."""
    if result_df.empty:
        return result_df.copy()

    idx = (
        result_df
        .groupby(["capital", "layers"])["score"]
        .idxmax()
    )

    return (
        result_df
        .loc[idx]
        .sort_values(["capital", "layers"])
        .reset_index(drop=True)
    )


def save_optimizer_result(result: pd.DataFrame, output: str | Path):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    return output


__all__ = [
    "optimize_grid",
    "optimize_flexible_grid",
    "best_by_capital_and_layers",
    "save_optimizer_result",
]
