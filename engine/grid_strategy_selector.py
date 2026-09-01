"""
==========================================
SULTAN QUANT OS
Module : Grid Strategy Selector
Version : 1.1.1
==========================================

Responsibilities
----------------
- Select the best grid strategies from ranked strategy results.
- Accept the official Grid Strategy Ranker contract.
- Preserve strategy ranking and complete strategy data.
- Support configurable top_n selection.
- Reject invalid strategy containers safely.
- Reject invalid strategy records safely.
- Preserve input immutability.
- Return independent result objects.
- Provide backward-compatible aliases:
    run()
    process()
    execute()

Selection priority
------------------
1. Valid strategy records only.
2. Existing rank is preserved when available.
3. Existing score is preserved.
4. Existing order is used as a stable fallback.
5. top_n controls the number of selected strategies.

Official Ranker compatibility
-----------------------------
The Grid Strategy Ranker produces strategy records containing:

    rank
    symbol
    score
    performance_score
    risk_score
    performance
    risk
    analysis

The selector therefore treats `symbol` as the primary strategy
identity field while retaining backward compatibility with:

    name
    strategy
    id

This module does NOT:
- execute trades
- modify grid plans
- perform backtesting
- calculate risk
- place live orders
"""

from __future__ import annotations

from copy import deepcopy


# ============================================================
# ENGINE
# ============================================================

