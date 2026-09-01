"""
==========================================
SULTAN QUANT OS
Grid Risk Analyzer
Version : 1.0.0
==========================================

Responsibilities:

- Analyze risk characteristics of grid simulations
- Measure capital utilization
- Measure capital exposure
- Measure completed/open/pending layer risk
- Calculate maximum layer exposure
- Calculate utilization and exposure ratios
- Calculate profit-to-capital ratios
- Calculate risk-adjusted efficiency metrics
- Preserve simulation input immutability
- Return stable result contracts
"""

from copy import deepcopy
from typing import Any


class GridRiskAnalyzer:
    """
    Analyze risk characteristics from grid simulation results.

    The analyzer consumes simulation dictionaries produced by the
    GridExecutionSimulator and converts them into normalized risk metrics.

    The implementation intentionally avoids modifying source simulations.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    REQUIRED_RESULT_KEYS = (
        "status",
        "analyses",
        "processed_count",
        "failed_count",
        "errors",
        "input",
    )

    REQUIRED_METRIC_KEYS = (
        "symbol",
        "layers",
        "completed_layers",
        "open_layers",
        "pending_layers",
        "completion_rate",
        "total_capital",
        "capital_deployed",
        "capital_available",
        "capital_utilization",
        "capital_exposure",
        "capital_exposure_ratio",
        "maximum_layer_capital",
        "average_layer_capital",
        "realized_profit",
        "unrealized_profit",
        "total_profit",
        "realized_return",
        "total_return",
        "profit_to_exposure",
        "risk_score",
    )

    def __init__(
        self,
        max_safe_utilization: float = 0.80,
        max_safe_exposure: float = 0.80,
    ):
        self.max_safe_utilization = (
            self._validate_threshold(
                max_safe_utilization,
                "max_safe_utilization",
            )
        )

        self.max_safe_exposure = (
            self._validate_threshold(
                max_safe_exposure,
                "max_safe_exposure",
            )
        )

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def run(
        self,
        simulations: Any,
    ) -> dict:
        """
        Analyze grid simulation results.
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
                "simulations must be a list or tuple"
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

        self._validate_simulation(
            simulation
        )

        simulation_copy = deepcopy(
            simulation
        )

        symbol = self._normalize_symbol(
            simulation_copy["symbol"]
        )

        layers = self._validate_positive_integer(
            simulation_copy["layers"],
            "layers",
        )

        total_capital = self._validate_positive_number(
            simulation_copy["total_capital"],
            "total_capital",
        )

        layer_collection = self._get_layer_collection(
            simulation_copy
        )

        if len(layer_collection) != layers:
            raise ValueError(
                "layer collection length must equal layers"
            )

        layer_metrics = []

        for layer in layer_collection:

            layer_metrics.append(
                self._analyze_layer(
                    layer
                )
            )

        completed_layers = sum(
            1
            for item in layer_metrics
            if item["status"] == "COMPLETED"
        )

        open_layers = sum(
            1
            for item in layer_metrics
            if item["status"] == "OPEN"
        )

        pending_layers = sum(
            1
            for item in layer_metrics
            if item["status"] == "PENDING"
        )

        completion_rate = (
            completed_layers / layers
        )

        capital_deployed = sum(
            item["capital"]
            for item in layer_metrics
            if item["status"]
            in (
                "OPEN",
                "COMPLETED",
            )
        )

        capital_available = max(
            total_capital - capital_deployed,
            0.0,
        )

        capital_utilization = (
            capital_deployed / total_capital
        )

        capital_exposure = sum(
            item["capital"]
            for item in layer_metrics
            if item["status"] == "OPEN"
        )

        capital_exposure_ratio = (
            capital_exposure / total_capital
        )

        layer_capitals = [
            item["capital"]
            for item in layer_metrics
        ]

        maximum_layer_capital = max(
            layer_capitals
        )

        average_layer_capital = (
            sum(layer_capitals)
            / len(layer_capitals)
        )

        realized_profit = self._resolve_profit(
            simulation_copy,
            "realized_profit",
            layer_metrics,
            "COMPLETED",
        )

        unrealized_profit = self._resolve_profit(
            simulation_copy,
            "unrealized_profit",
            layer_metrics,
            "OPEN",
        )

        total_profit = (
            realized_profit
            + unrealized_profit
        )

        realized_return = (
            realized_profit
            / total_capital
        )

        total_return = (
            total_profit
            / total_capital
        )

        profit_to_exposure = (
            total_profit / capital_exposure
            if capital_exposure > 0
            else 0.0
        )

        risk_score = self._calculate_risk_score(
            capital_utilization,
            capital_exposure_ratio,
            completion_rate,
            pending_layers,
            layers,
        )

        return {
            "symbol": symbol,
            "layers": layers,
            "completed_layers": completed_layers,
            "open_layers": open_layers,
            "pending_layers": pending_layers,
            "completion_rate": completion_rate,
            "total_capital": total_capital,
            "capital_deployed": capital_deployed,
            "capital_available": capital_available,
            "capital_utilization": capital_utilization,
            "capital_exposure": capital_exposure,
            "capital_exposure_ratio": capital_exposure_ratio,
            "maximum_layer_capital": maximum_layer_capital,
            "average_layer_capital": average_layer_capital,
            "realized_profit": realized_profit,
            "unrealized_profit": unrealized_profit,
            "total_profit": total_profit,
            "realized_return": realized_return,
            "total_return": total_return,
            "profit_to_exposure": profit_to_exposure,
            "risk_score": risk_score,
            "layers_detail": deepcopy(
                layer_metrics
            ),
            "simulation": deepcopy(
                simulation_copy
            ),
        }

    # ==========================================================
    # SIMULATION VALIDATION
    # ==========================================================

    def _validate_simulation(
        self,
        simulation: Any,
    ) -> None:

        if not isinstance(
            simulation,
            dict,
        ):
            raise ValueError(
                "simulation must be a dictionary"
            )

        required_fields = (
            "symbol",
            "layers",
            "total_capital",
        )

        for field in required_fields:

            if field not in simulation:
                raise ValueError(
                    f"simulation missing required field: {field}"
                )

        self._normalize_symbol(
            simulation["symbol"]
        )

        self._validate_positive_integer(
            simulation["layers"],
            "layers",
        )

        self._validate_positive_number(
            simulation["total_capital"],
            "total_capital",
        )

        self._get_layer_collection(
            simulation
        )

    def _get_layer_collection(
        self,
        simulation: dict,
    ) -> list:

        layer_collection = None

        if "layers_detail" in simulation:
            layer_collection = simulation[
                "layers_detail"
            ]

        elif "layer_results" in simulation:
            layer_collection = simulation[
                "layer_results"
            ]

        elif "layers_result" in simulation:
            layer_collection = simulation[
                "layers_result"
            ]

        elif "layers_data" in simulation:
            layer_collection = simulation[
                "layers_data"
            ]

        elif "layer_plans" in simulation:
            layer_collection = simulation[
                "layer_plans"
            ]

        if not isinstance(
            layer_collection,
            (list, tuple),
        ):
            raise ValueError(
                "simulation layer collection must be a list or tuple"
            )

        return list(
            layer_collection
        )

    # ==========================================================
    # LAYER ANALYSIS
    # ==========================================================

    def _analyze_layer(
        self,
        layer: Any,
    ) -> dict:

        if not isinstance(
            layer,
            dict,
        ):
            raise ValueError(
                "layer must be a dictionary"
            )

        status = layer.get(
            "status"
        )

        if not isinstance(
            status,
            str,
        ):
            raise ValueError(
                "layer status must be a string"
            )

        status = status.strip().upper()

        if status not in (
            "PENDING",
            "OPEN",
            "COMPLETED",
        ):
            raise ValueError(
                "invalid layer status"
            )

        capital_value = layer.get(
            "capital",
            layer.get(
                "layer_capital"
            ),
        )

        capital = self._validate_non_negative_number(
            capital_value,
            "layer capital",
        )

        profit_value = layer.get(
            "profit",
            0.0,
        )

        profit = self._validate_number(
            profit_value,
            "layer profit",
        )

        return {
            "layer": deepcopy(
                layer.get(
                    "layer",
                    layer.get(
                        "layer_number"
                    ),
                )
            ),
            "status": status,
            "capital": capital,
            "profit": profit,
        }

    # ==========================================================
    # PROFIT
    # ==========================================================

    def _resolve_profit(
        self,
        simulation: dict,
        field: str,
        layer_metrics: list,
        status: str,
    ) -> float:

        if field in simulation:

            return self._validate_number(
                simulation[field],
                field,
            )

        return sum(
            item["profit"]
            for item in layer_metrics
            if item["status"] == status
        )

    # ==========================================================
    # RISK SCORE
    # ==========================================================

    def _calculate_risk_score(
        self,
        utilization: float,
        exposure_ratio: float,
        completion_rate: float,
        pending_layers: int,
        total_layers: int,
    ) -> float:
        """
        Calculate normalized grid risk score.

        Higher score means higher capital risk.

        Components:

        - Capital utilization
        - Open capital exposure
        - Pending layer concentration

        Completion rate reduces the risk contribution because
        completed layers represent recycled/realized grid activity.
        """

        pending_ratio = (
            pending_layers / total_layers
            if total_layers > 0
            else 0.0
        )

        utilization_component = min(
            utilization,
            1.0,
        )

        exposure_component = min(
            exposure_ratio,
            1.0,
        )

        pending_component = min(
            pending_ratio,
            1.0,
        )

        completion_reduction = min(
            completion_rate,
            1.0,
        )

        raw_score = (
            utilization_component * 0.40
            + exposure_component * 0.40
            + pending_component * 0.20
        )

        adjusted_score = (
            raw_score
            * (
                1.0
                - (
                    completion_reduction
                    * 0.25
                )
            )
        )

        return max(
            0.0,
            min(
                adjusted_score,
                1.0,
            ),
        )

    # ==========================================================
    # VALIDATION HELPERS
    # ==========================================================

    def _normalize_symbol(
        self,
        value: Any,
    ) -> str:

        if not isinstance(
            value,
            str,
        ):
            raise ValueError(
                "symbol must be a string"
            )

        symbol = (
            value
            .strip()
            .upper()
            .replace("/", "")
            .replace("-", "")
            .replace("_", "")
            .replace(" ", "")
        )

        if not symbol:
            raise ValueError(
                "symbol cannot be empty"
            )

        return symbol

    def _validate_number(
        self,
        value: Any,
        name: str,
    ) -> float:

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{name} must be numeric"
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
                f"{name} must be numeric"
            )

        return numeric_value

    def _validate_positive_number(
        self,
        value: Any,
        name: str,
    ) -> float:

        numeric_value = self._validate_number(
            value,
            name,
        )

        if numeric_value <= 0:
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric_value

    def _validate_non_negative_number(
        self,
        value: Any,
        name: str,
    ) -> float:

        numeric_value = self._validate_number(
            value,
            name,
        )

        if numeric_value < 0:
            raise ValueError(
                f"{name} cannot be negative"
            )

        return numeric_value

    def _validate_positive_integer(
        self,
        value: Any,
        name: str,
    ) -> int:

        if isinstance(
            value,
            bool,
        ):
            raise ValueError(
                f"{name} must be an integer"
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
                f"{name} must be an integer"
            )

        if not numeric_value.is_integer():
            raise ValueError(
                f"{name} must be an integer"
            )

        numeric_value = int(
            numeric_value
        )

        if numeric_value <= 0:
            raise ValueError(
                f"{name} must be greater than zero"
            )

        return numeric_value

    def _validate_threshold(
        self,
        value: Any,
        name: str,
    ) -> float:

        numeric_value = self._validate_number(
            value,
            name,
        )

        if not 0 < numeric_value <= 1:
            raise ValueError(
                f"{name} must be greater than zero and less than or equal to one"
            )

        return numeric_value

    # ==========================================================
    # RESULT CONTRACT
    # ==========================================================

    def _create_result(
        self,
        input_data: Any,
    ) -> dict:

        return {
            "status": self.STATUS_EMPTY,
            "analyses": [],
            "processed_count": 0,
            "failed_count": 0,
            "errors": [],
            "input": deepcopy(
                input_data
            ),
        }


# ==============================================================
# FUNCTION API
# ==============================================================

def analyze_grid_risk(
    simulations: Any,
    **kwargs,
) -> dict:
    """
    Convenience function for GridRiskAnalyzer.
    """

    analyzer = GridRiskAnalyzer(
        **kwargs
    )

    return analyzer.run(
        simulations
    )