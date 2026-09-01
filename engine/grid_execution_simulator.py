"""
==========================================
SULTAN QUANT OS
Grid Execution Simulator
Version : 1.0.0
==========================================

Responsibilities:

- Simulate grid execution plans
- Process price sequences
- Detect triggered grid entry levels
- Calculate take-profit exits
- Track open and closed layers
- Produce deterministic simulation results

Input:

Execution plan:

{
    "symbol": "HYPEUSDT",
    "reference_price": 100.0,
    "layers": 3,
    "take_profit": 0.02,
    "entry_levels": [...],
    "layer_plans": [...]
}

Price sequence:

[100.0, 99.0, 98.0, ...]

Output:

{
    "plans": [...],
    "simulations": [...],
    "completed": [...],
    "open": [...],
    "errors": [...]
}

The simulator does not mutate input plans or price sequences.
"""

from copy import deepcopy
from numbers import Real


class GridExecutionSimulator:
    """
    Simulate execution of one or more grid execution plans.

    A layer is opened when market price reaches or falls below its
    entry price.

    A layer is closed when market price reaches or exceeds its
    take-profit price.
    """

    def __init__(self):
        pass

    @staticmethod
    def _empty_result():
        return {
            "plans": [],
            "simulations": [],
            "completed": [],
            "open": [],
            "errors": [],
        }

    @staticmethod
    def _is_valid_number(value):
        return (
            isinstance(value, Real)
            and not isinstance(value, bool)
        )

    @staticmethod
    def _normalize_symbol(symbol):
        if not isinstance(symbol, str):
            return None

        symbol = symbol.strip().upper()

        if not symbol:
            return None

        return symbol

    def _validate_price_sequence(self, prices):
        errors = []

        if prices is None:
            errors.append("prices must not be None")
            return None, errors

        if isinstance(prices, (str, bytes)):
            errors.append("prices must be a list or tuple")
            return None, errors

        if not isinstance(prices, (list, tuple)):
            errors.append("prices must be a list or tuple")
            return None, errors

        if len(prices) == 0:
            errors.append("prices must not be empty")
            return None, errors

        normalized_prices = []

        for index, price in enumerate(prices):
            if not self._is_valid_number(price):
                errors.append(
                    f"price at index {index} must be numeric"
                )
                continue

            if price <= 0:
                errors.append(
                    f"price at index {index} must be greater than zero"
                )
                continue

            normalized_prices.append(float(price))

        if errors:
            return None, errors

        return normalized_prices, []

    def _validate_plan(self, plan):
        errors = []

        if not isinstance(plan, dict):
            return None, ["plan must be a dictionary"]

        symbol = self._normalize_symbol(plan.get("symbol"))

        if symbol is None:
            errors.append("plan symbol is invalid")

        reference_price = plan.get("reference_price")

        if not self._is_valid_number(reference_price):
            errors.append(
                "plan reference_price must be numeric"
            )
        elif reference_price <= 0:
            errors.append(
                "plan reference_price must be greater than zero"
            )

        layers = plan.get("layers")

        if (
            not isinstance(layers, int)
            or isinstance(layers, bool)
            or layers <= 0
        ):
            errors.append(
                "plan layers must be a positive integer"
            )

        take_profit = plan.get("take_profit")

        if not self._is_valid_number(take_profit):
            errors.append(
                "plan take_profit must be numeric"
            )
        elif take_profit <= 0:
            errors.append(
                "plan take_profit must be greater than zero"
            )

        entry_levels = plan.get("entry_levels")

        if isinstance(layers, int) and not isinstance(layers, bool):
            expected_layers = layers
        else:
            expected_layers = None

        if not isinstance(entry_levels, (list, tuple)):
            errors.append(
                "plan entry_levels must be a list or tuple"
            )
        elif expected_layers is not None:
            if len(entry_levels) != expected_layers:
                errors.append(
                    "plan entry_levels length must match layers"
                )

        normalized_entry_levels = []

        if isinstance(entry_levels, (list, tuple)):
            for index, entry_price in enumerate(entry_levels):
                if not self._is_valid_number(entry_price):
                    errors.append(
                        f"entry level at index {index} must be numeric"
                    )
                    continue

                if entry_price <= 0:
                    errors.append(
                        f"entry level at index {index} "
                        "must be greater than zero"
                    )
                    continue

                normalized_entry_levels.append(
                    float(entry_price)
                )

        layer_plans = plan.get("layer_plans")

        if not isinstance(layer_plans, (list, tuple)):
            errors.append(
                "plan layer_plans must be a list or tuple"
            )
        elif expected_layers is not None:
            if len(layer_plans) != expected_layers:
                errors.append(
                    "plan layer_plans length must match layers"
                )

        normalized_layer_plans = []

        if isinstance(layer_plans, (list, tuple)):
            for index, layer_plan in enumerate(layer_plans):
                if not isinstance(layer_plan, dict):
                    errors.append(
                        f"layer plan at index {index} "
                        "must be a dictionary"
                    )
                    continue

                layer_number = layer_plan.get("layer")

                if (
                    not isinstance(layer_number, int)
                    or isinstance(layer_number, bool)
                    or layer_number <= 0
                ):
                    errors.append(
                        f"layer plan at index {index} "
                        "has invalid layer"
                    )

                entry_price = layer_plan.get("entry_price")

                if not self._is_valid_number(entry_price):
                    errors.append(
                        f"layer plan at index {index} "
                        "has invalid entry_price"
                    )
                elif entry_price <= 0:
                    errors.append(
                        f"layer plan at index {index} "
                        "entry_price must be greater than zero"
                    )

                take_profit_price = layer_plan.get(
                    "take_profit_price"
                )

                if not self._is_valid_number(take_profit_price):
                    errors.append(
                        f"layer plan at index {index} "
                        "has invalid take_profit_price"
                    )
                elif take_profit_price <= 0:
                    errors.append(
                        f"layer plan at index {index} "
                        "take_profit_price must be greater than zero"
                    )

                capital = layer_plan.get("capital")

                if not self._is_valid_number(capital):
                    errors.append(
                        f"layer plan at index {index} "
                        "has invalid capital"
                    )
                elif capital <= 0:
                    errors.append(
                        f"layer plan at index {index} "
                        "capital must be greater than zero"
                    )

                normalized_layer_plans.append(
                    deepcopy(layer_plan)
                )

        if errors:
            return None, errors

        normalized_plan = deepcopy(plan)

        normalized_plan["symbol"] = symbol
        normalized_plan["reference_price"] = float(
            reference_price
        )
        normalized_plan["layers"] = layers
        normalized_plan["take_profit"] = float(
            take_profit
        )
        normalized_plan["entry_levels"] = (
            normalized_entry_levels
        )
        normalized_plan["layer_plans"] = (
            normalized_layer_plans
        )

        return normalized_plan, []

    def _simulate_plan(self, plan, prices):
        layer_states = []

        for layer_plan in plan["layer_plans"]:
            layer_states.append({
                "layer": layer_plan["layer"],
                "capital": float(layer_plan["capital"]),
                "entry_price": float(
                    layer_plan["entry_price"]
                ),
                "take_profit_price": float(
                    layer_plan["take_profit_price"]
                ),
                "status": "pending",
                "opened_at": None,
                "closed_at": None,
                "opened_price": None,
                "closed_price": None,
                "profit": 0.0,
            })

        completed_layers = []
        open_layers = []

        for price_index, price in enumerate(prices):
            for state in layer_states:
                if (
                    state["status"] == "pending"
                    and price <= state["entry_price"]
                ):
                    state["status"] = "open"
                    state["opened_at"] = price_index
                    state["opened_price"] = price

            for state in layer_states:
                if (
                    state["status"] == "open"
                    and price >= state["take_profit_price"]
                ):
                    state["status"] = "completed"
                    state["closed_at"] = price_index
                    state["closed_price"] = price

                    quantity = (
                        state["capital"]
                        / state["opened_price"]
                    )

                    profit = quantity * (
                        state["closed_price"]
                        - state["opened_price"]
                    )

                    state["profit"] = float(profit)

        for state in layer_states:
            if state["status"] == "completed":
                completed_layers.append(
                    deepcopy(state)
                )
            elif state["status"] == "open":
                open_layers.append(
                    deepcopy(state)
                )

        pending_layers = [
            deepcopy(state)
            for state in layer_states
            if state["status"] == "pending"
        ]

        total_profit = sum(
            layer["profit"]
            for layer in completed_layers
        )

        simulation = {
            "symbol": plan["symbol"],
            "reference_price": plan["reference_price"],
            "layers": deepcopy(layer_states),
            "completed_layers": completed_layers,
            "open_layers": open_layers,
            "pending_layers": pending_layers,
            "completed_count": len(completed_layers),
            "open_count": len(open_layers),
            "pending_count": len(pending_layers),
            "total_profit": float(total_profit),
        }

        return simulation

    def run(self, plans, prices):
        """
        Run grid execution simulation.

        Parameters
        ----------
        plans : list | tuple
            Execution plans produced by GridExecutionPlanner.

        prices : list | tuple
            Market price sequence.

        Returns
        -------
        dict
            Simulation result.
        """

        result = self._empty_result()

        normalized_prices, price_errors = (
            self._validate_price_sequence(prices)
        )

        if price_errors:
            result["errors"].extend(price_errors)
            return result

        if plans is None:
            result["errors"].append(
                "plans must not be None"
            )
            return result

        if isinstance(plans, (str, bytes)):
            result["errors"].append(
                "plans must be a list or tuple"
            )
            return result

        if not isinstance(plans, (list, tuple)):
            result["errors"].append(
                "plans must be a list or tuple"
            )
            return result

        if len(plans) == 0:
            return result

        for index, plan in enumerate(plans):
            normalized_plan, plan_errors = (
                self._validate_plan(plan)
            )

            if plan_errors:
                result["errors"].append({
                    "index": index,
                    "errors": deepcopy(plan_errors),
                })
                continue

            simulation = self._simulate_plan(
                normalized_plan,
                normalized_prices,
            )

            result["plans"].append(
                deepcopy(normalized_plan)
            )

            result["simulations"].append(
                deepcopy(simulation)
            )

            for layer in simulation["completed_layers"]:
                completed = deepcopy(layer)
                completed["symbol"] = (
                    simulation["symbol"]
                )
                result["completed"].append(completed)

            for layer in simulation["open_layers"]:
                opened = deepcopy(layer)
                opened["symbol"] = simulation["symbol"]
                result["open"].append(opened)

        return deepcopy(result)

    def process(self, plans, prices):
        """
        Alias for run().
        """

        return self.run(plans, prices)

    def execute(self, plans, prices):
        """
        Alias for run().
        """

        return self.run(plans, prices)


def simulate_grid_execution(plans, prices):
    """
    Convenience function for GridExecutionSimulator.
    """

    simulator = GridExecutionSimulator()

    return simulator.run(plans, prices)