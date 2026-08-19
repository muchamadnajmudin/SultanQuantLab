"""
==========================================
SULTAN QUANT OS
Module : Grid Engine
Version: 2.0.0
==========================================

Core grid strategy engine.

Responsibilities
----------------
- Manage grid layers
- Calculate layer entry prices
- Calculate weighted average entry
- Calculate TP price
- Track capital allocation
- Track open layers
- Track realized profit
- Track fees
- Track slippage
- Track maximum capital used
- Track maximum open layers
- Support flexible capital per layer

Important
---------
This module is an execution-independent grid state engine.

It does NOT:
- connect to Bitget
- place live orders
- store API credentials
- fetch market data

The backtest engine is responsible for feeding
market events into this engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence


# ============================================================
# GRID LAYER
# ============================================================


@dataclass
class GridLayer:
    """
    Represents one grid position/layer.
    """

    index: int

    entry_price: float

    capital: float

    quantity: float

    fee: float = 0.0

    status: str = "OPEN"

    exit_price: Optional[float] = None

    exit_fee: float = 0.0

    gross_profit: float = 0.0

    net_profit: float = 0.0

    # --------------------------------------------------------
    # CLOSE
    # --------------------------------------------------------

    def close(
        self,
        exit_price: float,
        exit_fee: float = 0.0,
    ) -> float:
        """
        Close this layer.

        Returns
        -------
        float
            Net profit of the layer.
        """

        if self.status == "CLOSED":
            return self.net_profit

        self.exit_price = float(exit_price)

        self.exit_fee = float(exit_fee)

        proceeds = (
            self.quantity
            * self.exit_price
        )

        self.gross_profit = (
            proceeds
            - self.capital
        )

        self.net_profit = (
            self.gross_profit
            - self.fee
            - self.exit_fee
        )

        self.status = "CLOSED"

        return self.net_profit


# ============================================================
# GRID CONFIG
# ============================================================


@dataclass(frozen=True)
class GridConfig:
    """
    Grid configuration.

    spacing
        Percentage decline between consecutive layers.

        Example:

            [0.01, 0.02, 0.03]

        means:

            Layer 1 -> 1%
            Layer 2 -> 2%
            Layer 3 -> 3%

        relative to the previous layer.

    tp_percent
        TP percentage above weighted average entry.

    capital
        Total capital available.

    layers
        Number of grid layers.

    layer_capital
        Optional explicit capital allocation per layer.
    """

    spacing: Sequence[float]

    tp_percent: float

    capital: float

    layers: Optional[int] = None

    layer_capital: Optional[Sequence[float]] = None

    def __post_init__(self):

        spacing = [
            float(x)
            for x in self.spacing
        ]

        if not spacing:
            raise ValueError(
                "spacing must not be empty"
            )

        if any(
            x <= 0
            for x in spacing
        ):
            raise ValueError(
                "spacing values must be > 0"
            )

        if float(self.tp_percent) <= 0:
            raise ValueError(
                "tp_percent must be > 0"
            )

        if float(self.capital) <= 0:
            raise ValueError(
                "capital must be > 0"
            )

        target_layers = int(
            self.layers
            if self.layers is not None
            else len(spacing) + 1
        )

        if target_layers <= 0:
            raise ValueError(
                "layers must be > 0"
            )

        if len(spacing) < target_layers - 1:
            raise ValueError(
                "spacing must contain "
                "at least layers - 1 values"
            )

        if self.layer_capital is not None:

            allocations = [
                float(x)
                for x in self.layer_capital
            ]

            if len(allocations) != target_layers:
                raise ValueError(
                    "layer_capital length must "
                    "equal layers"
                )

            if any(
                x <= 0
                for x in allocations
            ):
                raise ValueError(
                    "layer_capital values "
                    "must be > 0"
                )

            if (
                sum(allocations)
                > float(self.capital)
                + 1e-9
            ):
                raise ValueError(
                    "layer_capital total "
                    "exceeds capital"
                )


# ============================================================
# GRID ENGINE RESULT
# ============================================================


@dataclass
class GridResult:

    realized_profit: float

    closed_layers: int

    max_open_layers: int

    max_capital_used: float

    layers: list[GridLayer] = field(
        default_factory=list
    )

    total_fees: float = 0.0

    total_slippage: float = 0.0

    gross_profit: float = 0.0

    open_layers: int = 0

    open_capital: float = 0.0

    weighted_average_entry: float = 0.0

    tp_price: Optional[float] = None


# ============================================================
# GRID ENGINE
# ============================================================


class GridEngine:
    """
    Core stateful grid engine.

    The engine does not know about candles.

    It receives price events through:

        open_layer()
        close_all()

    This makes it usable by:

        - backtest
        - optimizer
        - research
        - paper trading
        - future live execution adapter
    """

    def __init__(
        self,
        config: GridConfig,
    ):

        self.config = config

        self.spacing = [
            float(x)
            for x in config.spacing
        ]

        self.tp_percent = float(
            config.tp_percent
        )

        self.capital = float(
            config.capital
        )

        self.layers_target = int(
            config.layers
            if config.layers is not None
            else len(self.spacing) + 1
        )

        self.allocations = (
            self._build_allocations()
        )

        self.layers: list[GridLayer] = []

        self.realized_profit = 0.0

        self.total_fees = 0.0

        self.total_slippage = 0.0

        self.gross_profit = 0.0

        self.max_open_layers = 0

        self.max_capital_used = 0.0

    # ========================================================
    # ALLOCATIONS
    # ========================================================

    def _build_allocations(
        self,
    ) -> list[float]:
        """
        Build flexible layer allocations.

        If explicit layer capital is supplied,
        use it.

        Otherwise distribute total capital
        equally among layers.
        """

        if (
            self.config.layer_capital
            is not None
        ):

            return [
                float(x)
                for x
                in self.config.layer_capital
            ]

        allocation = (
            self.capital
            / self.layers_target
        )

        return [
            allocation
            for _ in range(
                self.layers_target
            )
        ]

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def open_layers(
        self,
    ) -> list[GridLayer]:

        return [
            layer
            for layer in self.layers
            if layer.status == "OPEN"
        ]

    @property
    def closed_layers(
        self,
    ) -> list[GridLayer]:

        return [
            layer
            for layer in self.layers
            if layer.status == "CLOSED"
        ]

    @property
    def open_layer_count(
        self,
    ) -> int:

        return len(
            self.open_layers
        )

    @property
    def capital_used(
        self,
    ) -> float:

        return float(
            sum(
                layer.capital
                for layer
                in self.open_layers
            )
        )

    @property
    def quantity(
        self,
    ) -> float:

        return float(
            sum(
                layer.quantity
                for layer
                in self.open_layers
            )
        )

    # ========================================================
    # WEIGHTED AVERAGE ENTRY
    # ========================================================

    @property
    def weighted_average_entry(
        self,
    ) -> float:

        layers = self.open_layers

        if not layers:
            return 0.0

        quantity = sum(
            layer.quantity
            for layer in layers
        )

        if quantity <= 0:
            return 0.0

        total_cost = sum(
            layer.capital
            for layer in layers
        )

        return (
            total_cost
            / quantity
        )

    # ========================================================
    # TP PRICE
    # ========================================================

    @property
    def tp_price(
        self,
    ) -> Optional[float]:

        avg = (
            self.weighted_average_entry
        )

        if avg <= 0:
            return None

        return (
            avg
            * (
                1.0
                + self.tp_percent
            )
        )

    # ========================================================
    # NEXT LAYER
    # ========================================================

    @property
    def next_layer_index(
        self,
    ) -> Optional[int]:

        index = len(
            self.layers
        )

        if index >= self.layers_target:
            return None

        return index

    # ========================================================
    # NEXT GRID PRICE
    # ========================================================

    def next_entry_price(
        self,
    ) -> Optional[float]:
        """
        Calculate next layer trigger.

        Layer 0 is opened externally.

        Every subsequent layer is based on
        the previous filled layer price.

        Example:

            layer 0 = 100
            spacing = 1%

            layer 1 = 99
        """

        if not self.layers:
            return None

        index = len(
            self.layers
        )

        if index >= self.layers_target:
            return None

        previous = self.layers[-1]

        spacing_index = index - 1

        spacing = self.spacing[
            spacing_index
        ]

        return (
            previous.entry_price
            * (
                1.0 - spacing
            )
        )

    # ========================================================
    # CAN ADD LAYER
    # ========================================================

    def can_add_layer(
        self,
    ) -> bool:

        return (
            len(self.layers)
            < self.layers_target
        )

    # ========================================================
    # OPEN LAYER
    # ========================================================

    def open_layer(
        self,
        price: float,
        fee_rate: float = 0.0,
        slippage_rate: float = 0.0,
    ) -> GridLayer:
        """
        Open the next grid layer.

        Parameters
        ----------
        price:
            Intended execution price.

        fee_rate:
            Entry fee rate.

        slippage_rate:
            Buy slippage rate.

        Returns
        -------
        GridLayer
        """

        if not self.can_add_layer():
            raise RuntimeError(
                "Maximum grid layers reached"
            )

        price = float(price)

        if price <= 0:
            raise ValueError(
                "price must be > 0"
            )

        fee_rate = float(
            fee_rate
        )

        slippage_rate = float(
            slippage_rate
        )

        if fee_rate < 0:
            raise ValueError(
                "fee_rate must be >= 0"
            )

        if slippage_rate < 0:
            raise ValueError(
                "slippage_rate must be >= 0"
            )

        # ----------------------------------------------------
        # Apply buy slippage
        # ----------------------------------------------------

        execution_price = (
            price
            * (
                1.0
                + slippage_rate
            )
        )

        layer_index = len(
            self.layers
        )

        capital = self.allocations[
            layer_index
        ]

        quantity = (
            capital
            / execution_price
        )

        fee = (
            capital
            * fee_rate
        )

        layer = GridLayer(
            index=layer_index,
            entry_price=execution_price,
            capital=capital,
            quantity=quantity,
            fee=fee,
        )

        self.layers.append(
            layer
        )

        self.total_fees += fee

        self.total_slippage += (
            capital
            * slippage_rate
        )

        self.max_open_layers = max(
            self.max_open_layers,
            self.open_layer_count,
        )

        self.max_capital_used = max(
            self.max_capital_used,
            self.capital_used,
        )

        return layer

    # ========================================================
    # OPEN FIRST LAYER
    # ========================================================

    def open_initial_layer(
        self,
        price: float,
        fee_rate: float = 0.0,
        slippage_rate: float = 0.0,
    ) -> GridLayer:

        if self.layers:
            raise RuntimeError(
                "Initial layer already opened"
            )

        return self.open_layer(
            price=price,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
        )

    # ========================================================
    # CHECK NEXT LAYER TRIGGER
    # ========================================================

    def should_add_layer(
        self,
        low_price: float,
    ) -> bool:
        """
        Determine whether the next grid layer
        should be activated.

        Uses the candle low supplied by the
        backtest engine.
        """

        if not self.can_add_layer():
            return False

        trigger = (
            self.next_entry_price()
        )

        if trigger is None:
            return False

        return (
            float(low_price)
            <= trigger
        )

    # ========================================================
    # ADD NEXT LAYER
    # ========================================================

    def add_next_layer(
        self,
        fee_rate: float = 0.0,
        slippage_rate: float = 0.0,
    ) -> Optional[GridLayer]:
        """
        Add the next layer at its calculated
        grid trigger.
        """

        trigger = (
            self.next_entry_price()
        )

        if trigger is None:
            return None

        return self.open_layer(
            price=trigger,
            fee_rate=fee_rate,
            slippage_rate=slippage_rate,
        )

    # ========================================================
    # CLOSE ALL
    # ========================================================

    def close_all(
        self,
        price: float,
        fee_rate: float = 0.0,
        slippage_rate: float = 0.0,
    ) -> float:
        """
        Close every open layer.

        Returns
        -------
        float
            Total net profit from the close.
        """

        if not self.open_layers:
            return 0.0

        price = float(price)

        if price <= 0:
            raise ValueError(
                "price must be > 0"
            )

        fee_rate = float(
            fee_rate
        )

        slippage_rate = float(
            slippage_rate
        )

        execution_price = (
            price
            * (
                1.0
                - slippage_rate
            )
        )

        total_net = 0.0

        for layer in list(
            self.open_layers
        ):

            proceeds = (
                layer.quantity
                * execution_price
            )

            exit_fee = (
                proceeds
                * fee_rate
            )

            before_profit = (
                layer.gross_profit
            )

            net = layer.close(
                exit_price=execution_price,
                exit_fee=exit_fee,
            )

            total_net += net

            self.total_fees += (
                exit_fee
            )

            self.total_slippage += (
                proceeds
                * slippage_rate
            )

            self.gross_profit += (
                layer.gross_profit
            )

        self.realized_profit += (
            total_net
        )

        return total_net

    # ========================================================
    # MARK TO MARKET
    # ========================================================

    def mark_to_market(
        self,
        price: float,
    ) -> float:
        """
        Current unrealized P&L.

        Fees already paid at entry are included
        in the layer cost.
        """

        price = float(price)

        if price <= 0:
            raise ValueError(
                "price must be > 0"
            )

        unrealized = 0.0

        for layer in self.open_layers:

            market_value = (
                layer.quantity
                * price
            )

            unrealized += (
                market_value
                - layer.capital
                - layer.fee
            )

        return float(
            unrealized
        )

    # ========================================================
    # EQUITY
    # ========================================================

    def equity(
        self,
        price: float,
    ) -> float:
        """
        Mark-to-market equity of currently
        deployed grid capital.
        """

        return float(
            self.capital_used
            + self.mark_to_market(
                price
            )
        )

    # ========================================================
    # RESET
    # ========================================================

    def reset(self) -> None:
        """
        Reset engine state.
        """

        self.layers = []

        self.realized_profit = 0.0

        self.total_fees = 0.0

        self.total_slippage = 0.0

        self.gross_profit = 0.0

        self.max_open_layers = 0

        self.max_capital_used = 0.0

    # ========================================================
    # RESULT
    # ========================================================

    def result(
        self,
    ) -> GridResult:

        return GridResult(

            realized_profit=(
                self.realized_profit
            ),

            closed_layers=sum(
                layer.status == "CLOSED"
                for layer in self.layers
            ),

            max_open_layers=(
                self.max_open_layers
            ),

            max_capital_used=(
                self.max_capital_used
            ),

            layers=self.layers.copy(),

            total_fees=(
                self.total_fees
            ),

            total_slippage=(
                self.total_slippage
            ),

            gross_profit=(
                self.gross_profit
            ),

            open_layers=(
                self.open_layer_count
            ),

            open_capital=(
                self.capital_used
            ),

            weighted_average_entry=(
                self.weighted_average_entry
            ),

            tp_price=(
                self.tp_price
            ),
        )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================


def create_grid_engine(
    spacing: Sequence[float],
    tp_percent: float,
    capital: float,
    layers: Optional[int] = None,
    layer_capital: Optional[
        Sequence[float]
    ] = None,
) -> GridEngine:
    """
    Convenience constructor.

    Example
    -------

    engine = create_grid_engine(
        spacing=[
            0.0075,
            0.0150,
            0.0250,
        ],
        tp_percent=0.0075,
        capital=100.0,
        layers=4,
    )
    """

    config = GridConfig(
        spacing=spacing,
        tp_percent=tp_percent,
        capital=capital,
        layers=layers,
        layer_capital=layer_capital,
    )

    return GridEngine(
        config
    )