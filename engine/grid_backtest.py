"""
==========================================
SULTAN QUANT OS
Module : Grid Backtest Engine
Version: 2.1.0
==========================================

Realistic long-only SPOT grid backtest.

Features
--------
- Flexible total capital
- Flexible layer count
- Flexible capital allocation per layer
- Flexible grid spacing
- Maker / taker fees
- Buy / sell slippage
- Net P&L after all costs
- Capital usage tracking
- Drawdown tracking
- Trade-by-trade result
- Conservative OHLC handling
- Trigger price separated from execution price

Important
---------
This module is RESEARCH / BACKTEST ONLY.

It does not place live orders.

API credentials are never stored here.

Cost model
----------
Gross P&L
    ↓
Trading fees
    ↓
Slippage cost
    ↓
Net P&L
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Sequence, Optional

import numpy as np
import pandas as pd


# ============================================================
# COST MODEL
# ============================================================


@dataclass(frozen=True)
class GridCostModel:
    """
    Trading cost model.

    All rates are decimal fractions.

    Example
    -------
    0.001 = 0.10%
    0.0008 = 0.08%
    """

    maker_fee_rate: float = 0.0010
    taker_fee_rate: float = 0.0010

    buy_slippage_rate: float = 0.0000
    sell_slippage_rate: float = 0.0000

    def __post_init__(self):

        for name in (
            "maker_fee_rate",
            "taker_fee_rate",
            "buy_slippage_rate",
            "sell_slippage_rate",
        ):

            value = float(
                getattr(self, name)
            )

            if value < 0:

                raise ValueError(
                    f"{name} must be >= 0"
                )


# ============================================================
# TRADE RESULT
# ============================================================


@dataclass
class GridTrade:
    """
    One completed grid cycle.
    """

    cycle: int

    entry_time: object
    exit_time: object

    entry_price: float
    exit_price: float

    capital: float

    layers: int

    gross_profit: float

    fees: float

    slippage_cost: float

    net_profit: float

    return_pct: float

    max_drawdown_pct: float

    max_capital_used: float

    exit_reason: str = "TP"

    def to_dict(self):

        return asdict(self)


# ============================================================
# BACKTEST RESULT
# ============================================================


@dataclass
class GridBacktestResult:

    trades: list[GridTrade]

    cycles: int

    wins: int

    losses: int

    win_rate: float

    gross_profit: float

    fees: float

    slippage_cost: float

    net_profit: float

    profit_factor: float

    avg_trade: float

    max_drawdown_pct: float

    max_capital_used: float

    avg_layers: float

    avg_return_pct: float

    median_return_pct: float

    def to_dict(self):

        return {
            "cycles": self.cycles,
            "wins": self.wins,
            "losses": self.losses,
            "win_rate": self.win_rate,
            "gross_profit": self.gross_profit,
            "fees": self.fees,
            "slippage_cost": self.slippage_cost,
            "net_profit": self.net_profit,
            "profit_factor": self.profit_factor,
            "avg_trade": self.avg_trade,
            "max_drawdown_pct": self.max_drawdown_pct,
            "max_capital_used": self.max_capital_used,
            "avg_layers": self.avg_layers,
            "avg_return_pct": self.avg_return_pct,
            "median_return_pct": self.median_return_pct,
        }


# ============================================================
# GRID BACKTEST ENGINE
# ============================================================


class GridBacktest:
    """
    Long-only SPOT grid backtest.

    Parameters
    ----------
    spacing:
        Percentage decline required from the previous
        filled layer to activate the next layer.

        Example:

            [0.01, 0.02, 0.03]

        means:

            Layer 2:
                -1.00%

            Layer 3:
                -2.00%
                from previous filled layer

            Layer 4:
                -3.00%
                from previous filled layer

    tp_percent:
        Take-profit percentage from weighted-average
        entry price.

    capital:
        Maximum total capital available to the grid.

    layers:
        Maximum number of layers.

        If omitted:

            len(spacing) + 1

    layer_capital:
        Optional explicit capital allocation per layer.

    costs:
        GridCostModel.

    entry_fee_type:
        "maker" or "taker"

    exit_fee_type:
        "maker" or "taker"


    OHLC MODEL
    ----------
    A candle only provides:

        open
        high
        low
        close

    It does not tell us the exact intrabar sequence.

    Therefore this engine uses a deterministic conservative rule:

        1. Check TP first.
        2. If TP is not reached, evaluate drawdown.
        3. Add at most one new layer per candle.

    This avoids pretending to know the exact
    high/low sequence inside a candle.

    Important
    ---------
    This is still a research approximation.

    It should later be validated with lower timeframe
    data and/or tick data before live deployment.
    """

    def __init__(
        self,
        spacing: Sequence[float],
        tp_percent: float,
        capital: float,
        layers: Optional[int] = None,
        layer_capital: Optional[Sequence[float]] = None,
        costs: Optional[GridCostModel] = None,
        entry_fee_type: str = "maker",
        exit_fee_type: str = "maker",
    ):

        # ----------------------------------------------------
        # SPACING
        # ----------------------------------------------------

        self.spacing = [
            float(x)
            for x in spacing
        ]

        if not self.spacing:

            raise ValueError(
                "spacing must not be empty"
            )

        if any(
            x <= 0
            for x in self.spacing
        ):

            raise ValueError(
                "spacing values must be > 0"
            )

        # ----------------------------------------------------
        # TAKE PROFIT
        # ----------------------------------------------------

        self.tp_percent = float(
            tp_percent
        )

        if self.tp_percent <= 0:

            raise ValueError(
                "tp_percent must be > 0"
            )

        # ----------------------------------------------------
        # CAPITAL
        # ----------------------------------------------------

        self.capital = float(
            capital
        )

        if self.capital <= 0:

            raise ValueError(
                "capital must be > 0"
            )

        # ----------------------------------------------------
        # LAYERS
        # ----------------------------------------------------

        self.layers_target = int(
            layers
            if layers is not None
            else len(self.spacing) + 1
        )

        if self.layers_target <= 0:

            raise ValueError(
                "layers must be > 0"
            )

        if len(self.spacing) < (
            self.layers_target - 1
        ):

            raise ValueError(
                "spacing must contain "
                "at least layers-1 values"
            )

        # ----------------------------------------------------
        # CAPITAL ALLOCATION
        # ----------------------------------------------------

        if layer_capital is None:

            self.allocations = (
                self._equal_allocations(
                    self.capital,
                    self.layers_target,
                )
            )

        else:

            self.allocations = [
                float(x)
                for x in layer_capital
            ]

            if len(
                self.allocations
            ) != self.layers_target:

                raise ValueError(
                    "layer_capital length "
                    "must equal layers"
                )

            if any(
                x <= 0
                for x in self.allocations
            ):

                raise ValueError(
                    "layer_capital values "
                    "must be > 0"
                )

            if (
                sum(self.allocations)
                > self.capital + 1e-9
            ):

                raise ValueError(
                    "layer_capital total "
                    "exceeds capital"
                )

        # ----------------------------------------------------
        # COST MODEL
        # ----------------------------------------------------

        self.costs = (
            costs
            if costs is not None
            else GridCostModel()
        )

        # ----------------------------------------------------
        # FEE TYPES
        # ----------------------------------------------------

        if entry_fee_type not in (
            "maker",
            "taker",
        ):

            raise ValueError(
                "entry_fee_type must be "
                "maker or taker"
            )

        if exit_fee_type not in (
            "maker",
            "taker",
        ):

            raise ValueError(
                "exit_fee_type must be "
                "maker or taker"
            )

        self.entry_fee_type = (
            entry_fee_type
        )

        self.exit_fee_type = (
            exit_fee_type
        )

    # ========================================================
    # EQUAL ALLOCATION
    # ========================================================

    @staticmethod
    def _equal_allocations(
        capital: float,
        layers: int,
    ) -> list[float]:

        base = (
            capital
            / layers
        )

        return [
            base
            for _ in range(layers)
        ]

    # ========================================================
    # FEE RATE
    # ========================================================

    def _fee_rate(
        self,
        side: str,
    ) -> float:

        if side == "entry":

            if (
                self.entry_fee_type
                == "maker"
            ):

                return float(
                    self.costs.maker_fee_rate
                )

            return float(
                self.costs.taker_fee_rate
            )

        if side == "exit":

            if (
                self.exit_fee_type
                == "maker"
            ):

                return float(
                    self.costs.maker_fee_rate
                )

            return float(
                self.costs.taker_fee_rate
            )

        raise ValueError(
            "side must be entry or exit"
        )

    # ========================================================
    # BUY EXECUTION PRICE
    # ========================================================

    def _buy_fill(
        self,
        trigger_price: float,
    ) -> float:

        return (
            trigger_price
            * (
                1.0
                + self.costs.buy_slippage_rate
            )
        )

    # ========================================================
    # SELL EXECUTION PRICE
    # ========================================================

    def _sell_fill(
        self,
        trigger_price: float,
    ) -> float:

        return (
            trigger_price
            * (
                1.0
                - self.costs.sell_slippage_rate
            )
        )

    # ========================================================
    # MAIN BACKTEST
    # ========================================================

    def run(
        self,
        df: pd.DataFrame,
    ) -> GridBacktestResult:

        # ----------------------------------------------------
        # VALIDATE COLUMNS
        # ----------------------------------------------------

        required = {
            "open",
            "high",
            "low",
            "close",
        }

        missing = (
            required
            - set(df.columns)
        )

        if missing:

            raise ValueError(
                f"Missing columns: "
                f"{sorted(missing)}"
            )

        # ----------------------------------------------------
        # COPY DATA
        # ----------------------------------------------------

        data = (
            df.copy()
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # NUMERIC CONVERSION
        # ----------------------------------------------------

        for column in required:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce",
            )

        # ----------------------------------------------------
        # DROP INVALID ROWS
        # ----------------------------------------------------

        data = (
            data
            .dropna(
                subset=list(required)
            )
            .reset_index(drop=True)
        )

        # ----------------------------------------------------
        # MINIMUM DATA
        # ----------------------------------------------------

        if len(data) < 2:

            return self._result([])

        # ----------------------------------------------------
        # BACKTEST STATE
        # ----------------------------------------------------

        trades: list[GridTrade] = []

        cycle = 0

        i = 0

        # ====================================================
        # OUTER CYCLE LOOP
        # ====================================================

        while i < len(data) - 1:

            # ------------------------------------------------
            # ENTRY
            # ------------------------------------------------

            entry_time = data.iloc[i].get(
                "time",
                i,
            )

            first_price = float(
                data.iloc[i]["close"]
            )

            first_execution_price = (
                self._buy_fill(
                    first_price
                )
            )

            first_capital = (
                self.allocations[0]
            )

            first_qty = (
                first_capital
                / first_execution_price
            )

            fills = [
                {
                    "trigger_price": first_price,
                    "price": first_execution_price,
                    "capital": first_capital,
                    "qty": first_qty,
                }
            ]

            # ------------------------------------------------
            # COSTS
            # ------------------------------------------------

            entry_fee_rate = (
                self._fee_rate("entry")
            )

            exit_fee_rate = (
                self._fee_rate("exit")
            )

            # Entry fee
            fees = (
                first_capital
                * entry_fee_rate
            )

            # Buy slippage
            slippage_cost = (
                first_capital
                * self.costs.buy_slippage_rate
            )

            # ------------------------------------------------
            # CAPITAL TRACKING
            # ------------------------------------------------

            max_capital_used = (
                first_capital
            )

            # ------------------------------------------------
            # DRAW DOWN
            # ------------------------------------------------

            max_dd = 0.0

            # ------------------------------------------------
            # NEXT LAYER
            # ------------------------------------------------

            next_layer = 1

            # ------------------------------------------------
            # CYCLE STATE
            # ------------------------------------------------

            closed = False

            # =================================================
            # FUTURE CANDLES
            # =================================================

            for j in range(
                i + 1,
                len(data),
            ):

                candle = data.iloc[j]

                low = float(
                    candle["low"]
                )

                high = float(
                    candle["high"]
                )

                # ---------------------------------------------
                # CURRENT POSITION
                # ---------------------------------------------

                total_capital = sum(
                    x["capital"]
                    for x in fills
                )

                total_qty = sum(
                    x["qty"]
                    for x in fills
                )

                # ---------------------------------------------
                # WEIGHTED AVERAGE ENTRY
                # ---------------------------------------------

                avg_entry = (
                    total_capital
                    / total_qty
                )

                # ---------------------------------------------
                # TAKE PROFIT
                # ---------------------------------------------

                tp_trigger_price = (
                    avg_entry
                    * (
                        1.0
                        + self.tp_percent
                    )
                )

                # =================================================
                # TP CHECK
                # =================================================

                if (
                    high
                    >= tp_trigger_price
                ):

                    # -----------------------------------------
                    # SELL EXECUTION
                    # -----------------------------------------

                    exit_price = (
                        self._sell_fill(
                            tp_trigger_price
                        )
                    )

                    exit_notional = (
                        total_qty
                        * exit_price
                    )

                    # -----------------------------------------
                    # GROSS PROFIT
                    #
                    # Based on execution prices.
                    # -----------------------------------------

                    gross_profit = (
                        exit_notional
                        - total_capital
                    )

                    # -----------------------------------------
                    # EXIT FEE
                    # -----------------------------------------

                    exit_fee = (
                        exit_notional
                        * exit_fee_rate
                    )

                    # -----------------------------------------
                    # TOTAL FEES
                    # -----------------------------------------

                    total_fees = (
                        fees
                        + exit_fee
                    )

                    # -----------------------------------------
                    # TOTAL SLIPPAGE
                    #
                    # Buy slippage was already tracked
                    # when each layer was filled.
                    #
                    # Sell slippage:
                    # difference between TP trigger and
                    # actual execution price.
                    # -----------------------------------------

                    sell_slippage_cost = (
                        total_qty
                        * (
                            tp_trigger_price
                            - exit_price
                        )
                    )

                    total_slippage = (
                        slippage_cost
                        + sell_slippage_cost
                    )

                    # -----------------------------------------
                    # NET PROFIT
                    #
                    # IMPORTANT:
                    # Do NOT subtract slippage twice.
                    # -----------------------------------------

                    net_profit = (
                        gross_profit
                        - total_fees
                    )

                    # Gross profit already contains the
                    # actual execution price, therefore the
                    # sell slippage is already reflected.
                    #
                    # For reporting, slippage_cost is
                    # informational and is NOT deducted again.

                    # -----------------------------------------
                    # RETURN
                    # -----------------------------------------

                    return_pct = (
                        net_profit
                        / total_capital
                        * 100.0
                    )

                    # -----------------------------------------
                    # CYCLE NUMBER
                    # -----------------------------------------

                    cycle += 1

                    # -----------------------------------------
                    # RECORD TRADE
                    # -----------------------------------------

                    trades.append(
                        GridTrade(
                            cycle=cycle,

                            entry_time=entry_time,

                            exit_time=candle.get(
                                "time",
                                j,
                            ),

                            entry_price=avg_entry,

                            exit_price=exit_price,

                            capital=total_capital,

                            layers=len(fills),

                            gross_profit=gross_profit,

                            fees=total_fees,

                            slippage_cost=total_slippage,

                            net_profit=net_profit,

                            return_pct=return_pct,

                            max_drawdown_pct=max_dd,

                            max_capital_used=max_capital_used,

                            exit_reason="TP",
                        )
                    )

                    # -----------------------------------------
                    # START NEXT CYCLE
                    # -----------------------------------------

                    i = j

                    closed = True

                    break

                # =================================================
                # MARK-TO-MARKET DRAWDOWN
                # =================================================

                equity_low = (
                    total_qty
                    * low
                )

                dd = (
                    (
                        equity_low
                        - total_capital
                    )
                    / total_capital
                    * 100.0
                )

                max_dd = min(
                    max_dd,
                    dd,
                )

                # =================================================
                # ADD NEXT LAYER
                # =================================================

                if (
                    next_layer
                    < self.layers_target
                ):

                    previous_entry = (
                        fills[-1]["price"]
                    )

                    spacing_rate = (
                        self.spacing[
                            next_layer - 1
                        ]
                    )

                    trigger_price = (
                        previous_entry
                        * (
                            1.0
                            - spacing_rate
                        )
                    )

                    # -----------------------------------------
                    # LAYER TRIGGERED
                    # -----------------------------------------

                    if (
                        low
                        <= trigger_price
                    ):

                        # -------------------------------------
                        # EXECUTION PRICE
                        # -------------------------------------

                        execution_price = (
                            self._buy_fill(
                                trigger_price
                            )
                        )

                        # -------------------------------------
                        # CAPITAL
                        # -------------------------------------

                        layer_capital = (
                            self.allocations[
                                next_layer
                            ]
                        )

                        # -------------------------------------
                        # QUANTITY
                        # -------------------------------------

                        quantity = (
                            layer_capital
                            / execution_price
                        )

                        # -------------------------------------
                        # STORE FILL
                        # -------------------------------------

                        fills.append(
                            {
                                "trigger_price": trigger_price,
                                "price": execution_price,
                                "capital": layer_capital,
                                "qty": quantity,
                            }
                        )

                        # -------------------------------------
                        # ENTRY FEE
                        # -------------------------------------

                        fees += (
                            layer_capital
                            * entry_fee_rate
                        )

                        # -------------------------------------
                        # BUY SLIPPAGE
                        # -------------------------------------

                        slippage_cost += (
                            layer_capital
                            * self.costs.buy_slippage_rate
                        )

                        # -------------------------------------
                        # CAPITAL USAGE
                        # -------------------------------------

                        current_capital_used = sum(
                            x["capital"]
                            for x in fills
                        )

                        max_capital_used = max(
                            max_capital_used,
                            current_capital_used,
                        )

                        # -------------------------------------
                        # NEXT LAYER
                        # -------------------------------------

                        next_layer += 1

            # =================================================
            # END OF DATA
            # =================================================

            if not closed:

                candle = data.iloc[-1]

                final_close = float(
                    candle["close"]
                )

                # ---------------------------------------------
                # POSITION
                # ---------------------------------------------

                total_capital = sum(
                    x["capital"]
                    for x in fills
                )

                total_qty = sum(
                    x["qty"]
                    for x in fills
                )

                avg_entry = (
                    total_capital
                    / total_qty
                )

                # ---------------------------------------------
                # FINAL SELL
                # ---------------------------------------------

                exit_price = (
                    self._sell_fill(
                        final_close
                    )
                )

                exit_notional = (
                    total_qty
                    * exit_price
                )

                # ---------------------------------------------
                # GROSS PROFIT
                # ---------------------------------------------

                gross_profit = (
                    exit_notional
                    - total_capital
                )

                # ---------------------------------------------
                # EXIT FEE
                # ---------------------------------------------

                exit_fee = (
                    exit_notional
                    * exit_fee_rate
                )

                # ---------------------------------------------
                # SELL SLIPPAGE
                # ---------------------------------------------

                sell_slippage_cost = (
                    total_qty
                    * (
                        final_close
                        - exit_price
                    )
                )

                total_slippage = (
                    slippage_cost
                    + sell_slippage_cost
                )

                # ---------------------------------------------
                # TOTAL FEES
                # ---------------------------------------------

                total_fees = (
                    fees
                    + exit_fee
                )

                # ---------------------------------------------
                # NET
                # ---------------------------------------------

                net_profit = (
                    gross_profit
                    - total_fees
                )

                # ---------------------------------------------
                # RETURN
                # ---------------------------------------------

                return_pct = (
                    net_profit
                    / total_capital
                    * 100.0
                )

                # ---------------------------------------------
                # CYCLE
                # ---------------------------------------------

                cycle += 1

                # ---------------------------------------------
                # RECORD
                # ---------------------------------------------

                trades.append(
                    GridTrade(
                        cycle=cycle,

                        entry_time=entry_time,

                        exit_time=candle.get(
                            "time",
                            len(data) - 1,
                        ),

                        entry_price=avg_entry,

                        exit_price=exit_price,

                        capital=total_capital,

                        layers=len(fills),

                        gross_profit=gross_profit,

                        fees=total_fees,

                        slippage_cost=total_slippage,

                        net_profit=net_profit,

                        return_pct=return_pct,

                        max_drawdown_pct=max_dd,

                        max_capital_used=max_capital_used,

                        exit_reason="END_OF_DATA",
                    )
                )

                break

        # =====================================================
        # RESULT
        # =====================================================

        return self._result(
            trades
        )

    # ========================================================
    # RESULT BUILDER
    # ========================================================

    @staticmethod
    def _result(
        trades: list[GridTrade],
    ) -> GridBacktestResult:

        # ----------------------------------------------------
        # EMPTY RESULT
        # ----------------------------------------------------

        if not trades:

            return GridBacktestResult(

                trades=[],

                cycles=0,

                wins=0,

                losses=0,

                win_rate=0.0,

                gross_profit=0.0,

                fees=0.0,

                slippage_cost=0.0,

                net_profit=0.0,

                profit_factor=0.0,

                avg_trade=0.0,

                max_drawdown_pct=0.0,

                max_capital_used=0.0,

                avg_layers=0.0,

                avg_return_pct=0.0,

                median_return_pct=0.0,
            )

        # ----------------------------------------------------
        # NET PROFITS
        # ----------------------------------------------------

        profits = np.array(
            [
                trade.net_profit
                for trade in trades
            ],
            dtype=float,
        )

        # ----------------------------------------------------
        # WINS
        # ----------------------------------------------------

        wins = profits[
            profits > 0
        ]

        # ----------------------------------------------------
        # LOSSES
        # ----------------------------------------------------

        losses = profits[
            profits < 0
        ]

        # ----------------------------------------------------
        # GROSS PROFIT
        # ----------------------------------------------------

        gross_profit = float(
            sum(
                trade.gross_profit
                for trade in trades
            )
        )

        # ----------------------------------------------------
        # FEES
        # ----------------------------------------------------

        total_fees = float(
            sum(
                trade.fees
                for trade in trades
            )
        )

        # ----------------------------------------------------
        # SLIPPAGE
        # ----------------------------------------------------

        total_slippage = float(
            sum(
                trade.slippage_cost
                for trade in trades
            )
        )

        # ----------------------------------------------------
        # NET PROFIT
        # ----------------------------------------------------

        net_profit = float(
            profits.sum()
        )

        # ----------------------------------------------------
        # GROSS PROFIT OF WINNING TRADES
        # ----------------------------------------------------

        winning_profit = float(
            wins.sum()
        ) if len(wins) else 0.0

        # ----------------------------------------------------
        # GROSS LOSS
        # ----------------------------------------------------

        losing_profit = float(
            abs(losses.sum())
        ) if len(losses) else 0.0

        # ----------------------------------------------------
        # PROFIT FACTOR
        # ----------------------------------------------------

        if losing_profit > 0:

            profit_factor = (
                winning_profit
                / losing_profit
            )

        else:

            profit_factor = float(
                "inf"
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return GridBacktestResult(

            trades=trades,

            cycles=len(trades),

            wins=int(
                (profits > 0).sum()
            ),

            losses=int(
                (profits <= 0).sum()
            ),

            win_rate=float(
                (
                    profits > 0
                ).mean()
                * 100.0
            ),

            gross_profit=gross_profit,

            fees=total_fees,

            slippage_cost=total_slippage,

            net_profit=net_profit,

            profit_factor=profit_factor,

            avg_trade=float(
                profits.mean()
            ),

            max_drawdown_pct=float(
                min(
                    trade.max_drawdown_pct
                    for trade in trades
                )
            ),

            max_capital_used=float(
                max(
                    trade.max_capital_used
                    for trade in trades
                )
            ),

            avg_layers=float(
                np.mean(
                    [
                        trade.layers
                        for trade in trades
                    ]
                )
            ),

            avg_return_pct=float(
                np.mean(
                    [
                        trade.return_pct
                        for trade in trades
                    ]
                )
            ),

            median_return_pct=float(
                np.median(
                    [
                        trade.return_pct
                        for trade in trades
                    ]
                )
            ),
        )

    # ========================================================
    # TRADES TO DATAFRAME
    # ========================================================

    @staticmethod
    def trades_to_dataframe(
        trades: list[GridTrade],
    ) -> pd.DataFrame:

        return pd.DataFrame(
            [
                trade.to_dict()
                for trade in trades
            ]
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def run_grid_backtest(
    df,
    spacing,
    tp_percent,
    capital,
    layers=None,
    layer_capital=None,
    costs=None,
    entry_fee_type="maker",
    exit_fee_type="maker",
):
    """
    Convenience wrapper.

    Example
    -------
    result = run_grid_backtest(
        df=df,
        spacing=[
            0.01,
            0.02,
            0.03,
        ],
        tp_percent=0.0075,
        capital=1000,
        costs=GridCostModel(
            maker_fee_rate=0.0008,
            taker_fee_rate=0.0010,
            buy_slippage_rate=0.0002,
            sell_slippage_rate=0.0002,
        ),
        entry_fee_type="maker",
        exit_fee_type="maker",
    )
    """

    engine = GridBacktest(

        spacing=spacing,

        tp_percent=tp_percent,

        capital=capital,

        layers=layers,

        layer_capital=layer_capital,

        costs=costs,

        entry_fee_type=entry_fee_type,

        exit_fee_type=exit_fee_type,
    )

    return engine.run(df)