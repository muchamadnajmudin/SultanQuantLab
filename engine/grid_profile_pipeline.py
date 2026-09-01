"""
==========================================
SULTAN QUANT OS
Grid Profile Pipeline
Version : 1.0.0
==========================================

Responsibilities:

- Orchestrate GridProfileBuilder
- Orchestrate GridProfileValidator
- Orchestrate GridProfileSelector
- Preserve stable module contracts
- Preserve input immutability
- Return stable pipeline result contracts
"""

from copy import deepcopy
from typing import Any

from engine.grid_profile_builder import (
    GridProfileBuilder,
)
from engine.grid_profile_validator import (
    GridProfileValidator,
)
from engine.grid_profile_selector import (
    GridProfileSelector,
)


class GridProfilePipeline:
    """
    End-to-end pipeline for grid profile processing.

    Flow:

        Candidates
            ->
        GridProfileBuilder
            ->
        GridProfileValidator
            ->
        GridProfileSelector
            ->
        Selected Profiles
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    REQUIRED_RESULT_KEYS = (
        "status",
        "profiles",
        "validated_profiles",
        "selected_profiles",
        "processed_count",
        "failed_count",
        "selected_count",
        "errors",
        "input",
        "build_result",
        "validation_result",
        "selection_result",
    )

    def __init__(
        self,
        builder: GridProfileBuilder | None = None,
        validator: GridProfileValidator | None = None,
        selector: GridProfileSelector | None = None,
    ):
        self.builder = (
            builder
            if builder is not None
            else GridProfileBuilder()
        )

        self.validator = (
            validator
            if validator is not None
            else GridProfileValidator()
        )

        self.selector = (
            selector
            if selector is not None
            else GridProfileSelector()
        )

        self._validate_dependencies()

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def run(
        self,
        candidates: Any,
        top_n: int | None = None,
    ) -> dict:
        """
        Run the complete Grid Profile pipeline.
        """

        original_input = deepcopy(candidates)

        result = self._create_result(
            input_data=original_input,
        )

        # ------------------------------------------------------
        # BUILD
        # ------------------------------------------------------

        try:

            build_result = self.builder.run(
                deepcopy(candidates)
            )

        except Exception as exc:

            result["status"] = self.STATUS_ERROR

            result["errors"].append(
                {
                    "stage": "builder",
                    "error": str(exc),
                }
            )

            return deepcopy(result)

        result["build_result"] = deepcopy(
            build_result
        )

        profiles = deepcopy(
            build_result.get(
                "profiles",
                [],
            )
        )

        result["profiles"] = deepcopy(
            profiles
        )

        # ------------------------------------------------------
        # EMPTY BUILD RESULT
        # ------------------------------------------------------

        if not profiles:

            result["processed_count"] = 0

            build_status = build_result.get(
                "status"
            )

            if build_status == self.STATUS_EMPTY:

                result["status"] = (
                    self.STATUS_EMPTY
                )

            else:

                result["status"] = (
                    self.STATUS_ERROR
                )

            build_errors = build_result.get(
                "errors",
                [],
            )

            result["errors"] = deepcopy(
                build_errors
            )

            return deepcopy(result)

        # ------------------------------------------------------
        # VALIDATE
        # ------------------------------------------------------

        validated_profiles = []
        validation_errors = []

        for index, profile in enumerate(
            profiles
        ):

            try:

                validation_result = (
                    self.validator.validate(
                        deepcopy(profile)
                    )
                )

            except Exception as exc:

                validation_errors.append(
                    {
                        "stage": "validator",
                        "index": index,
                        "error": str(exc),
                    }
                )

                continue

            if self._is_valid_validation_result(
                validation_result
            ):

                validated_profile = (
                    self._extract_valid_profile(
                        validation_result,
                        profile,
                    )
                )

                validated_profiles.append(
                    deepcopy(validated_profile)
                )

            else:

                validation_errors.append(
                    {
                        "stage": "validator",
                        "index": index,
                        "errors": deepcopy(
                            validation_result.get(
                                "errors",
                                [],
                            )
                        ),
                    }
                )

        validation_result = {
            "status": self._resolve_stage_status(
                total_count=len(profiles),
                success_count=len(
                    validated_profiles
                ),
                failure_count=len(
                    validation_errors
                ),
            ),
            "profiles": deepcopy(
                validated_profiles
            ),
            "processed_count": len(
                validated_profiles
            ),
            "failed_count": len(
                validation_errors
            ),
            "errors": deepcopy(
                validation_errors
            ),
            "input": deepcopy(
                profiles
            ),
        }

        result["validation_result"] = deepcopy(
            validation_result
        )

        result["validated_profiles"] = deepcopy(
            validated_profiles
        )

        result["failed_count"] = len(
            validation_errors
        )

        # ------------------------------------------------------
        # NO VALID PROFILES
        # ------------------------------------------------------

        if not validated_profiles:

            result["processed_count"] = 0

            result["status"] = (
                self.STATUS_ERROR
                if validation_errors
                else self.STATUS_EMPTY
            )

            result["errors"].extend(
                deepcopy(validation_errors)
            )

            return deepcopy(result)

        # ------------------------------------------------------
        # SELECT
        # ------------------------------------------------------

        try:

            selection_result = (
                self.selector.run(
                    deepcopy(validated_profiles),
                    top_n=top_n,
                )
            )

        except Exception as exc:

            result["status"] = self.STATUS_ERROR

            result["processed_count"] = len(
                validated_profiles
            )

            result["errors"].extend(
                deepcopy(validation_errors)
            )

            result["errors"].append(
                {
                    "stage": "selector",
                    "error": str(exc),
                }
            )

            return deepcopy(result)

        result["selection_result"] = deepcopy(
            selection_result
        )

        selected_profiles = deepcopy(
            selection_result.get(
                "selected_profiles",
                [],
            )
        )

        result["selected_profiles"] = (
            selected_profiles
        )

        result["selected_count"] = len(
            selected_profiles
        )

        result["processed_count"] = len(
            validated_profiles
        )

        result["failed_count"] = len(
            validation_errors
        )

        result["errors"].extend(
            deepcopy(validation_errors)
        )

        # ------------------------------------------------------
        # FINAL STATUS
        # ------------------------------------------------------

        result["status"] = (
            self._resolve_final_status(
                processed_count=result[
                    "processed_count"
                ],
                failed_count=result[
                    "failed_count"
                ],
                selected_count=result[
                    "selected_count"
                ],
            )
        )

        return deepcopy(result)

    def process(
        self,
        candidates: Any,
        top_n: int | None = None,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            candidates,
            top_n=top_n,
        )

    def execute(
        self,
        candidates: Any,
        top_n: int | None = None,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(
            candidates,
            top_n=top_n,
        )

    # ==========================================================
    # DEPENDENCY VALIDATION
    # ==========================================================

    def _validate_dependencies(
        self,
    ) -> None:

        if not hasattr(
            self.builder,
            "run",
        ):
            raise TypeError(
                "builder must provide run()"
            )

        if not hasattr(
            self.validator,
            "validate",
        ):
            raise TypeError(
                "validator must provide validate()"
            )

        if not hasattr(
            self.selector,
            "run",
        ):
            raise TypeError(
                "selector must provide run()"
            )

    # ==========================================================
    # VALIDATION HELPERS
    # ==========================================================

    def _is_valid_validation_result(
        self,
        validation_result: Any,
    ) -> bool:

        if not isinstance(
            validation_result,
            dict,
        ):
            return False

        if validation_result.get(
            "status"
        ) == self.STATUS_SUCCESS:
            return True

        if validation_result.get(
            "valid"
        ) is True:
            return True

        if validation_result.get(
            "is_valid"
        ) is True:
            return True

        return False

    def _extract_valid_profile(
        self,
        validation_result: dict,
        original_profile: dict,
    ) -> dict:

        profile = validation_result.get(
            "profile"
        )

        if isinstance(
            profile,
            dict,
        ):
            return deepcopy(profile)

        profile = validation_result.get(
            "validated_profile"
        )

        if isinstance(
            profile,
            dict,
        ):
            return deepcopy(profile)

        return deepcopy(
            original_profile
        )

    # ==========================================================
    # STATUS HELPERS
    # ==========================================================

    def _resolve_stage_status(
        self,
        total_count: int,
        success_count: int,
        failure_count: int,
    ) -> str:

        if total_count == 0:
            return self.STATUS_EMPTY

        if success_count == 0:

            if failure_count > 0:
                return self.STATUS_ERROR

            return self.STATUS_EMPTY

        if failure_count > 0:
            return self.STATUS_PARTIAL

        return self.STATUS_SUCCESS

    def _resolve_final_status(
        self,
        processed_count: int,
        failed_count: int,
        selected_count: int,
    ) -> str:

        if processed_count == 0:

            if failed_count > 0:
                return self.STATUS_ERROR

            return self.STATUS_EMPTY

        if selected_count == 0:

            if failed_count > 0:
                return self.STATUS_PARTIAL

            return self.STATUS_EMPTY

        if failed_count > 0:
            return self.STATUS_PARTIAL

        return self.STATUS_SUCCESS

    # ==========================================================
    # RESULT CONTRACT
    # ==========================================================

    def _create_result(
        self,
        input_data: Any,
    ) -> dict:

        return {
            "status": self.STATUS_EMPTY,
            "profiles": [],
            "validated_profiles": [],
            "selected_profiles": [],
            "processed_count": 0,
            "failed_count": 0,
            "selected_count": 0,
            "errors": [],
            "input": deepcopy(
                input_data
            ),
            "build_result": {},
            "validation_result": {},
            "selection_result": {},
        }


# ==============================================================
# FUNCTION API
# ==============================================================

def run_grid_profile_pipeline(
    candidates: Any,
    top_n: int | None = None,
    **kwargs,
) -> dict:
    """
    Convenience function for running the complete
    Grid Profile pipeline.
    """

    pipeline = GridProfilePipeline(
        **kwargs
    )

    return pipeline.run(
        candidates,
        top_n=top_n,
    )