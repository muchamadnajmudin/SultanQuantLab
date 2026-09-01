"""
==========================================
SULTAN QUANT LAB
Grid Execution Planner
Version : 1.0.0
==========================================

Responsibilities:

- Convert validated grid profiles into execution-ready plans
- Generate grid entry levels
- Preserve profile capital allocation
- Preserve take-profit configuration
- Support single and multiple profiles
- Prevent mutation of caller input
- Provide safe error handling

This module is intentionally isolated.

It does not:

- Place orders
- Connect to an exchange
- Modify portfolio state
- Modify institutional engines
- Modify source profiles
"""

from __future__ import annotations

from copy import deepcopy
from numbers import Real
from typing import Any


class GridExecutionPlanner:
    """
    Build execution-ready plans from validated grid profiles.

    Expected profile structure:

    {
        "symbol": "HYPEUSDT",
        "capital": 1000.0,
        "layers": 3,
        "take_profit": 0.02,
        "spacing": [0.01, 0.01],
        "layer_capital": [333.33, 333.33, 333.34]
    }

    The planner requires a current/reference price to calculate
    entry levels.

    Entry level formula:

        level[0] = reference_price

        level[n] =
            previous_level * (1 - spacing[n - 1])

    Example:

        reference_price = 100
        spacing = [0.01, 0.02]

        levels:

        100.00
         99.00
         97.02
    """

    def __init__(self, default_reference_price: float | None = None):
        self.default_reference_price = self._validate_reference_price(
            default_reference_price,
            allow_none=True,
        )

    @staticmethod
    def _is_number(value: Any) -> bool:
        return (
            isinstance(value, Real)
            and not isinstance(value, bool)
        )

    def _validate_reference_price(
        self,
        reference_price: Any,
        allow_none: bool = False,
    ) -> float | None:
        if reference_price is None:
            if allow_none:
                return None

            raise ValueError(
                "reference_price is required"
            )

        if not self._is_number(reference_price):
            raise TypeError(
                "reference_price must be numeric"
            )

        reference_price = float(reference_price)

        if reference_price <= 0:
            raise ValueError(
                "reference_price must be greater than zero"
            )

        return reference_price

    @staticmethod
    def _create_result() -> dict[str, Any]:
        return {
            "success": False,
            "plans": [],
            "errors": [],
            "processed": 0,
            "failed": 0,
        }

    def _validate_profile(
        self,
        profile: Any,
    ) -> list[str]:
        errors: list[str] = []

        if not isinstance(profile, dict):
            return [
                "profile must be a dictionary"
            ]

        required_keys = (
            "symbol",
            "capital",
            "layers",
            "take_profit",
            "spacing",
            "layer_capital",
        )

        for key in required_keys:
            if key not in profile:
                errors.append(
                    f"missing required field: {key}"
                )

        if errors:
            return errors

        symbol = profile["symbol"]

        if not isinstance(symbol, str):
            errors.append(
                "symbol must be a string"
            )
        elif not symbol.strip():
            errors.append(
                "symbol must not be empty"
            )

        capital = profile["capital"]

        if not self._is_number(capital):
            errors.append(
                "capital must be numeric"
            )
        elif float(capital) <= 0:
            errors.append(
                "capital must be greater than zero"
            )

        layers = profile["layers"]

        if (
            not isinstance(layers, int)
            or isinstance(layers, bool)
        ):
            errors.append(
                "layers must be an integer"
            )
        elif layers <= 0:
            errors.append(
                "layers must be greater than zero"
            )

        take_profit = profile["take_profit"]

        if not self._is_number(take_profit):
            errors.append(
                "take_profit must be numeric"
            )
        elif float(take_profit) <= 0:
            errors.append(
                "take_profit must be greater than zero"
            )

        spacing = profile["spacing"]

        if not isinstance(
            spacing,
            (list, tuple),
        ):
            errors.append(
                "spacing must be a list or tuple"
            )
        elif isinstance(layers, int) and not isinstance(
            layers,
            bool,
        ):
            expected_spacing_length = max(
                layers - 1,
                0,
            )

            if len(spacing) != expected_spacing_length:
                errors.append(
                    "spacing length must equal layers - 1"
                )

            for value in spacing:
                if not self._is_number(value):
                    errors.append(
                        "spacing values must be numeric"
                    )
                    break

                if float(value) <= 0:
                    errors.append(
                        "spacing values must be greater than zero"
                    )
                    break

        layer_capital = profile["layer_capital"]

        if not isinstance(
            layer_capital,
            (list, tuple),
        ):
            errors.append(
                "layer_capital must be a list or tuple"
            )
        elif isinstance(layers, int) and not isinstance(
            layers,
            bool,
        ):
            if len(layer_capital) != layers:
                errors.append(
                    "layer_capital length must equal layers"
                )

            for value in layer_capital:
                if not self._is_number(value):
                    errors.append(
                        "layer_capital values must be numeric"
                    )
                    break

                if float(value) <= 0:
                    errors.append(
                        "layer_capital values must be greater than zero"
                    )
                    break

        return errors

    @staticmethod
    def _build_entry_levels(
        reference_price: float,
        spacing: list[float],
        layers: int,
    ) -> list[float]:
        levels = [
            float(reference_price)
        ]

        current_price = float(reference_price)

        for spacing_value in spacing:
            current_price = (
                current_price
                * (1.0 - float(spacing_value))
            )

            levels.append(
                current_price
            )

        return levels[:layers]

    @staticmethod
    def _build_layer_plan(
        layer_index: int,
        entry_price: float,
        capital: float,
        take_profit: float,
    ) -> dict[str, Any]:
        take_profit_price = (
            entry_price
            * (1.0 + take_profit)
        )

        return {
            "layer": layer_index + 1,
            "entry_price": entry_price,
            "capital": capital,
            "take_profit": take_profit,
            "take_profit_price": take_profit_price,
        }

    def _build_plan(
        self,
        profile: dict[str, Any],
        reference_price: float,
    ) -> dict[str, Any]:
        profile_copy = deepcopy(profile)

        symbol = str(
            profile_copy["symbol"]
        ).strip().upper()

        capital = float(
            profile_copy["capital"]
        )

        layers = int(
            profile_copy["layers"]
        )

        take_profit = float(
            profile_copy["take_profit"]
        )

        spacing = [
            float(value)
            for value in profile_copy["spacing"]
        ]

        layer_capital = [
            float(value)
            for value in profile_copy["layer_capital"]
        ]

        entry_levels = self._build_entry_levels(
            reference_price=reference_price,
            spacing=spacing,
            layers=layers,
        )

        layer_plans = []

        for index in range(layers):
            layer_plan = self._build_layer_plan(
                layer_index=index,
                entry_price=entry_levels[index],
                capital=layer_capital[index],
                take_profit=take_profit,
            )

            layer_plans.append(
                layer_plan
            )

        return {
            "symbol": symbol,
            "reference_price": float(
                reference_price
            ),
            "capital": capital,
            "layers": layers,
            "take_profit": take_profit,
            "spacing": deepcopy(spacing),
            "layer_capital": deepcopy(
                layer_capital
            ),
            "entry_levels": deepcopy(
                entry_levels
            ),
            "layer_plans": deepcopy(
                layer_plans
            ),
            "profile": deepcopy(
                profile_copy
            ),
        }

    def run(
        self,
        profiles: Any,
        reference_price: float | None = None,
    ) -> dict[str, Any]:
        result = self._create_result()

        if profiles is None:
            result["errors"].append(
                {
                    "index": None,
                    "errors": [
                        "profiles must not be None"
                    ],
                }
            )
            result["failed"] = 1
            return result

        if isinstance(
            profiles,
            (str, bytes),
        ):
            result["errors"].append(
                {
                    "index": None,
                    "errors": [
                        "profiles must be a list or tuple"
                    ],
                }
            )
            result["failed"] = 1
            return result

        if not isinstance(
            profiles,
            (list, tuple),
        ):
            result["errors"].append(
                {
                    "index": None,
                    "errors": [
                        "profiles must be a list or tuple"
                    ],
                }
            )
            result["failed"] = 1
            return result

        try:
            resolved_reference_price = (
                self.default_reference_price
                if reference_price is None
                else self._validate_reference_price(
                    reference_price
                )
            )

            resolved_reference_price = (
                self._validate_reference_price(
                    resolved_reference_price
                )
            )

        except (
            TypeError,
            ValueError,
        ) as error:
            result["errors"].append(
                {
                    "index": None,
                    "errors": [
                        str(error)
                    ],
                }
            )

            result["failed"] = len(
                profiles
            )

            return result

        for index, profile in enumerate(
            profiles
        ):
            result["processed"] += 1

            errors = self._validate_profile(
                profile
            )

            if errors:
                result["errors"].append(
                    {
                        "index": index,
                        "errors": errors,
                    }
                )

                result["failed"] += 1

                continue

            try:
                plan = self._build_plan(
                    profile=profile,
                    reference_price=resolved_reference_price,
                )

                result["plans"].append(
                    deepcopy(plan)
                )

            except Exception as error:
                result["errors"].append(
                    {
                        "index": index,
                        "errors": [
                            str(error)
                        ],
                    }
                )

                result["failed"] += 1

        result["success"] = (
            result["processed"] > 0
            and len(result["plans"]) > 0
            and result["failed"] == 0
        )

        return deepcopy(result)

    def process(
        self,
        profiles: Any,
        reference_price: float | None = None,
    ) -> dict[str, Any]:
        return self.run(
            profiles=profiles,
            reference_price=reference_price,
        )

    def execute(
        self,
        profiles: Any,
        reference_price: float | None = None,
    ) -> dict[str, Any]:
        return self.run(
            profiles=profiles,
            reference_price=reference_price,
        )


def build_grid_execution_plans(
    profiles: Any,
    reference_price: float,
) -> dict[str, Any]:
    """
    Convenience function for building grid execution plans.
    """

    planner = GridExecutionPlanner()

    return planner.run(
        profiles=profiles,
        reference_price=reference_price,
    )