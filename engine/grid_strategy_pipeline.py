"""
==========================================
SULTAN QUANT OS
Module : Grid Strategy Pipeline
Version : 1.0.0
==========================================

Responsibilities
----------------
- Orchestrate Grid Strategy Ranker.
- Orchestrate Grid Strategy Selector.
- Forward performance/risk weights to the ranker.
- Forward top_n to the selector.
- Preserve ranker and selector outputs.
- Support partial failures.
- Preserve input immutability.
- Return independent result objects.
- Provide backward-compatible aliases:
    run()
    process()
    execute()

Pipeline
--------
Input
  |
  v
Grid Strategy Ranker
  |
  v
Ranked Strategies
  |
  v
Grid Strategy Selector
  |
  v
Selected Strategies

This module does NOT:
- execute trades
- modify grid plans
- perform backtesting
- calculate raw performance metrics
- calculate raw risk metrics
- place live orders
- connect to exchanges
"""

from __future__ import annotations

from copy import deepcopy
from numbers import Real
from typing import Any, Dict, Iterable


# ============================================================
# VERSION
# ============================================================

VERSION = "1.0.0"


# ============================================================
# STATUS
# ============================================================

STATUS_SUCCESS = "SUCCESS"
STATUS_PARTIAL = "PARTIAL"
STATUS_EMPTY = "EMPTY"
STATUS_ERROR = "ERROR"


# ============================================================
# DEFAULT CONFIGURATION
# ============================================================

DEFAULT_PERFORMANCE_WEIGHT = 0.60
DEFAULT_RISK_WEIGHT = 0.40
DEFAULT_TOP_N = 1


# ============================================================
# REQUIRED RESULT CONTRACT
# ============================================================

REQUIRED_RESULT_KEYS = {
    "success",
    "status",
    "processed_count",
    "valid_count",
    "invalid_count",
    "ranked_strategies",
    "selected_strategies",
    "ranked_count",
    "selected_count",
    "ranking",
    "selection",
    "invalid_strategies",
    "errors",
    "input",
}


# ============================================================
# SAFE HELPERS
# ============================================================