class GridStrategySelector:
    """
    Select top grid strategies from ranked strategy results.
    """

    STATUS_SUCCESS = "SUCCESS"
    STATUS_EMPTY = "EMPTY"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_ERROR = "ERROR"

    DEFAULT_TOP_N = 1

    def __init__(
        self,
        top_n: int = DEFAULT_TOP_N,
    ):
        if isinstance(top_n, bool):
            raise ValueError(
                "top_n must be a positive integer"
            )

        if not isinstance(top_n, int):
            raise ValueError(
                "top_n must be a positive integer"
            )

        if top_n <= 0:
            raise ValueError(
                "top_n must be a positive integer"
            )

        self.top_n = top_n

    # ============================================================
    # PUBLIC API
    # ============================================================

    def run(
        self,
        strategies,
        top_n=None,
    ):
        """
        Select top grid strategies.

        Parameters
        ----------
        strategies : list or tuple
            Ranked strategy dictionaries.

        top_n : int, optional
            Runtime selection limit.

        Returns
        -------
        dict
            Stable selector result.
        """

        original_strategies = deepcopy(
            strategies
        )

        result = self._build_empty_result()

        # --------------------------------------------------------
        # Validate container
        # --------------------------------------------------------

        if strategies is None:
            result["status"] = self.STATUS_EMPTY
            result["errors"].append(
                "strategies is None"
            )
            result["input"] = original_strategies

            return deepcopy(result)

        if not isinstance(
            strategies,
            (list, tuple),
        ):
            result["status"] = self.STATUS_ERROR
            result["errors"].append(
                "strategies must be a list or tuple"
            )
            result["input"] = original_strategies

            return deepcopy(result)

        if not strategies:
            result["status"] = self.STATUS_EMPTY
            result["input"] = original_strategies

            return deepcopy(result)

        # --------------------------------------------------------
        # Resolve top_n
        # --------------------------------------------------------

        resolved_top_n = self._resolve_top_n(
            top_n
        )

        if resolved_top_n is None:
            result["status"] = self.STATUS_ERROR
            result["errors"].append(
                "top_n must be a positive integer"
            )
            result["input"] = original_strategies

            return deepcopy(result)

        result["top_n"] = resolved_top_n

        # --------------------------------------------------------
        # Validate and normalize strategy records
        # --------------------------------------------------------

        valid_strategies = []
        invalid_errors = []

        for index, strategy in enumerate(
            strategies
        ):
            # IMPORTANT:
            #
            # processed_count represents actual dictionary
            # strategy records entering validation.
            #
            # Non-dictionary values such as:
            #     None
            #     "invalid"
            #     123
            #
            # are invalid input records but are not counted as
            # processed strategies.
            if not isinstance(
                strategy,
                dict,
            ):
                invalid_errors.append(
                    {
                        "index": index,
                        "errors": self._strategy_errors(
                            strategy,
                            index,
                        ),
                    }
                )

                continue

            result["processed_count"] += 1

            normalized = self._validate_strategy(
                strategy,
                index,
            )

            if normalized is None:
                invalid_errors.append(
                    {
                        "index": index,
                        "errors": self._strategy_errors(
                            strategy,
                            index,
                        ),
                    }
                )

                continue

            valid_strategies.append(
                normalized
            )

        result["failed_count"] = len(
            invalid_errors
        )

        result["errors"] = deepcopy(
            invalid_errors
        )

        # --------------------------------------------------------
        # Nothing valid
        # --------------------------------------------------------

        if not valid_strategies:
            result["status"] = self.STATUS_EMPTY
            result["input"] = original_strategies

            return deepcopy(result)

        # --------------------------------------------------------
        # Ensure stable ranking
        # --------------------------------------------------------

        ranked = self._rank_for_selection(
            valid_strategies
        )

        # --------------------------------------------------------
        # Select top N
        # --------------------------------------------------------

        selected = ranked[
            :resolved_top_n
        ]

        selected = deepcopy(
            selected
        )

        # --------------------------------------------------------
        # Add selection metadata
        # --------------------------------------------------------

        for selection_rank, strategy in enumerate(
            selected,
            start=1,
        ):
            strategy["selection_rank"] = (
                selection_rank
            )

        # --------------------------------------------------------
        # Result
        # --------------------------------------------------------

        result["strategies"] = deepcopy(
            ranked
        )

        result["selected_strategies"] = deepcopy(
            selected
        )

        result["ranked_count"] = len(
            ranked
        )

        result["selected_count"] = len(
            selected
        )

        # --------------------------------------------------------
        # Status
        # --------------------------------------------------------

        if result["failed_count"] > 0:
            result["status"] = self.STATUS_PARTIAL
        else:
            result["status"] = self.STATUS_SUCCESS

        result["input"] = original_strategies

        return deepcopy(result)

    # ============================================================
    # PROCESS ALIAS
    # ============================================================

    def process(
        self,
        strategies,
        top_n=None,
    ):
        """
        Alias for run().
        """

        return self.run(
            strategies,
            top_n=top_n,
        )

    # ============================================================
    # EXECUTE ALIAS
    # ============================================================

    def execute(
        self,
        strategies,
        top_n=None,
    ):
        """
        Alias for run().
        """

        return self.run(
            strategies,
            top_n=top_n,
        )

    # ============================================================
    # TOP N
    # ============================================================

    def _resolve_top_n(
        self,
        top_n,
    ):
        """
        Resolve constructor or runtime top_n.

        Runtime top_n overrides constructor top_n
        when explicitly supplied.
        """

        if top_n is None:
            return self.top_n

        if isinstance(
            top_n,
            bool,
        ):
            return None

        if not isinstance(
            top_n,
            int,
        ):
            return None

        if top_n <= 0:
            return None

        return top_n

    # ============================================================
    # STRATEGY VALIDATION
    # ============================================================

    def _validate_strategy(
        self,
        strategy,
        index,
    ):
        """
        Validate a single strategy safely.

        Official Ranker output uses `symbol` as identity.

        Backward-compatible identity fields:
            symbol
            name
            strategy
            id
        """

        if not isinstance(
            strategy,
            dict,
        ):
            return None

        data = deepcopy(
            strategy
        )

        # --------------------------------------------------------
        # Strategy identity
        # --------------------------------------------------------

        identity = self._extract_identity(
            data
        )

        if identity is None:
            return None

        # --------------------------------------------------------
        # Official symbol handling
        # --------------------------------------------------------

        if "symbol" in data:
            symbol = data.get(
                "symbol"
            )

            if not isinstance(
                symbol,
                str,
            ):
                return None

            symbol = symbol.strip()

            if not symbol:
                return None

            data["symbol"] = symbol

        else:
            data["symbol"] = identity

        # --------------------------------------------------------
        # Backward-compatible name handling
        # --------------------------------------------------------
        #
        # IMPORTANT:
        # Always normalize the existing name.
        #
        # This fixes cases such as:
        #
        #     "  Grid Alpha  "
        #
        # becoming:
        #
        #     "Grid Alpha"
        #
        # without modifying the original input object.
        #

        if "name" in data:

            name = data.get(
                "name"
            )

            if not isinstance(
                name,
                str,
            ):
                return None

            name = name.strip()

            if not name:
                return None

            data["name"] = name

        else:
            data["name"] = identity

        # --------------------------------------------------------
        # Score
        # --------------------------------------------------------

        score = data.get(
            "score",
            data.get(
                "grid_score",
                None,
            ),
        )

        if score is None:
            return None

        if isinstance(
            score,
            bool,
        ):
            return None

        try:
            score = float(score)
        except (
            TypeError,
            ValueError,
        ):
            return None

        data["score"] = score

        # --------------------------------------------------------
        # Rank
        # --------------------------------------------------------

        if "rank" in data:

            rank = data["rank"]

            if isinstance(
                rank,
                bool,
            ):
                return None

            if not isinstance(
                rank,
                int,
            ):
                return None

            if rank <= 0:
                return None

        else:
            data["rank"] = index + 1

        # --------------------------------------------------------
        # Ranker output integrity
        # --------------------------------------------------------
        #
        # Ranker officially supplies performance/risk/analysis.
        # Selector preserves these objects but does not
        # recalculate them.
        #
        # They remain optional here for compatibility with
        # simpler selector consumers.
        #

        if "performance" in data:

            if not isinstance(
                data["performance"],
                dict,
            ):
                return None

        if "risk" in data:

            if not isinstance(
                data["risk"],
                dict,
            ):
                return None

        if "analysis" in data:

            if not isinstance(
                data["analysis"],
                dict,
            ):
                return None

        return data

    # ============================================================
    # IDENTITY EXTRACTION
    # ============================================================

    @staticmethod
    def _extract_identity(
        strategy,
    ):
        """
        Extract strategy identity.

        Priority:
            symbol
            name
            strategy
            id
        """

        candidates = (
            "symbol",
            "name",
            "strategy",
            "id",
        )

        for key in candidates:

            value = strategy.get(
                key
            )

            if isinstance(
                value,
                str,
            ):

                value = value.strip()

                if value:
                    return value

        return None

    # ============================================================
    # ERROR REPORTING
    # ============================================================

    def _strategy_errors(
        self,
        strategy,
        index,
    ):
        """
        Return structured validation errors.
        """

        errors = []

        # --------------------------------------------------------
        # Container
        # --------------------------------------------------------

        if not isinstance(
            strategy,
            dict,
        ):

            errors.append(
                "strategy must be a dictionary"
            )

            return errors

        # --------------------------------------------------------
        # Identity
        # --------------------------------------------------------

        identity = self._extract_identity(
            strategy
        )

        if identity is None:

            errors.append(
                "strategy identity must contain "
                "a non-empty symbol, name, strategy, or id"
            )

        # --------------------------------------------------------
        # Score
        # --------------------------------------------------------

        score = strategy.get(
            "score",
            strategy.get(
                "grid_score",
                None,
            ),
        )

        if score is None:

            errors.append(
                "score is required"
            )

        elif isinstance(
            score,
            bool,
        ):

            errors.append(
                "score must be numeric"
            )

        else:

            try:
                float(score)

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    "score must be numeric"
                )

        # --------------------------------------------------------
        # Rank
        # --------------------------------------------------------

        if "rank" in strategy:

            rank = strategy["rank"]

            if isinstance(
                rank,
                bool,
            ):

                errors.append(
                    "rank must be a positive integer"
                )

            elif not isinstance(
                rank,
                int,
            ):

                errors.append(
                    "rank must be a positive integer"
                )

            elif rank <= 0:

                errors.append(
                    "rank must be a positive integer"
                )

        # --------------------------------------------------------
        # Performance
        # --------------------------------------------------------

        if "performance" in strategy:

            if not isinstance(
                strategy["performance"],
                dict,
            ):

                errors.append(
                    "performance must be a dictionary"
                )

        # --------------------------------------------------------
        # Risk
        # --------------------------------------------------------

        if "risk" in strategy:

            if not isinstance(
                strategy["risk"],
                dict,
            ):

                errors.append(
                    "risk must be a dictionary"
                )

        # --------------------------------------------------------
        # Analysis
        # --------------------------------------------------------

        if "analysis" in strategy:

            if not isinstance(
                strategy["analysis"],
                dict,
            ):

                errors.append(
                    "analysis must be a dictionary"
                )

        # --------------------------------------------------------
        # Fallback error
        # --------------------------------------------------------

        if not errors:

            errors.append(
                f"invalid strategy at index {index}"
            )

        return errors

    # ============================================================
    # RANKING
    # ============================================================

    def _rank_for_selection(
        self,
        strategies,
    ):
        """
        Produce stable selection order.

        Existing rank is the primary ordering field.
        Score is the secondary ordering field.
        Original list position is the final stable tie-breaker.
        """

        prepared = []

        for index, strategy in enumerate(
            strategies
        ):

            item = deepcopy(
                strategy
            )

            rank = item.get(
                "rank",
                index + 1,
            )

            score = item.get(
                "score",
                0,
            )

            prepared.append(
                (
                    rank,
                    -self._safe_float(
                        score
                    ),
                    index,
                    item,
                )
            )

        prepared.sort(
            key=lambda value: (
                value[0],
                value[1],
                value[2],
            )
        )

        ranked = []

        for rank_position, item_data in enumerate(
            prepared,
            start=1,
        ):

            item = deepcopy(
                item_data[3]
            )

            # Preserve original rank.
            item["source_rank"] = item.get(
                "rank",
                rank_position,
            )

            # Assign normalized ranking position.
            item["rank"] = rank_position

            ranked.append(
                item
            )

        return deepcopy(
            ranked
        )

    # ============================================================
    # SAFE FLOAT
    # ============================================================

    @staticmethod
    def _safe_float(
        value,
        default=0.0,
    ):
        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

    # ============================================================
    # RESULT CONTRACT
    # ============================================================

    def _build_empty_result(
        self,
    ):
        """
        Build stable result contract.
        """

        return {
            "status": self.STATUS_EMPTY,
            "strategies": [],
            "selected_strategies": [],
            "processed_count": 0,
            "failed_count": 0,
            "ranked_count": 0,
            "selected_count": 0,
            "top_n": self.top_n,
            "errors": [],
            "input": None,
        }


# ============================================================
# CONVENIENCE FUNCTION
# ============================================================

def select_grid_strategies(
    strategies,
    top_n=GridStrategySelector.DEFAULT_TOP_N,
):
    """
    Convenience function for selecting grid strategies.
    """

    selector = GridStrategySelector(
        top_n=top_n,
    )

    return selector.run(
        strategies
    )


# ============================================================
# BACKWARD-COMPATIBLE ALIAS
# ============================================================

GridStrategySelectorEngine = (
    GridStrategySelector
)


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [
    "GridStrategySelector",
    "GridStrategySelectorEngine",
    "select_grid_strategies",
]