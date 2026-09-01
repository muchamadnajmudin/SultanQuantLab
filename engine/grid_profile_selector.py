"""
==========================================
SULTAN QUANT OS
Grid Profile Selector
Version : 1.0.0
==========================================

Responsibilities:

- Accept multiple grid profiles
- Validate grid profiles
- Separate valid and invalid profiles
- Rank valid profiles
- Select top profiles
- Support top_n selection
- Preserve input immutability
- Return deterministic result contracts

This module depends only on:

- engine.grid_profile_validator

It must not depend on:

- institutional_engine.py
- institutional_portfolio_engine.py
- portfolio lifecycle modules
- other Sultan Quant OS orchestration modules
"""

from copy import deepcopy
from numbers import Real
from typing import Any

from engine.grid_profile_validator import (
    GridProfileValidator,
)


class GridProfileSelector:
    """
    Validate, rank, and select grid profiles.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    REQUIRED_RESULT_KEYS = (
        "status",
        "selected_profiles",
        "ranked_profiles",
        "valid_profiles",
        "invalid_profiles",
        "processed_count",
        "valid_count",
        "invalid_count",
        "selected_count",
        "input",
        "errors",
    )

    def __init__(
        self,
        top_n=None,
        validator=None,
    ):
        """
        Initialize selector.

        Parameters
        ----------
        top_n : int or None
            Maximum number of profiles to select.
            None means select all valid profiles.

        validator : GridProfileValidator or None
            Optional validator instance.
        """

        self.top_n = self._validate_top_n(
            top_n
        )

        if validator is None:

            validator = GridProfileValidator()

        if not isinstance(
            validator,
            GridProfileValidator,
        ):
            raise TypeError(
                "validator must be a GridProfileValidator"
            )

        self.validator = validator

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def run(
        self,
        profiles: Any,
        top_n=None,
    ) -> dict:
        """
        Validate, rank, and select grid profiles.
        """

        original_input = deepcopy(
            profiles
        )

        result = self._create_result(
            input_data=original_input,
        )

        if profiles is None:

            result["status"] = self.STATUS_EMPTY

            return deepcopy(result)

        if isinstance(
            profiles,
            str,
        ):

            result["status"] = self.STATUS_ERROR

            result["errors"].append(
                "profiles must be a list or tuple"
            )

            return deepcopy(result)

        if not isinstance(
            profiles,
            (list, tuple),
        ):

            result["status"] = self.STATUS_ERROR

            result["errors"].append(
                "profiles must be a list or tuple"
            )

            return deepcopy(result)

        if len(profiles) == 0:

            result["status"] = self.STATUS_EMPTY

            return deepcopy(result)

        selection_top_n = self._resolve_top_n(
            top_n
        )

        valid_profiles = []
        invalid_profiles = []
        errors = []

        for index, profile in enumerate(
            profiles
        ):

            validation_result = (
                self.validator.validate(
                    profile
                )
            )

            if validation_result["valid"]:

                valid_profiles.append(
                    deepcopy(
                        validation_result[
                            "profile"
                        ]
                    )
                )

            else:

                invalid_entry = {
                    "index": index,
                    "profile": deepcopy(
                        validation_result[
                            "profile"
                        ]
                    ),
                    "errors": deepcopy(
                        validation_result[
                            "errors"
                        ]
                    ),
                }

                invalid_profiles.append(
                    invalid_entry
                )

                errors.append(
                    deepcopy(
                        invalid_entry
                    )
                )

        ranked_profiles = self._rank_profiles(
            valid_profiles
        )

        selected_profiles = (
            self._select_profiles(
                ranked_profiles,
                selection_top_n,
            )
        )

        result["valid_profiles"] = (
            deepcopy(valid_profiles)
        )

        result["invalid_profiles"] = (
            deepcopy(invalid_profiles)
        )

        result["ranked_profiles"] = (
            deepcopy(ranked_profiles)
        )

        result["selected_profiles"] = (
            deepcopy(selected_profiles)
        )

        result["processed_count"] = len(
            profiles
        )

        result["valid_count"] = len(
            valid_profiles
        )

        result["invalid_count"] = len(
            invalid_profiles
        )

        result["selected_count"] = len(
            selected_profiles
        )

        result["errors"] = deepcopy(
            errors
        )

        result["status"] = (
            self._resolve_status(
                valid_count=len(
                    valid_profiles
                ),
                invalid_count=len(
                    invalid_profiles
                ),
            )
        )

        return deepcopy(result)

    def process(
        self,
        profiles: Any,
        top_n=None,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            profiles,
            top_n=top_n,
        )

    def execute(
        self,
        profiles: Any,
        top_n=None,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            profiles,
            top_n=top_n,
        )

    # ==========================================================
    # TOP N
    # ==========================================================

    def _validate_top_n(
        self,
        top_n,
    ):

        if top_n is None:

            return None

        if isinstance(
            top_n,
            bool,
        ):

            raise ValueError(
                "top_n must be an integer"
            )

        if not isinstance(
            top_n,
            int,
        ):

            raise ValueError(
                "top_n must be an integer"
            )

        if top_n <= 0:

            raise ValueError(
                "top_n must be greater than zero"
            )

        return top_n

    def _resolve_top_n(
        self,
        top_n,
    ):

        if top_n is None:

            return self.top_n

        return self._validate_top_n(
            top_n
        )

    # ==========================================================
    # RANKING
    # ==========================================================

    def _rank_profiles(
        self,
        profiles,
    ):
        """
        Rank valid profiles deterministically.

        Ranking priority:

        1. Higher take_profit
        2. Higher capital
        3. Fewer layers
        4. Alphabetical symbol
        """

        indexed_profiles = []

        for index, profile in enumerate(
            profiles
        ):

            indexed_profiles.append(
                (
                    self._build_rank_key(
                        profile,
                        index,
                    ),
                    deepcopy(profile),
                )
            )

        indexed_profiles.sort(
            key=lambda item: item[0]
        )

        ranked_profiles = []

        for rank, (
            _,
            profile,
        ) in enumerate(
            indexed_profiles,
            start=1,
        ):

            ranked_profile = deepcopy(
                profile
            )

            ranked_profile["rank"] = rank

            ranked_profiles.append(
                ranked_profile
            )

        return ranked_profiles

    def _build_rank_key(
        self,
        profile,
        index,
    ):
        """
        Build deterministic ranking key.

        The validator guarantees the required
        values are valid before this method is used.
        """

        take_profit = profile[
            "take_profit"
        ]

        capital = profile[
            "capital"
        ]

        layers = profile[
            "layers"
        ]

        symbol = profile[
            "symbol"
        ]

        return (
            -float(take_profit),
            -float(capital),
            int(layers),
            str(symbol),
            index,
        )

    # ==========================================================
    # SELECTION
    # ==========================================================

    def _select_profiles(
        self,
        ranked_profiles,
        top_n,
    ):

        if top_n is None:

            return deepcopy(
                ranked_profiles
            )

        return deepcopy(
            ranked_profiles[:top_n]
        )

    # ==========================================================
    # STATUS
    # ==========================================================

    def _resolve_status(
        self,
        valid_count,
        invalid_count,
    ):

        if valid_count == 0:

            if invalid_count == 0:

                return self.STATUS_EMPTY

            return self.STATUS_ERROR

        if invalid_count > 0:

            return self.STATUS_PARTIAL

        return self.STATUS_SUCCESS

    # ==========================================================
    # RESULT CONTRACT
    # ==========================================================

    def _create_result(
        self,
        input_data,
    ) -> dict:

        return {
            "status": self.STATUS_EMPTY,
            "selected_profiles": [],
            "ranked_profiles": [],
            "valid_profiles": [],
            "invalid_profiles": [],
            "processed_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "selected_count": 0,
            "input": deepcopy(
                input_data
            ),
            "errors": [],
        }


# ==============================================================
# FUNCTION API
# ==============================================================

def select_grid_profiles(
    profiles,
    top_n=None,
    validator=None,
):
    """
    Convenience function for selecting
    grid profiles.
    """

    selector = GridProfileSelector(
        top_n=top_n,
        validator=validator,
    )

    return selector.run(
        profiles
    )