def _is_number(value: Any) -> bool:
    """
    Return True when value is numeric but not boolean.
    """

    return (
        isinstance(value, Real)
        and not isinstance(value, bool)
    )


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convert a value to float safely.
    """

    if not _is_number(value):
        return default

    try:
        return float(value)
    except (
        TypeError,
        ValueError,
    ):
        return default


def _safe_dict(
    value: Any,
) -> Dict[str, Any]:
    """
    Return an independent dictionary copy.

    Non-dictionary values become an empty dictionary.
    """

    if isinstance(value, dict):
        return deepcopy(value)

    return {}


def _safe_list(
    value: Any,
):
    """
    Return an independent list copy.

    Non-list/tuple values become an empty list.
    """

    if isinstance(
        value,
        (list, tuple),
    ):
        return deepcopy(
            list(value)
        )

    return []


def _normalize_symbol(
    value: Any,
) -> str:
    """
    Normalize strategy symbols.
    """

    if not isinstance(
        value,
        str,
    ):
        return ""

    return value.strip().upper()


# ============================================================
# INPUT SNAPSHOT
# ============================================================

def _snapshot_input(
    simulations: Any,
):
    """
    Create an independent input snapshot.

    This helper intentionally does not mutate the source.
    """

    try:
        return deepcopy(
            simulations
        )
    except Exception:
        return simulations


# ============================================================
# CONTAINER VALIDATION
# ============================================================

def _is_invalid_container(
    simulations: Any,
) -> bool:
    """
    Return True when the simulation container is invalid.
    """

    return isinstance(
        simulations,
        (str, bytes),
    )


def _to_items(
    simulations: Any,
):
    """
    Safely convert an iterable to a list.
    """

    try:
        return list(simulations)
    except (
        TypeError,
        ValueError,
    ):
        return None


# ============================================================
# INPUT INTEGRITY
# ============================================================

def _strategy_has_analysis_data(
    strategy: Any,
) -> bool:
    """
    Determine whether a strategy contains usable
    analysis/performance/risk information.

    Official Grid Strategy Ranker records contain analysis,
    performance and risk information.

    A strategy is considered structurally complete when
    at least one of those supported data containers exists.

    This keeps compatibility with the current Ranker contract
    while allowing incomplete records to be detected by the
    pipeline.
    """

    if not isinstance(
        strategy,
        dict,
    ):
        return False

    performance = strategy.get(
        "performance"
    )

    risk = strategy.get(
        "risk"
    )

    analysis = strategy.get(
        "analysis"
    )

    return (
        isinstance(
            performance,
            dict,
        )
        or isinstance(
            risk,
            dict,
        )
        or isinstance(
            analysis,
            dict,
        )
    )


def _is_structurally_invalid_strategy(
    strategy: Any,
) -> bool:
    """
    Determine whether a strategy record is structurally
    invalid at pipeline level.

    Rules
    -----
    1. Strategy must be a dictionary.
    2. Strategy must have a non-empty symbol.
    3. Strategy must contain analysis/performance/risk data.

    This deliberately handles records such as:

        {
            "symbol": "INVALID"
        }

    as invalid pipeline candidates.
    """

    if not isinstance(
        strategy,
        dict,
    ):
        return True

    symbol = strategy.get(
        "symbol"
    )

    if not isinstance(
        symbol,
        str,
    ):
        return True

    if not symbol.strip():
        return True

    if not _strategy_has_analysis_data(
        strategy
    ):
        return True

    return False


def _split_pipeline_inputs(
    simulations: Any,
):
    """
    Split raw input into structurally valid and invalid records.

    Returns
    -------
    tuple
        (
            valid_items,
            invalid_entries,
        )

    Important
    ---------
    This function does not modify the original input.
    """

    valid_items = []
    invalid_entries = []

    if simulations is None:
        return (
            valid_items,
            invalid_entries,
        )

    items = _to_items(
        simulations
    )

    if items is None:
        return (
            valid_items,
            invalid_entries,
        )

    for index, strategy in enumerate(
        items
    ):

        if _is_structurally_invalid_strategy(
            strategy
        ):

            invalid_entries.append(
                _build_invalid_entry(
                    strategy,
                    index,
                )
            )

            continue

        valid_items.append(
            deepcopy(
                strategy
            )
        )

    return (
        valid_items,
        invalid_entries,
    )


def _build_invalid_entry(
    strategy: Any,
    index: int,
):
    """
    Build a structured pipeline invalid entry.
    """

    if not isinstance(
        strategy,
        dict,
    ):

        error_message = (
            f"Strategy at index {index} "
            "must be a dictionary."
        )

    else:

        symbol = strategy.get(
            "symbol"
        )

        if not isinstance(
            symbol,
            str,
        ):

            error_message = (
                f"Strategy at index {index} "
                "must contain a valid symbol."
            )

        elif not symbol.strip():

            error_message = (
                f"Strategy at index {index} "
                "contains an empty symbol."
            )

        else:

            error_message = (
                f"Strategy at index {index} "
                "is incomplete: missing "
                "analysis, performance, or risk data."
            )

    return {
        "index": index,
        "strategy": deepcopy(
            strategy
        ),
        "errors": [
            error_message
        ],
    }


# ============================================================
# LEGACY COMPATIBILITY HELPERS
# ============================================================

def _count_incomplete_input_strategies(
    simulations: Any,
) -> int:
    """
    Count structurally incomplete strategy records.

    Kept as a compatibility helper for callers/tests that
    may import this internal function.
    """

    if simulations is None:
        return 0

    if _is_invalid_container(
        simulations
    ):
        return 0

    items = _to_items(
        simulations
    )

    if items is None:
        return 0

    invalid_count = 0

    for strategy in items:

        if _is_structurally_invalid_strategy(
            strategy
        ):
            invalid_count += 1

    return invalid_count


def _build_pipeline_invalid_entries(
    simulations: Any,
):
    """
    Build structured invalid entries for structurally
    incomplete strategy records.

    Kept as a compatibility helper.
    """

    if simulations is None:
        return []

    if _is_invalid_container(
        simulations
    ):
        return []

    items = _to_items(
        simulations
    )

    if items is None:
        return []

    invalid_entries = []

    for index, strategy in enumerate(
        items
    ):

        if not _is_structurally_invalid_strategy(
            strategy
        ):
            continue

        invalid_entries.append(
            _build_invalid_entry(
                strategy,
                index,
            )
        )

    return invalid_entries


# ============================================================
# RANKER IMPORT
# ============================================================

def _create_ranker(
    performance_weight: float,
    risk_weight: float,
):
    """
    Create the Grid Strategy Ranker.

    Import is kept local so this pipeline remains lightweight
    and avoids unnecessary import coupling at module load time.
    """

    from engine.grid_strategy_ranker import (
        GridStrategyRanker,
    )

    return GridStrategyRanker(
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


# ============================================================
# SELECTOR IMPORT
# ============================================================

def _create_selector(
    top_n: int,
):
    """
    Create the Grid Strategy Selector.
    """

    from engine.grid_strategy_selector import (
        GridStrategySelector,
    )

    return GridStrategySelector(
        top_n=top_n,
    )


# ============================================================
# VALIDATION
# ============================================================

def _validate_weight(
    value: Any,
    name: str,
):
    """
    Validate a strategy score weight.

    Returns:
        (True, normalized_value, None)

    or:

        (False, None, error_message)
    """

    if not _is_number(
        value
    ):
        return (
            False,
            None,
            f"{name} must be numeric.",
        )

    numeric_value = float(
        value
    )

    if numeric_value < 0:
        return (
            False,
            None,
            f"{name} must not be negative.",
        )

    return (
        True,
        numeric_value,
        None,
    )


def _validate_weights(
    performance_weight: Any,
    risk_weight: Any,
):
    """
    Validate and normalize performance/risk weights.
    """

    valid_performance, performance, error = (
        _validate_weight(
            performance_weight,
            "Performance weight",
        )
    )

    if not valid_performance:
        return (
            False,
            None,
            None,
            error,
        )

    valid_risk, risk, error = (
        _validate_weight(
            risk_weight,
            "Risk weight",
        )
    )

    if not valid_risk:
        return (
            False,
            None,
            None,
            error,
        )

    total = (
        performance
        + risk
    )

    if total <= 0:
        return (
            False,
            None,
            None,
            (
                "Performance and risk weights "
                "must have a positive total."
            ),
        )

    performance /= total
    risk /= total

    return (
        True,
        performance,
        risk,
        None,
    )


def _validate_top_n(
    top_n: Any,
):
    """
    Validate top_n.

    None is valid because it means:
    select all ranked strategies.
    """

    if top_n is None:
        return (
            True,
            None,
            None,
        )

    if isinstance(
        top_n,
        bool,
    ):
        return (
            False,
            None,
            "top_n must be an integer.",
        )

    if not isinstance(
        top_n,
        int,
    ):
        return (
            False,
            None,
            "top_n must be an integer.",
        )

    if top_n <= 0:
        return (
            False,
            None,
            "top_n must be greater than zero.",
        )

    return (
        True,
        top_n,
        None,
    )


# ============================================================
# EMPTY RESULT
# ============================================================

def _build_empty_result():
    """
    Build the stable pipeline result contract.
    """

    return {
        "success": True,
        "status": STATUS_EMPTY,

        "processed_count": 0,
        "valid_count": 0,
        "invalid_count": 0,

        "ranked_count": 0,
        "selected_count": 0,

        "ranked_strategies": [],
        "selected_strategies": [],

        "ranking": {},
        "selection": {},

        "invalid_strategies": [],
        "errors": [],

        "input": None,
    }


# ============================================================
# MAIN PIPELINE
# ============================================================

def run_grid_strategy_pipeline(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = DEFAULT_TOP_N,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    """
    Run the complete Grid Strategy ranking and selection
    pipeline.

    Parameters
    ----------
    simulations:
        Iterable containing grid strategy analysis results.

    top_n:
        Maximum number of strategies to select.

        None means all ranked strategies are selected.

    performance_weight:
        Weight used by GridStrategyRanker.

    risk_weight:
        Weight used by GridStrategyRanker.

    Returns
    -------
    dict
        Stable pipeline result.
    """

    original_input = _snapshot_input(
        simulations
    )

    result = _build_empty_result()

    result["input"] = deepcopy(
        original_input
    )

    # ========================================================
    # INPUT CONTAINER
    # ========================================================

    if simulations is None:

        result["status"] = STATUS_EMPTY

        return deepcopy(
            result
        )

    if _is_invalid_container(
        simulations
    ):

        result["success"] = False
        result["status"] = STATUS_ERROR

        result["errors"].append(
            "Simulations must be a list, tuple, or iterable."
        )

        return deepcopy(
            result
        )

    items = _to_items(
        simulations
    )

    if items is None:

        result["success"] = False
        result["status"] = STATUS_ERROR

        result["errors"].append(
            "Simulations must be an iterable collection."
        )

        return deepcopy(
            result
        )

    if not items:

        result["status"] = STATUS_EMPTY

        return deepcopy(
            result
        )

    # ========================================================
    # PROCESSED COUNT
    # ========================================================

    result["processed_count"] = len(
        items
    )

    # ========================================================
    # WEIGHT VALIDATION
    # ========================================================

    (
        valid_weights,
        normalized_performance_weight,
        normalized_risk_weight,
        weight_error,
    ) = _validate_weights(
        performance_weight,
        risk_weight,
    )

    if not valid_weights:

        result["success"] = False
        result["status"] = STATUS_ERROR

        result["errors"].append(
            weight_error
        )

        return deepcopy(
            result
        )

    # ========================================================
    # TOP N VALIDATION
    # ========================================================

    (
        valid_top_n,
        normalized_top_n,
        top_n_error,
    ) = _validate_top_n(
        top_n
    )

    if not valid_top_n:

        result["success"] = False
        result["status"] = STATUS_ERROR

        result["errors"].append(
            top_n_error
        )

        return deepcopy(
            result
        )

    # ========================================================
    # PIPELINE INPUT INTEGRITY
    # ========================================================
    #
    # IMPORTANT:
    #
    # The Ranker is allowed to have its own validation rules.
    # The pipeline must nevertheless prevent obviously
    # incomplete strategy records from being counted as valid
    # candidates.
    #
    # Example:
    #
    #     {
    #         "symbol": "INVALID"
    #     }
    #
    # must not become a valid ranked strategy merely because
    # the Ranker is permissive about missing analysis data.
    #
    # Therefore we split the input BEFORE ranking.
    # ========================================================

    (
        valid_input_items,
        pipeline_invalid_entries,
    ) = _split_pipeline_inputs(
        items
    )

    pipeline_invalid_count = len(
        pipeline_invalid_entries
    )

    # Preserve pipeline-level invalid entries immediately.
    result["invalid_strategies"] = deepcopy(
        pipeline_invalid_entries
    )

    # Add their error messages.
    for invalid_entry in (
        pipeline_invalid_entries
    ):

        for error in invalid_entry.get(
            "errors",
            [],
        ):

            if error not in result["errors"]:
                result["errors"].append(
                    error
                )

    # ========================================================
    # NO VALID INPUTS
    # ========================================================

    if not valid_input_items:

        if pipeline_invalid_count > 0:

            result["success"] = False
            result["status"] = STATUS_ERROR

            result["invalid_count"] = (
                pipeline_invalid_count
            )

        else:

            result["success"] = True
            result["status"] = STATUS_EMPTY

        return deepcopy(
            result
        )

    # ========================================================
    # RANKING
    # ========================================================

    try:

        ranker = _create_ranker(
            performance_weight=(
                normalized_performance_weight
            ),
            risk_weight=(
                normalized_risk_weight
            ),
        )

        ranking_result = ranker.run(
            deepcopy(
                valid_input_items
            )
        )

    except Exception as exc:

        result["success"] = False
        result["status"] = STATUS_ERROR

        error_message = (
            "Grid Strategy Ranker failed: "
            f"{exc}"
        )

        result["errors"].append(
            error_message
        )

        return deepcopy(
            result
        )

    ranking_result = _safe_dict(
        ranking_result
    )

    # ========================================================
    # PRESERVE RANKER OUTPUT
    # ========================================================

    ranked_strategies = _safe_list(
        ranking_result.get(
            "ranked_strategies"
        )
    )

    ranker_invalid_strategies = _safe_list(
        ranking_result.get(
            "invalid_strategies"
        )
    )

    ranker_errors = _safe_list(
        ranking_result.get(
            "errors"
        )
    )

    ranker_processed_count = int(
        _safe_float(
            ranking_result.get(
                "processed_count"
            )
        )
    )

    ranker_valid_count = int(
        _safe_float(
            ranking_result.get(
                "valid_count"
            )
        )
    )

    ranker_invalid_count = int(
        _safe_float(
            ranking_result.get(
                "invalid_count"
            )
        )
    )

    result["ranking"] = deepcopy(
        ranking_result
    )

    # --------------------------------------------------------
    # Do NOT expose incomplete records as ranked candidates.
    #
    # This is a defensive second validation layer in case
    # the Ranker itself accepts an incomplete record.
    # --------------------------------------------------------

    clean_ranked_strategies = []

    ranker_post_validation_invalid = []

    for ranked_index, strategy in enumerate(
        ranked_strategies
    ):

        if _is_structurally_invalid_strategy(
            strategy
        ):

            ranker_post_validation_invalid.append(
                _build_invalid_entry(
                    strategy,
                    ranked_index,
                )
            )

            continue

        clean_ranked_strategies.append(
            deepcopy(
                strategy
            )
        )

    ranked_strategies = (
        clean_ranked_strategies
    )

    result["ranked_strategies"] = deepcopy(
        ranked_strategies
    )

    result["ranked_count"] = len(
        ranked_strategies
    )

    # ========================================================
    # MERGE INVALID OUTPUT
    # ========================================================

    invalid_strategies = []

    seen_indices = set()

    # --------------------------------------------------------
    # Pipeline-level invalid entries
    # --------------------------------------------------------

    for invalid_entry in (
        pipeline_invalid_entries
    ):

        entry = deepcopy(
            invalid_entry
        )

        invalid_strategies.append(
            entry
        )

        index = entry.get(
            "index"
        )

        if isinstance(
            index,
            int,
        ):
            seen_indices.add(
                index
            )

    # --------------------------------------------------------
    # Ranker invalid entries
    #
    # These are preserved exactly as supplied by the Ranker.
    # --------------------------------------------------------

    for invalid_entry in (
        ranker_invalid_strategies
    ):

        entry = deepcopy(
            invalid_entry
        )

        index = (
            entry.get("index")
            if isinstance(
                entry,
                dict,
            )
            else None
        )

        if (
            isinstance(
                index,
                int,
            )
            and index in seen_indices
        ):
            continue

        invalid_strategies.append(
            entry
        )

        if isinstance(
            index,
            int,
        ):
            seen_indices.add(
                index
            )

    # --------------------------------------------------------
    # Post-ranker validation failures
    # --------------------------------------------------------

    for invalid_entry in (
        ranker_post_validation_invalid
    ):

        invalid_strategies.append(
            deepcopy(
                invalid_entry
            )
        )

    result["invalid_strategies"] = (
        deepcopy(
            invalid_strategies
        )
    )

    # ========================================================
    # ERRORS
    # ========================================================

    result["errors"] = deepcopy(
        ranker_errors
    )

    existing_error_text = {
        str(error)
        for error in result["errors"]
    }

    for invalid_entry in (
        pipeline_invalid_entries
    ):

        for error in invalid_entry.get(
            "errors",
            [],
        ):

            if str(error) in existing_error_text:
                continue

            result["errors"].append(
                str(error)
            )

            existing_error_text.add(
                str(error)
            )

    for invalid_entry in (
        ranker_post_validation_invalid
    ):

        for error in invalid_entry.get(
            "errors",
            [],
        ):

            if str(error) in existing_error_text:
                continue

            result["errors"].append(
                str(error)
            )

            existing_error_text.add(
                str(error)
            )

    # ========================================================
    # INVALID COUNT
    # ========================================================

    #
    # The authoritative pipeline count is based on:
    #
    #   pipeline-invalid inputs
    #   +
    #   Ranker-invalid inputs not already represented
    #
    # This prevents double counting.
    #

    effective_invalid_count = max(
        pipeline_invalid_count,
        ranker_invalid_count,
        len(invalid_strategies),
    )

    result["invalid_count"] = (
        effective_invalid_count
    )

    # ========================================================
    # VALID COUNT
    # ========================================================

    #
    # Valid candidates are the strategies that actually
    # survived pipeline validation and reached ranking.
    #
    result["valid_count"] = len(
        ranked_strategies
    )

    # If the Ranker agrees with the actual ranked list,
    # preserving its count is safe.
    if (
        ranker_valid_count
        == len(ranked_strategies)
    ):

        result["valid_count"] = (
            ranker_valid_count
        )

    # ========================================================
    # NOTHING RANKED
    # ========================================================

    if not ranked_strategies:

        if effective_invalid_count > 0:

            result["success"] = False
            result["status"] = STATUS_ERROR

        else:

            result["success"] = True
            result["status"] = STATUS_EMPTY

        result["selection"] = {
            "status": STATUS_EMPTY,
            "selected_strategies": [],
            "selected_count": 0,
        }

        return deepcopy(
            result
        )

    # ========================================================
    # SELECTION TOP N
    # ========================================================

    #
    # Selector expects an integer top_n.
    #
    # Pipeline top_n=None means:
    # select all ranked strategies.
    #

    effective_selector_top_n = (
        len(ranked_strategies)
        if normalized_top_n is None
        else normalized_top_n
    )

    try:

        selector = _create_selector(
            top_n=effective_selector_top_n
        )

        selection_result = selector.run(
            deepcopy(
                ranked_strategies
            ),
            top_n=effective_selector_top_n,
        )

    except Exception as exc:

        result["success"] = False
        result["status"] = STATUS_ERROR

        error_message = (
            "Grid Strategy Selector failed: "
            f"{exc}"
        )

        result["errors"].append(
            error_message
        )

        return deepcopy(
            result
        )

    selection_result = _safe_dict(
        selection_result
    )

    # ========================================================
    # PRESERVE SELECTOR OUTPUT
    # ========================================================

    selected_strategies = _safe_list(
        selection_result.get(
            "selected_strategies"
        )
    )

    result["selection"] = deepcopy(
        selection_result
    )

    result["selected_strategies"] = deepcopy(
        selected_strategies
    )

    result["selected_count"] = len(
        selected_strategies
    )

    # ========================================================
    # STATUS
    # ========================================================

    selection_status = selection_result.get(
        "status"
    )

    if (
        effective_invalid_count > 0
        or selection_status == STATUS_PARTIAL
    ):

        result["status"] = STATUS_PARTIAL

        result["success"] = (
            result["valid_count"] > 0
            and result["selected_count"] > 0
        )

    elif selection_status == STATUS_EMPTY:

        result["status"] = STATUS_EMPTY

        result["success"] = (
            result["valid_count"] > 0
        )

    else:

        result["status"] = STATUS_SUCCESS
        result["success"] = True

    # ========================================================
    # FINAL INDEPENDENT RESULT
    # ========================================================

    return deepcopy(
        result
    )


# ============================================================
# ALIASES
# ============================================================

def process_grid_strategy_pipeline(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = DEFAULT_TOP_N,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    """
    Backward-compatible alias for run_grid_strategy_pipeline().
    """

    return run_grid_strategy_pipeline(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


def execute_grid_strategy_pipeline(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = DEFAULT_TOP_N,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    """
    Backward-compatible alias for run_grid_strategy_pipeline().
    """

    return run_grid_strategy_pipeline(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def grid_strategy_pipeline(
    simulations: Iterable[Dict[str, Any]] | None,
    top_n: int | None = DEFAULT_TOP_N,
    performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
    risk_weight: float = DEFAULT_RISK_WEIGHT,
) -> Dict[str, Any]:
    """
    Convenience function for running the complete
    Grid Strategy Pipeline.
    """

    return run_grid_strategy_pipeline(
        simulations,
        top_n=top_n,
        performance_weight=performance_weight,
        risk_weight=risk_weight,
    )


# ============================================================
# OBJECT-ORIENTED WRAPPER
# ============================================================

class GridStrategyPipeline:
    """
    Object-oriented wrapper for Grid Strategy Pipeline.

    Constructor configuration:
        performance_weight
        risk_weight
        top_n

    Runtime top_n overrides constructor top_n when supplied.
    """

    def __init__(
        self,
        performance_weight: float = DEFAULT_PERFORMANCE_WEIGHT,
        risk_weight: float = DEFAULT_RISK_WEIGHT,
        top_n: int | None = DEFAULT_TOP_N,
    ) -> None:

        valid_weights, _, _, weight_error = (
            _validate_weights(
                performance_weight,
                risk_weight,
            )
        )

        if not valid_weights:
            raise ValueError(
                weight_error
            )

        valid_top_n, _, top_n_error = (
            _validate_top_n(
                top_n
            )
        )

        if not valid_top_n:
            raise ValueError(
                top_n_error
            )

        self.performance_weight = (
            performance_weight
        )

        self.risk_weight = (
            risk_weight
        )

        self.top_n = top_n

    def run(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:
        """
        Run the pipeline.
        """

        effective_top_n = (
            self.top_n
            if top_n is None
            else top_n
        )

        return run_grid_strategy_pipeline(
            simulations,
            top_n=effective_top_n,
            performance_weight=(
                self.performance_weight
            ),
            risk_weight=(
                self.risk_weight
            ),
        )

    def process(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:
        """
        Alias for run().
        """

        return self.run(
            simulations,
            top_n=top_n,
        )

    def execute(
        self,
        simulations: Iterable[Dict[str, Any]] | None,
        top_n: int | None = None,
    ) -> Dict[str, Any]:
        """
        Alias for run().
        """

        return self.run(
            simulations,
            top_n=top_n,
        )


# ============================================================
# ENGINE ALIAS
# ============================================================

GridStrategyPipelineEngine = (
    GridStrategyPipeline
)


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [
    "VERSION",

    "STATUS_SUCCESS",
    "STATUS_PARTIAL",
    "STATUS_EMPTY",
    "STATUS_ERROR",

    "DEFAULT_PERFORMANCE_WEIGHT",
    "DEFAULT_RISK_WEIGHT",
    "DEFAULT_TOP_N",

    "REQUIRED_RESULT_KEYS",

    "run_grid_strategy_pipeline",
    "process_grid_strategy_pipeline",
    "execute_grid_strategy_pipeline",
    "grid_strategy_pipeline",

    "GridStrategyPipeline",
    "GridStrategyPipelineEngine",
]