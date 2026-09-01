"""
==========================================
SULTAN QUANT OS
Grid Performance Analyzer
Version : 1.0.0
==========================================

Responsibilities:

- Analyze Grid Execution Simulator results
- Calculate aggregate performance metrics
- Calculate realized and unrealized performance
- Calculate completion and layer statistics
- Preserve input immutability
- Return stable result contracts
- Support process() and execute() aliases
"""

from copy import deepcopy
from typing import Any


class GridPerformanceAnalyzer:
    """
    Analyze grid execution simulation results.

    The analyzer intentionally returns dictionaries so that its output
    can be consumed safely by ranking engines, portfolio engines,
    reporting layers, and future institutional modules.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    REQUIRED_RESULT_KEYS = (
        "status",
        "metrics",
        "analyses",
        "processed_count",
        "failed_count",
        "input",
        "errors",
    )

    REQUIRED_METRIC_KEYS = (
        "total_plans",
        "completed_plans",
        "open_plans",
        "pending_plans",
        "total_layers",
        "completed_layers",
        "open_layers",
        "pending_layers",
        "completion_rate",
        "total_capital",
        "capital_deployed",
        "realized_profit",
        "unrealized_profit",
        "total_profit",
        "realized_return",
        "total_return",
        "profit_per_completed_layer",
        "profit_per_plan",
    )

    def __init__(self):
        pass

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def run(
        self,
        simulations: Any,
    ) -> dict:
        """
        Analyze simulation results.
        """

        original_input = deepcopy(simulations)

        result = self._create_result(
            input_data=original_input,
        )

        # ------------------------------------------------------
        # Empty input
        # ------------------------------------------------------

        if simulations is None:
            result["status"] = self.STATUS_EMPTY
            return deepcopy(result)

        # ------------------------------------------------------
        # Container validation
        # ------------------------------------------------------

        if isinstance(simulations, str):
            result["status"] = self.STATUS_ERROR
            result["errors"].append(
                "simulations must be a list"
            )
            return deepcopy(result)

        if not isinstance(
            simulations,
            (list, tuple),
        ):
            result["status"] = self.STATUS_ERROR
            result["errors"].append(
                "simulations must be a list or tuple"
            )
            return deepcopy(result)

        if len(simulations) == 0:
            result["status"] = self.STATUS_EMPTY
            return deepcopy(result)

        analyses = []
        errors = []

        # ------------------------------------------------------
        # Process simulations
        # ------------------------------------------------------

        for index, simulation in enumerate(simulations):

            try:

                analysis = self._analyze_simulation(
                    simulation
                )

                analyses.append(
                    deepcopy(analysis)
                )

            except Exception as exc:

                errors.append(
                    {
                        "index": index,
                        "error": str(exc),
                    }
                )

        result["analyses"] = deepcopy(analyses)
        result["processed_count"] = len(analyses)
        result["failed_count"] = len(errors)
        result["errors"] = deepcopy(errors)

        # ------------------------------------------------------
        # Aggregate metrics
        # ------------------------------------------------------

        result["metrics"] = self._aggregate_metrics(
            analyses
        )

        # ------------------------------------------------------
        # Final status
        # ------------------------------------------------------

        if len(analyses) == 0:

            if len(errors) == 0:
                result["status"] = self.STATUS_EMPTY
            else:
                result["status"] = self.STATUS_ERROR

        elif len(errors) > 0:

            result["status"] = self.STATUS_PARTIAL

        else:

            result["status"] = self.STATUS_SUCCESS

        return deepcopy(result)

    def process(
        self,
        simulations: Any,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(simulations)

    def execute(
        self,
        simulations: Any,
    ) -> dict:
        """
        Alias for run().
        """

        return self.run(simulations)

    # ==========================================================
    # SIMULATION ANALYSIS
    # ==========================================================

    def _analyze_simulation(
        self,
        simulation: Any,
    ) -> dict:

        if not isinstance(
            simulation,
            dict,
        ):
            raise ValueError(
                "simulation must be a dictionary"
            )

        simulation_copy = deepcopy(simulation)

        symbol = self._resolve_symbol(
            simulation_copy
        )

        layers = self._resolve_layers(
            simulation_copy
        )

        completed_layers = self._resolve_layer_collection(
            simulation_copy,
            "completed",
        )

        open_layers = self._resolve_layer_collection(
            simulation_copy,
            "open",
        )

        pending_layers = self._resolve_layer_collection(
            simulation_copy,
            "pending",
        )

        total_capital = self._resolve_numeric(
            simulation_copy.get(
                "total_capital",
                simulation_copy.get(
                    "capital",
                    0.0,
                ),
            ),
            "total_capital",
            allow_zero=True,
        )

        capital_deployed = self._resolve_numeric(
            simulation_copy.get(
                "capital_deployed",
                0.0,
            ),
            "capital_deployed",
            allow_zero=True,
        )

        realized_profit = self._resolve_numeric(
            simulation_copy.get(
                "realized_profit",
                self._sum_profit(
                    completed_layers
                ),
            ),
            "realized_profit",
            allow_zero=True,
        )

        unrealized_profit = self._resolve_numeric(
            simulation_copy.get(
                "unrealized_profit",
                self._sum_profit(
                    open_layers
                ),
            ),
            "unrealized_profit",
            allow_zero=True,
        )

        total_profit = self._resolve_numeric(
            simulation_copy.get(
                "total_profit",
                realized_profit
                + unrealized_profit,
            ),
            "total_profit",
            allow_zero=True,
        )

        completed_count = len(
            completed_layers
        )

        open_count = len(
            open_layers
        )

        pending_count = len(
            pending_layers
        )

        actual_total_layers = (
            completed_count
            + open_count
            + pending_count
        )

        if layers is None:
            layers = actual_total_layers

        if layers < actual_total_layers:
            raise ValueError(
                "layers cannot be less than total layer states"
            )

        completion_rate = self._safe_ratio(
            completed_count,
            layers,
        )

        realized_return = self._safe_ratio(
            realized_profit,
            total_capital,
        )

        total_return = self._safe_ratio(
            total_profit,
            total_capital,
        )

        profit_per_completed_layer = (
            self._safe_ratio(
                realized_profit,
                completed_count,
            )
        )

        return {
            "symbol": symbol,
            "layers": layers,
            "completed_layers": completed_count,
            "open_layers": open_count,
            "pending_layers": pending_count,
            "completion_rate": completion_rate,
            "total_capital": total_capital,
            "capital_deployed": capital_deployed,
            "realized_profit": realized_profit,
            "unrealized_profit": unrealized_profit,
            "total_profit": total_profit,
            "realized_return": realized_return,
            "total_return": total_return,
            "profit_per_completed_layer": (
                profit_per_completed_layer
            ),
            "completed": deepcopy(
                completed_layers
            ),
            "open": deepcopy(
                open_layers
            ),
            "pending": deepcopy(
                pending_layers
            ),
            "simulation": deepcopy(
                simulation_copy
            ),
        }

    # ==========================================================
    # SYMBOL
    # ==========================================================

    def _resolve_symbol(
        self,
        simulation: dict,
    ) -> str:

        symbol = simulation.get(
            "symbol"
        )

        if not isinstance(
            symbol,
            str,
        ):
            raise ValueError(
                "simulation symbol must be a string"
            )

        symbol = symbol.strip()

        if not symbol:
            raise ValueError(
                "simulation symbol cannot be empty"
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
                "simulation symbol cannot be empty"
            )

        return symbol

    # ==========================================================
    # LAYERS
    # ==========================================================

    def _resolve_layers(
        self,
        simulation: dict,
    ):
        value = simulation.get(
            "layers"
        )

        if value is None:
            return None

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
    # LAYER COLLECTIONS
    # ==========================================================

    def _resolve_layer_collection(
        self,
        simulation: dict,
        name: str,
    ) -> list:

        value = simulation.get(
            name,
            [],
        )

        if value is None:
            return []

        if not isinstance(
            value,
            (list, tuple),
        ):
            raise ValueError(
                f"{name} must be a list or tuple"
            )

        return deepcopy(
            list(value)
        )

    # ==========================================================
    # NUMERIC
    # ==========================================================

    def _resolve_numeric(
        self,
        value: Any,
        field_name: str,
        allow_zero: bool = False,
    ) -> float:

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{field_name} must be numeric"
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
                f"{field_name} must be numeric"
            )

        if allow_zero:

            if numeric_value < 0:
                raise ValueError(
                    f"{field_name} cannot be negative"
                )

        elif numeric_value <= 0:

            raise ValueError(
                f"{field_name} must be greater than zero"
            )

        return numeric_value

    # ==========================================================
    # PROFIT
    # ==========================================================

    def _sum_profit(
        self,
        layers: list,
    ) -> float:

        total = 0.0

        for layer in layers:

            if not isinstance(
                layer,
                dict,
            ):
                raise ValueError(
                    "layer result must be a dictionary"
                )

            value = layer.get(
                "profit",
                0.0,
            )

            value = self._resolve_numeric(
                value,
                "layer profit",
                allow_zero=True,
            )

            total += value

        return total

    # ==========================================================
    # RATIO
    # ==========================================================

    def _safe_ratio(
        self,
        numerator: float,
        denominator: float,
    ) -> float:

        if denominator <= 0:
            return 0.0

        return numerator / denominator

    # ==========================================================
    # AGGREGATION
    # ==========================================================

    def _aggregate_metrics(
        self,
        analyses: list,
    ) -> dict:

        metrics = {
            "total_plans": 0,
            "completed_plans": 0,
            "open_plans": 0,
            "pending_plans": 0,
            "total_layers": 0,
            "completed_layers": 0,
            "open_layers": 0,
            "pending_layers": 0,
            "completion_rate": 0.0,
            "total_capital": 0.0,
            "capital_deployed": 0.0,
            "realized_profit": 0.0,
            "unrealized_profit": 0.0,
            "total_profit": 0.0,
            "realized_return": 0.0,
            "total_return": 0.0,
            "profit_per_completed_layer": 0.0,
            "profit_per_plan": 0.0,
        }

        if not analyses:
            return metrics

        metrics["total_plans"] = len(
            analyses
        )

        for analysis in analyses:

            completed = analysis[
                "completed_layers"
            ]

            open_count = analysis[
                "open_layers"
            ]

            pending = analysis[
                "pending_layers"
            ]

            total_layers = analysis[
                "layers"
            ]

            metrics[
                "total_layers"
            ] += total_layers

            metrics[
                "completed_layers"
            ] += completed

            metrics[
                "open_layers"
            ] += open_count

            metrics[
                "pending_layers"
            ] += pending

            metrics[
                "total_capital"
            ] += analysis[
                "total_capital"
            ]

            metrics[
                "capital_deployed"
            ] += analysis[
                "capital_deployed"
            ]

            metrics[
                "realized_profit"
            ] += analysis[
                "realized_profit"
            ]

            metrics[
                "unrealized_profit"
            ] += analysis[
                "unrealized_profit"
            ]

            metrics[
                "total_profit"
            ] += analysis[
                "total_profit"
            ]

            if completed == total_layers:
                metrics[
                    "completed_plans"
                ] += 1

            elif completed > 0 or open_count > 0:
                metrics[
                    "open_plans"
                ] += 1

            else:
                metrics[
                    "pending_plans"
                ] += 1

        metrics[
            "completion_rate"
        ] = self._safe_ratio(
            metrics["completed_layers"],
            metrics["total_layers"],
        )

        metrics[
            "realized_return"
        ] = self._safe_ratio(
            metrics["realized_profit"],
            metrics["total_capital"],
        )

        metrics[
            "total_return"
        ] = self._safe_ratio(
            metrics["total_profit"],
            metrics["total_capital"],
        )

        metrics[
            "profit_per_completed_layer"
        ] = self._safe_ratio(
            metrics["realized_profit"],
            metrics["completed_layers"],
        )

        metrics[
            "profit_per_plan"
        ] = self._safe_ratio(
            metrics["total_profit"],
            metrics["total_plans"],
        )

        return metrics

    # ==========================================================
    # RESULT CONTRACT
    # ==========================================================

    def _create_result(
        self,
        input_data: Any,
    ) -> dict:

        return {
            "status": self.STATUS_EMPTY,
            "metrics": {
                "total_plans": 0,
                "completed_plans": 0,
                "open_plans": 0,
                "pending_plans": 0,
                "total_layers": 0,
                "completed_layers": 0,
                "open_layers": 0,
                "pending_layers": 0,
                "completion_rate": 0.0,
                "total_capital": 0.0,
                "capital_deployed": 0.0,
                "realized_profit": 0.0,
                "unrealized_profit": 0.0,
                "total_profit": 0.0,
                "realized_return": 0.0,
                "total_return": 0.0,
                "profit_per_completed_layer": 0.0,
                "profit_per_plan": 0.0,
            },
            "analyses": [],
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

def analyze_grid_performance(
    simulations: Any,
) -> dict:
    """
    Convenience function for analyzing Grid simulations.
    """

    analyzer = GridPerformanceAnalyzer()

    return analyzer.run(
        simulations
    )