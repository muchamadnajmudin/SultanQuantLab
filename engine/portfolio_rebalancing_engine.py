"""
==========================================
SULTAN QUANT OS
Portfolio Rebalancing Engine
==========================================

Responsibilities:

- Compare current portfolio allocation
  with target allocation
- Detect portfolio allocation drift
- Generate ADD actions
- Generate INCREASE actions
- Generate REDUCE actions
- Generate REMOVE actions
- Detect large rebalance requirements
- Preserve input immutability
- Provide stable output contract
- Provide backward compatible aliases
"""

from copy import deepcopy


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_NO_ACTION = "NO_ACTION"

STATUS_REBALANCE_REQUIRED = "REBALANCE_REQUIRED"

STATUS_WARNING = "WARNING"

STATUS_BLOCKED = "BLOCKED"


# ============================================================
# ACTION CONSTANTS
# ============================================================

ACTION_ADD = "ADD"

ACTION_INCREASE = "INCREASE"

ACTION_REDUCE = "REDUCE"

ACTION_REMOVE = "REMOVE"


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_LARGE_REBALANCE_THRESHOLD = 0.25

FLOAT_PRECISION = 10


# ============================================================
# REQUIRED CONTRACT
# ============================================================

REQUIRED_REBALANCING_KEYS = {
    "status",
    "portfolio",
    "current_allocation",
    "target_allocation",
    "actions",
    "warnings",
    "rebalance_required",
}


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0,
):
    """
    Safely convert a value to float.
    """

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return float(
            default
        )


def _normalize_weight(
    value,
):
    """
    Normalize portfolio weight.

    Floating point values are rounded to keep
    public engine output deterministic.

    Example:

        0.60 - 0.40

    becomes:

        0.2

    instead of:

        0.19999999999999996
    """

    return round(

        _safe_float(
            value
        ),

        FLOAT_PRECISION,

    )


def _normalize_allocation(
    allocation,
):
    """
    Normalize allocation into:

        {
            strategy_name: weight
        }

    Supported dictionary format:

        {
            "strategy_alpha": 0.50,
            "strategy_beta": 0.50,
        }

    Supported list format:

        [
            {
                "strategy": "strategy_alpha",
                "weight": 0.50,
            },
            {
                "strategy": "strategy_beta",
                "weight": 0.50,
            },
        ]

    Invalid input returns an empty dictionary.
    """

    normalized = {}

    if isinstance(
        allocation,
        dict,
    ):

        for strategy, weight in allocation.items():

            if not isinstance(
                strategy,
                str,
            ):

                continue

            normalized[
                strategy
            ] = _normalize_weight(
                weight
            )

        return normalized

    if isinstance(
        allocation,
        list,
    ):

        for item in allocation:

            if not isinstance(
                item,
                dict,
            ):

                continue

            strategy = item.get(
                "strategy"
            )

            if strategy is None:

                strategy = item.get(
                    "name"
                )

            if not isinstance(
                strategy,
                str,
            ):

                continue

            weight = item.get(
                "weight"
            )

            if weight is None:

                weight = item.get(
                    "allocation"
                )

            normalized[
                strategy
            ] = _normalize_weight(
                weight
            )

        return normalized

    return normalized


def _extract_current_allocation(
    portfolio,
):
    """
    Extract current allocation from portfolio.
    """

    if not isinstance(
        portfolio,
        dict,
    ):

        return {}

    return _normalize_allocation(

        portfolio.get(
            "allocation",
            {},
        )

    )


def _extract_target_allocation(
    portfolio,
):
    """
    Extract target allocation from portfolio.

    Primary contract:

        target_allocation

    Compatible aliases are also supported.
    """

    if not isinstance(
        portfolio,
        dict,
    ):

        return {}

    target = portfolio.get(
        "target_allocation"
    )

    if target is None:

        target = portfolio.get(
            "target"
        )

    if target is None:

        target = portfolio.get(
            "target_weights"
        )

    if target is None:

        target = portfolio.get(
            "recommended_allocation"
        )

    return _normalize_allocation(
        target
    )


def _remove_duplicates(
    values,
):
    """
    Remove duplicate values while preserving order.
    """

    result = []

    for value in values:

        if value not in result:

            result.append(
                value
            )

    return result


# ============================================================
# ACTION BUILDING
# ============================================================

def _build_action(
    strategy,
    current_weight,
    target_weight,
):
    """
    Build a single portfolio rebalancing action.

    Returns None when no rebalance is required.
    """

    current_weight = _normalize_weight(
        current_weight
    )

    target_weight = _normalize_weight(
        target_weight
    )

    drift = round(

        target_weight
        -
        current_weight,

        FLOAT_PRECISION,

    )

    if drift == 0:

        return None

    if current_weight == 0:

        action_type = ACTION_ADD

    elif target_weight == 0:

        action_type = ACTION_REMOVE

    elif drift > 0:

        action_type = ACTION_INCREASE

    else:

        action_type = ACTION_REDUCE

    return {

        "strategy":
            strategy,

        "action":
            action_type,

        "current_weight":
            current_weight,

        "target_weight":
            target_weight,

        "drift":
            drift,

    }


# ============================================================
# PORTFOLIO REBALANCING ENGINE
# ============================================================

def run_portfolio_rebalancing(
    portfolio,
    target_allocation=None,
    large_rebalance_threshold=
        DEFAULT_LARGE_REBALANCE_THRESHOLD,
):
    """
    Run portfolio rebalancing analysis.

    Parameters
    ----------

    portfolio:

        Portfolio dictionary containing current
        allocation and optionally target allocation.

    target_allocation:

        Optional explicit target allocation.

        When omitted, the engine reads:

            portfolio["target_allocation"]

        Compatible aliases are also supported.

    large_rebalance_threshold:

        Absolute drift threshold used to generate
        rebalance warnings.

    Returns
    -------

    Dictionary containing the stable contract:

        status
        portfolio
        current_allocation
        target_allocation
        actions
        warnings
        rebalance_required
    """

    # --------------------------------------------------------
    # INPUT SAFETY
    # --------------------------------------------------------

    if not isinstance(
        portfolio,
        dict,
    ):

        portfolio = {}

    portfolio_copy = deepcopy(
        portfolio
    )

    # --------------------------------------------------------
    # CURRENT ALLOCATION
    # --------------------------------------------------------

    current_allocation = _extract_current_allocation(
        portfolio_copy
    )

    # --------------------------------------------------------
    # TARGET ALLOCATION
    # --------------------------------------------------------

    if target_allocation is None:

        normalized_target_allocation = (
            _extract_target_allocation(
                portfolio_copy
            )
        )

    else:

        normalized_target_allocation = (
            _normalize_allocation(
                target_allocation
            )
        )

    # --------------------------------------------------------
    # THRESHOLD NORMALIZATION
    # --------------------------------------------------------

    normalized_threshold = abs(

        _normalize_weight(
            large_rebalance_threshold
        )

    )

    # --------------------------------------------------------
    # COLLECT ALL STRATEGIES
    # --------------------------------------------------------

    strategies = sorted(

        set(
            current_allocation.keys()
        )

        |

        set(
            normalized_target_allocation.keys()
        )

    )

    actions = []

    warnings = []

    # --------------------------------------------------------
    # BUILD REBALANCING ACTIONS
    # --------------------------------------------------------

    for strategy in strategies:

        current_weight = _normalize_weight(

            current_allocation.get(
                strategy,
                0.0,
            )

        )

        target_weight = _normalize_weight(

            normalized_target_allocation.get(
                strategy,
                0.0,
            )

        )

        action = _build_action(

            strategy,

            current_weight,

            target_weight,

        )

        if action is None:

            continue

        actions.append(
            action
        )

        absolute_drift = abs(

            _normalize_weight(
                action[
                    "drift"
                ]
            )

        )

        if (

            normalized_threshold > 0

            and

            absolute_drift
            >=
            normalized_threshold

        ):

            warnings.append(

                (
                    "Large rebalance required for "
                    f"{strategy}: "
                    f"{absolute_drift}"
                )

            )

    # --------------------------------------------------------
    # DETERMINE REBALANCING REQUIREMENT
    # --------------------------------------------------------

    rebalance_required = (

        len(
            actions
        )

        > 0

    )

    # --------------------------------------------------------
    # DETERMINE STATUS
    # --------------------------------------------------------

    if not rebalance_required:

        status = STATUS_NO_ACTION

    elif len(
        warnings
    ) > 0:

        status = STATUS_WARNING

    else:

        status = STATUS_REBALANCE_REQUIRED

    # --------------------------------------------------------
    # STABLE RESULT CONTRACT
    # --------------------------------------------------------

    result = {

        "status":
            status,

        "portfolio":
            deepcopy(
                portfolio_copy
            ),

        "current_allocation":
            deepcopy(
                current_allocation
            ),

        "target_allocation":
            deepcopy(
                normalized_target_allocation
            ),

        "actions":
            deepcopy(
                actions
            ),

        "warnings":
            _remove_duplicates(
                warnings
            ),

        "rebalance_required":
            rebalance_required,

    }

    return result


# ============================================================
# BACKWARD COMPATIBLE ALIAS
# ============================================================

def rebalance_portfolio(
    portfolio,
    target_allocation=None,
    large_rebalance_threshold=
        DEFAULT_LARGE_REBALANCE_THRESHOLD,
):
    """
    Alias for run_portfolio_rebalancing().
    """

    return run_portfolio_rebalancing(

        portfolio,

        target_allocation=
            target_allocation,

        large_rebalance_threshold=
            large_rebalance_threshold,

    )


# ============================================================
# PROCESS ALIAS
# ============================================================

def process_rebalancing(
    portfolio,
    target_allocation=None,
    large_rebalance_threshold=
        DEFAULT_LARGE_REBALANCE_THRESHOLD,
):
    """
    Alias for run_portfolio_rebalancing().
    """

    return run_portfolio_rebalancing(

        portfolio,

        target_allocation=
            target_allocation,

        large_rebalance_threshold=
            large_rebalance_threshold,

    )


# ============================================================
# OBJECT-ORIENTED WRAPPER
# ============================================================

class PortfolioRebalancingEngine:
    """
    Object-oriented wrapper for the
    Portfolio Rebalancing Engine.
    """

    def __init__(
        self,
        large_rebalance_threshold=
            DEFAULT_LARGE_REBALANCE_THRESHOLD,
    ):

        self.large_rebalance_threshold = abs(

            _normalize_weight(
                large_rebalance_threshold
            )

        )

    def run(
        self,
        portfolio,
        target_allocation=None,
    ):
        """
        Run portfolio rebalancing.
        """

        return run_portfolio_rebalancing(

            portfolio,

            target_allocation=
                target_allocation,

            large_rebalance_threshold=
                self.large_rebalance_threshold,

        )

    def rebalance(
        self,
        portfolio,
        target_allocation=None,
    ):
        """
        Alias for run().
        """

        return self.run(

            portfolio,

            target_allocation=
                target_allocation,

        )