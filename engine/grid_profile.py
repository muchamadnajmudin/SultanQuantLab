"""
==========================================
SULTAN QUANT OS
Module : Grid Profile
Version : 1.0.0
==========================================

Universal configuration profile for
crypto spot grid strategies.

Responsibilities
----------------
- Store symbol-specific grid configuration
- Validate capital and layer settings
- Validate grid spacing
- Support equal or custom capital allocation
- Preserve a reusable configuration object
- Remain independent from exchange APIs
- Remain independent from execution engines

Important
---------
This module does NOT:

- connect to Bitget
- place orders
- fetch market data
- modify existing grid engines

It only represents a validated grid configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional, Sequence


@dataclass
class GridProfile:
    """
    Universal grid configuration profile.

    Parameters
    ----------
    symbol:
        Trading symbol.

        Examples:
        - HYPEUSDT
        - BTCUSDT
        - ETHUSDT
        - SOLUSDT

    capital:
        Maximum capital allocated to this grid.

    layers:
        Total number of grid layers including
        the initial entry layer.

    spacing:
        Percentage decline required to open
        each subsequent layer.

        For 4 layers, spacing requires at least
        3 values.

        Example:

            layers = 4

            spacing = [
                0.01,
                0.015,
                0.02,
            ]

    tp_percent:
        Take-profit percentage measured from
        weighted average entry.

    layer_capital:
        Optional custom capital allocation
        for each layer.

        If omitted, capital is allocated equally.

    enabled:
        Allows the profile to be disabled
        without deleting its configuration.

    metadata:
        Optional additional information.

        Example:
        - exchange
        - timeframe
        - research source
        - optimizer score
    """

    symbol: str

    capital: float

    layers: int

    spacing: Sequence[float]

    tp_percent: float

    layer_capital: Optional[Sequence[float]] = None

    enabled: bool = True

    metadata: dict = field(
        default_factory=dict
    )

    def __post_init__(self):

        self.symbol = str(
            self.symbol
        ).upper().strip()

        if not self.symbol:

            raise ValueError(
                "symbol must not be empty"
            )

        self.capital = float(
            self.capital
        )

        if self.capital <= 0:

            raise ValueError(
                "capital must be > 0"
            )

        self.layers = int(
            self.layers
        )

        if self.layers <= 0:

            raise ValueError(
                "layers must be > 0"
            )

        self.spacing = [
            float(value)
            for value in self.spacing
        ]

        if self.layers == 1:

            if self.spacing:

                raise ValueError(
                    "spacing must be empty "
                    "when layers is 1"
                )

        else:

            required_spacing = (
                self.layers - 1
            )

            if len(
                self.spacing
            ) < required_spacing:

                raise ValueError(
                    "spacing must contain at least "
                    f"{required_spacing} values "
                    f"for {self.layers} layers"
                )

            if any(
                value <= 0
                for value in self.spacing
            ):

                raise ValueError(
                    "spacing values must be > 0"
                )

        self.tp_percent = float(
            self.tp_percent
        )

        if self.tp_percent <= 0:

            raise ValueError(
                "tp_percent must be > 0"
            )

        if self.layer_capital is None:

            allocation = (
                self.capital
                / self.layers
            )

            self.layer_capital = [
                allocation
                for _ in range(
                    self.layers
                )
            ]

        else:

            self.layer_capital = [
                float(value)
                for value
                in self.layer_capital
            ]

            if len(
                self.layer_capital
            ) != self.layers:

                raise ValueError(
                    "layer_capital length "
                    "must equal layers"
                )

            if any(
                value <= 0
                for value
                in self.layer_capital
            ):

                raise ValueError(
                    "layer_capital values "
                    "must be > 0"
                )

            total_allocation = sum(
                self.layer_capital
            )

            if (
                total_allocation
                > self.capital + 1e-9
            ):

                raise ValueError(
                    "layer_capital total "
                    "exceeds capital"
                )

        if not isinstance(
            self.metadata,
            dict,
        ):

            raise ValueError(
                "metadata must be a dict"
            )

    # ========================================================
    # PROPERTIES
    # ========================================================

    @property
    def max_spacing_layers(self) -> int:
        """
        Number of available spacing steps.
        """

        return len(
            self.spacing
        )

    @property
    def total_allocated_capital(
        self,
    ) -> float:
        """
        Total capital assigned to layers.
        """

        return float(
            sum(
                self.layer_capital
            )
        )

    @property
    def unused_capital(
        self,
    ) -> float:
        """
        Capital remaining unallocated.
        """

        return float(
            self.capital
            - self.total_allocated_capital
        )

    @property
    def is_fully_allocated(
        self,
    ) -> bool:
        """
        True when all configured capital
        is allocated to layers.
        """

        return abs(
            self.unused_capital
        ) <= 1e-9

    # ========================================================
    # GRID HELPERS
    # ========================================================

    def get_layer_capital(
        self,
        layer_index: int,
    ) -> float:
        """
        Return capital allocation for
        a zero-based layer index.
        """

        if (
            layer_index < 0
            or layer_index >= self.layers
        ):

            raise IndexError(
                "layer_index out of range"
            )

        return float(
            self.layer_capital[
                layer_index
            ]
        )

    def get_spacing(
        self,
        spacing_index: int,
    ) -> float:
        """
        Return spacing percentage for
        a zero-based spacing index.
        """

        if (
            spacing_index < 0
            or spacing_index
            >= len(self.spacing)
        ):

            raise IndexError(
                "spacing_index out of range"
            )

        return float(
            self.spacing[
                spacing_index
            ]
        )

    # ========================================================
    # SERIALIZATION
    # ========================================================

    def to_dict(self) -> dict:
        """
        Convert profile to a plain dictionary.
        """

        result = asdict(
            self
        )

        result["spacing"] = list(
            self.spacing
        )

        result["layer_capital"] = list(
            self.layer_capital
        )

        result["metadata"] = dict(
            self.metadata
        )

        return result

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "GridProfile":
        """
        Create a GridProfile from a dictionary.
        """

        if not isinstance(
            data,
            dict,
        ):

            raise ValueError(
                "data must be a dict"
            )

        return cls(
            symbol=data["symbol"],
            capital=data["capital"],
            layers=data["layers"],
            spacing=data["spacing"],
            tp_percent=data["tp_percent"],
            layer_capital=data.get(
                "layer_capital"
            ),
            enabled=data.get(
                "enabled",
                True,
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )