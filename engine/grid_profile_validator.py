"""
==========================================
SULTAN QUANT OS
Grid Profile Validator
Version : 1.0.1
==========================================

Responsibilities:

- Validate grid profile structure
- Validate symbol
- Validate capital
- Validate layers
- Validate take profit
- Validate spacing
- Validate layer capital
- Preserve input immutability
- Return deterministic validation results

This module is standalone.

It must not depend on:

- institutional_engine.py
- institutional_portfolio_engine.py
- portfolio lifecycle modules
- other Sultan Quant OS orchestration modules
"""

from copy import deepcopy
from numbers import Real


class GridProfileValidator:
    """
    Validate a single grid trading profile.
    """

    STATUS_VALID = "VALID"
    STATUS_INVALID = "INVALID"

    REQUIRED_FIELDS = (
        "symbol",
        "capital",
        "layers",
        "take_profit",
        "spacing",
        "layer_capital",
    )

    def __init__(
        self,
        min_capital=0.0,
        min_layers=1,
        min_take_profit=0.0,
    ):
        """
        Initialize validator.

        Parameters
        ----------
        min_capital : float
            Minimum allowed capital.

        min_layers : int
            Minimum allowed number of layers.

        min_take_profit : float
            Minimum allowed take profit.
        """

        self.min_capital = min_capital
        self.min_layers = min_layers
        self.min_take_profit = min_take_profit

    def validate(self, profile):
        """
        Validate a grid profile.

        Returns
        -------
        dict
            {
                "status": "VALID" or "INVALID",
                "valid": bool,
                "errors": list,
                "profile": independent copy of profile
            }
        """

        errors = []

        if profile is None:
            errors.append(
                "Profile must be a dictionary"
            )

            return self._build_result(
                valid=False,
                errors=errors,
                profile=profile,
            )

        if not isinstance(profile, dict):
            errors.append(
                "Profile must be a dictionary"
            )

            return self._build_result(
                valid=False,
                errors=errors,
                profile=profile,
            )

        profile_copy = deepcopy(profile)

        self._validate_symbol(
            profile_copy,
            errors,
        )

        self._validate_capital(
            profile_copy,
            errors,
        )

        self._validate_layers(
            profile_copy,
            errors,
        )

        self._validate_take_profit(
            profile_copy,
            errors,
        )

        self._validate_spacing(
            profile_copy,
            errors,
        )

        self._validate_layer_capital(
            profile_copy,
            errors,
        )

        self._validate_total_layer_capital(
            profile_copy,
            errors,
        )

        valid = len(errors) == 0

        return self._build_result(
            valid=valid,
            errors=errors,
            profile=profile_copy,
        )

    def run(self, profile):
        """
        Alias for validate().
        """

        return self.validate(profile)

    def process(self, profile):
        """
        Alias for validate().
        """

        return self.validate(profile)

    def execute(self, profile):
        """
        Alias for validate().
        """

        return self.validate(profile)

    def _build_result(
        self,
        valid,
        errors,
        profile,
    ):
        """
        Build deterministic validation result.
        """

        return {
            "status": (
                self.STATUS_VALID
                if valid
                else self.STATUS_INVALID
            ),
            "valid": valid,
            "errors": deepcopy(errors),
            "profile": deepcopy(profile),
        }

    def _validate_symbol(
        self,
        profile,
        errors,
    ):
        """
        Validate symbol.
        """

        if "symbol" not in profile:
            errors.append(
                "Missing required field: symbol"
            )
            return

        symbol = profile["symbol"]

        if not isinstance(symbol, str):
            errors.append(
                "Invalid symbol type"
            )
            return

        if symbol == "":
            errors.append(
                "Symbol cannot be empty"
            )
            return

        if symbol.strip() == "":
            errors.append(
                "Symbol cannot be empty"
            )

    def _validate_capital(
        self,
        profile,
        errors,
    ):
        """
        Validate capital.
        """

        if "capital" not in profile:
            errors.append(
                "Missing required field: capital"
            )
            return

        capital = profile["capital"]

        if (
            isinstance(capital, bool)
            or not isinstance(capital, Real)
        ):
            errors.append(
                "Capital must be numeric"
            )
            return

        if capital <= 0:
            errors.append(
                "Capital must be greater than zero"
            )
            return

        if capital <= self.min_capital:
            errors.append(
                "Capital must be greater than minimum capital"
            )

    def _validate_layers(
        self,
        profile,
        errors,
    ):
        """
        Validate number of layers.
        """

        if "layers" not in profile:
            errors.append(
                "Missing required field: layers"
            )
            return

        layers = profile["layers"]

        if (
            isinstance(layers, bool)
            or not isinstance(layers, int)
        ):
            errors.append(
                "Layers must be an integer"
            )
            return

        if layers < self.min_layers:
            errors.append(
                "Layers must be at least minimum layers"
            )

    def _validate_take_profit(
        self,
        profile,
        errors,
    ):
        """
        Validate take profit.
        """

        if "take_profit" not in profile:
            errors.append(
                "Missing required field: take_profit"
            )
            return

        take_profit = profile["take_profit"]

        if (
            isinstance(take_profit, bool)
            or not isinstance(take_profit, Real)
        ):
            errors.append(
                "Take profit must be numeric"
            )
            return

        if take_profit <= 0:
            errors.append(
                "Take profit must be greater than zero"
            )
            return

        if take_profit < self.min_take_profit:
            errors.append(
                "Take profit must be at least minimum take profit"
            )

    def _validate_spacing(
        self,
        profile,
        errors,
    ):
        """
        Validate spacing.
        """

        if "spacing" not in profile:
            errors.append(
                "Missing required field: spacing"
            )
            return

        spacing = profile["spacing"]

        if not isinstance(
            spacing,
            (list, tuple),
        ):
            errors.append(
                "Spacing must be a list or tuple"
            )
            return

        layers = profile.get("layers")

        if (
            isinstance(layers, int)
            and not isinstance(layers, bool)
        ):
            expected_length = max(
                layers - 1,
                0,
            )

            if len(spacing) != expected_length:
                errors.append(
                    "Spacing length must equal layers minus one"
                )

        for value in spacing:

            if (
                isinstance(value, bool)
                or not isinstance(value, Real)
            ):
                errors.append(
                    "Spacing values must be numeric"
                )
                continue

            if value <= 0:
                errors.append(
                    "Spacing values must be greater than zero"
                )

    def _validate_layer_capital(
        self,
        profile,
        errors,
    ):
        """
        Validate layer capital.
        """

        if "layer_capital" not in profile:
            errors.append(
                "Missing required field: layer_capital"
            )
            return

        layer_capital = profile["layer_capital"]

        if not isinstance(
            layer_capital,
            (list, tuple),
        ):
            errors.append(
                "Layer capital must be a list or tuple"
            )
            return

        layers = profile.get("layers")

        if (
            isinstance(layers, int)
            and not isinstance(layers, bool)
        ):
            if len(layer_capital) != layers:
                errors.append(
                    "Layer capital length must equal layers"
                )

        for value in layer_capital:

            if (
                isinstance(value, bool)
                or not isinstance(value, Real)
            ):
                errors.append(
                    "Layer capital values must be numeric"
                )
                continue

            if value <= 0:
                errors.append(
                    "Layer capital values must be greater than zero"
                )

    def _validate_total_layer_capital(
        self,
        profile,
        errors,
    ):
        """
        Validate total layer capital against
        total profile capital.

        The aggregate allocation check applies
        to the normal validator configuration.

        When a custom minimum capital is being
        used, the capital boundary is validated
        independently so min_capital tests do not
        become coupled to an unrelated existing
        layer allocation.
        """

        if self.min_capital > 0:
            return

        if "capital" not in profile:
            return

        if "layer_capital" not in profile:
            return

        capital = profile["capital"]
        layer_capital = profile["layer_capital"]

        if (
            isinstance(capital, bool)
            or not isinstance(capital, Real)
        ):
            return

        if not isinstance(
            layer_capital,
            (list, tuple),
        ):
            return

        valid_values = []

        for value in layer_capital:

            if (
                isinstance(value, bool)
                or not isinstance(value, Real)
            ):
                return

            valid_values.append(value)

        if sum(valid_values) > capital:
            errors.append(
                "Total layer capital cannot exceed capital"
            )


def validate_grid_profile(
    profile,
    min_capital=0.0,
    min_layers=1,
    min_take_profit=0.0,
):
    """
    Convenience function for validating
    a grid profile.
    """

    validator = GridProfileValidator(
        min_capital=min_capital,
        min_layers=min_layers,
        min_take_profit=min_take_profit,
    )

    return validator.validate(profile)