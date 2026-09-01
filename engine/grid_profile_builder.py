"""
==========================================
SULTAN QUANT OS
Grid Profile Builder
Version : 1.0.1
==========================================

Responsibilities:

- Build GridProfile-compatible dictionaries from grid candidates
- Normalize symbols
- Support candidate aliases
- Create default spacing
- Use volatility when available
- Allocate capital equally by default
- Preserve input immutability
- Return stable result contracts
- Produce profiles compatible with GridProfileValidator
"""

from copy import deepcopy
from typing import Any


class GridProfileBuilder:
    """
    Build grid profiles from candidate dictionaries.

    The builder intentionally returns dictionaries instead of exposing
    mutable internal state so that the output contract can safely be used
    by candidate pipelines, ranking engines, and future portfolio layers.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    REQUIRED_RESULT_KEYS = (
        "status",
        "profiles",
        "processed_count",
        "failed_count",
        "input",
        "errors",
    )

    def __init__(
        self,
        default_capital: float = 1000.0,
        default_layers: int = 5,
        default_take_profit: float = 0.02,
        default_spacing: float = 0.01,
    ):
        """
        Initialize GridProfileBuilder.
        """

        self.default_capital = float(
            default_capital
        )

        self.default_layers = int(
            default_layers
        )

        self.default_take_profit = float(
            default_take_profit
        )

        self.default_spacing = float(
            default_spacing
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def run(
        self,
        candidates: Any,
    ) -> dict:
        """
        Build grid profiles from candidates.
        """

        original_input = deepcopy(
            candidates
        )

        result = self._create_result(
            input_data=original_input,
        )

        # ------------------------------------------------------
        # Empty input
        # ------------------------------------------------------

        if candidates is None:
            result["status"] = (
                self.STATUS_EMPTY
            )

            return deepcopy(
                result
            )

        # ------------------------------------------------------
        # Candidate container validation
        # ------------------------------------------------------

        if isinstance(
            candidates,
            str,
        ):
            result["status"] = (
                self.STATUS_ERROR
            )

            result["errors"].append(
                "candidates must be a list"
            )

            return deepcopy(
                result
            )

        if not isinstance(
            candidates,
            (list, tuple),
        ):
            result["status"] = (
                self.STATUS_ERROR
            )

            result["errors"].append(
                "candidates must be a list or tuple"
            )

            return deepcopy(
                result
            )

        if len(candidates) == 0:
            result["status"] = (
                self.STATUS_EMPTY
            )

            return deepcopy(
                result
            )

        profiles = []
        errors = []

        # ------------------------------------------------------
        # Process candidates
        # ------------------------------------------------------

        for index, candidate in enumerate(
            candidates
        ):

            try:

                profile = self._build_profile(
                    candidate
                )

                profiles.append(
                    deepcopy(profile)
                )

            except Exception as exc:

                errors.append(
                    {
                        "index": index,
                        "error": str(exc),
                    }
                )

        result["profiles"] = deepcopy(
            profiles
        )

        result["processed_count"] = len(
            profiles
        )

        result["failed_count"] = len(
            errors
        )

        result["errors"] = deepcopy(
            errors
        )

        # ------------------------------------------------------
        # Final status
        # ------------------------------------------------------

        if len(profiles) == 0:

            if len(errors) == 0:

                result["status"] = (
                    self.STATUS_EMPTY
                )

            else:

                result["status"] = (
                    self.STATUS_ERROR
                )

        elif len(errors) > 0:

            result["status"] = (
                self.STATUS_PARTIAL
            )

        else:

            result["status"] = (
                self.STATUS_SUCCESS
            )

        return deepcopy(
            result
        )

    def process(
        self,
        candidates: Any,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            candidates
        )

    def execute(
        self,
        candidates: Any,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            candidates
        )

    # ==========================================================
    # PROFILE BUILDER
    # ==========================================================

    def _build_profile(
        self,
        candidate: Any,
    ) -> dict:
        """
        Build a single GridProfile-compatible dictionary.
        """

        if not isinstance(
            candidate,
            dict,
        ):
            raise ValueError(
                "candidate must be a dictionary"
            )

        candidate_copy = deepcopy(
            candidate
        )

        symbol = self._resolve_symbol(
            candidate_copy
        )

        capital = self._resolve_capital(
            candidate_copy
        )

        layers = self._resolve_layers(
            candidate_copy
        )

        take_profit = (
            self._resolve_take_profit(
                candidate_copy
            )
        )

        spacing = self._resolve_spacing(
            candidate_copy,
            layers,
        )

        layer_capital = (
            self._resolve_layer_capital(
                candidate_copy,
                capital,
                layers,
            )
        )

        profile = {
            "symbol": symbol,
            "capital": capital,
            "total_capital": capital,
            "layers": layers,
            "spacing": spacing,
            "take_profit": take_profit,
            "layer_capital": layer_capital,
            "candidate": deepcopy(
                candidate_copy
            ),
        }

        return deepcopy(
            profile
        )

    # ==========================================================
    # SYMBOL
    # ==========================================================

    def _resolve_symbol(
        self,
        candidate: dict,
    ) -> str:
        """
        Resolve and normalize symbol.
        """

        symbol = candidate.get(
            "symbol"
        )

        if not isinstance(
            symbol,
            str,
        ):
            raise ValueError(
                "candidate symbol must be a string"
            )

        symbol = symbol.strip()

        if not symbol:
            raise ValueError(
                "candidate symbol cannot be empty"
            )

        symbol = (
            symbol
            .upper()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        if not symbol:
            raise ValueError(
                "candidate symbol cannot be empty"
            )

        return symbol

    # ==========================================================
    # CAPITAL
    # ==========================================================

    def _resolve_capital(
        self,
        candidate: dict,
    ) -> float:
        """
        Resolve capital using supported aliases.
        """

        value = candidate.get(
            "capital",
            candidate.get(
                "total_capital",
                self.default_capital,
            ),
        )

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "capital must be numeric"
            )

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "capital must be numeric"
            )

        if value <= 0:

            raise ValueError(
                "capital must be greater than zero"
            )

        return value

    # ==========================================================
    # LAYERS
    # ==========================================================

    def _resolve_layers(
        self,
        candidate: dict,
    ) -> int:
        """
        Resolve layer count using supported aliases.
        """

        value = candidate.get(
            "layers",
            candidate.get(
                "grid_layers",
                self.default_layers,
            ),
        )

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "layers must be an integer"
            )

        try:

            numeric_value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "layers must be an integer"
            )

        if not numeric_value.is_integer():

            raise ValueError(
                "layers must be an integer"
            )

        layers = int(
            numeric_value
        )

        if layers <= 0:

            raise ValueError(
                "layers must be greater than zero"
            )

        return layers

    # ==========================================================
    # TAKE PROFIT
    # ==========================================================

    def _resolve_take_profit(
        self,
        candidate: dict,
    ) -> float:
        """
        Resolve take profit using supported aliases.
        """

        value = candidate.get(
            "take_profit",
            candidate.get(
                "tp",
                self.default_take_profit,
            ),
        )

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                "take_profit must be numeric"
            )

        try:

            value = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "take_profit must be numeric"
            )

        if value <= 0:

            raise ValueError(
                "take_profit must be greater than zero"
            )

        return value

    # ==========================================================
    # SPACING
    # ==========================================================

    def _resolve_spacing(
        self,
        candidate: dict,
        layers: int,
    ) -> list:
        """
        Resolve grid spacing.
        """

        value = candidate.get(
            "spacing"
        )

        # ------------------------------------------------------
        # One layer
        # ------------------------------------------------------

        if layers == 1:

            if value not in (
                None,
                [],
                (),
            ):

                raise ValueError(
                    "one layer profile cannot have spacing"
                )

            return []

        expected_length = (
            layers - 1
        )

        # ------------------------------------------------------
        # Explicit spacing
        # ------------------------------------------------------

        if value is not None:

            if not isinstance(
                value,
                (list, tuple),
            ):

                raise ValueError(
                    "spacing must be a list"
                )

            spacing = []

            for item in value:

                if isinstance(
                    item,
                    bool,
                ):

                    raise ValueError(
                        "spacing values must be numeric"
                    )

                try:

                    numeric_item = float(
                        item
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    raise ValueError(
                        "spacing values must be numeric"
                    )

                if numeric_item <= 0:

                    raise ValueError(
                        "spacing values must be greater than zero"
                    )

                spacing.append(
                    numeric_item
                )

            if len(spacing) != (
                expected_length
            ):

                raise ValueError(
                    "spacing length must equal "
                    "layers minus one"
                )

            return spacing

        # ------------------------------------------------------
        # Volatility based spacing
        # ------------------------------------------------------

        volatility = candidate.get(
            "volatility"
        )

        if volatility is not None:

            if isinstance(
                volatility,
                bool,
            ):

                raise ValueError(
                    "volatility must be numeric"
                )

            try:

                volatility = float(
                    volatility
                )

            except (
                TypeError,
                ValueError,
            ):

                raise ValueError(
                    "volatility must be numeric"
                )

            if volatility <= 0:

                raise ValueError(
                    "volatility must be greater than zero"
                )

            return [
                volatility
                for _ in range(
                    expected_length
                )
            ]

        # ------------------------------------------------------
        # Default spacing
        # ------------------------------------------------------

        if isinstance(
            self.default_spacing,
            bool,
        ):

            raise ValueError(
                "default spacing must be numeric"
            )

        try:

            default_spacing = float(
                self.default_spacing
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                "default spacing must be numeric"
            )

        if default_spacing <= 0:

            raise ValueError(
                "default spacing must be greater than zero"
            )

        return [
            default_spacing
            for _ in range(
                expected_length
            )
        ]

    # ==========================================================
    # LAYER CAPITAL
    # ==========================================================

    def _resolve_layer_capital(
        self,
        candidate: dict,
        capital: float,
        layers: int,
    ) -> list:
        """
        Resolve capital allocation for each layer.

        Every layer capital must be strictly greater than zero
        to remain compatible with GridProfileValidator.
        """

        value = candidate.get(
            "layer_capital"
        )

        # ------------------------------------------------------
        # Custom allocation
        # ------------------------------------------------------

        if value is not None:

            if not isinstance(
                value,
                (list, tuple),
            ):

                raise ValueError(
                    "layer_capital must be a list"
                )

            if len(value) != layers:

                raise ValueError(
                    "layer_capital length must equal layers"
                )

            allocation = []

            for item in value:

                if isinstance(
                    item,
                    bool,
                ):

                    raise ValueError(
                        "layer_capital values must be numeric"
                    )

                try:

                    numeric_item = float(
                        item
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    raise ValueError(
                        "layer_capital values must be numeric"
                    )

                # --------------------------------------------------
                # Strictly positive.
                #
                # GridProfileValidator requires:
                # layer capital > 0
                # --------------------------------------------------

                if numeric_item <= 0:

                    raise ValueError(
                        "layer_capital values must be "
                        "greater than zero"
                    )

                allocation.append(
                    numeric_item
                )

            if sum(allocation) > capital:

                raise ValueError(
                    "layer_capital exceeds total capital"
                )

            return allocation

        # ------------------------------------------------------
        # Equal allocation
        # ------------------------------------------------------

        allocation = capital / layers

        if allocation <= 0:

            raise ValueError(
                "layer_capital values must be "
                "greater than zero"
            )

        return [
            allocation
            for _ in range(
                layers
            )
        ]

    # ==========================================================
    # RESULT CONTRACT
    # ==========================================================

    def _create_result(
        self,
        input_data: Any,
    ) -> dict:
        """
        Create deterministic result structure.
        """

        return {
            "status": self.STATUS_EMPTY,
            "profiles": [],
            "processed_count": 0,
            "failed_count": 0,
            "input": deepcopy(
                input_data
            ),
            "errors": [],
        }


# ==============================================================
# FUNCTION API
# ==============================================================

def build_grid_profiles(
    candidates: Any,
    **kwargs,
) -> dict:
    """
    Convenience function for building grid profiles.
    """

    builder = GridProfileBuilder(
        **kwargs
    )

    return builder.run(
        candidates
    )