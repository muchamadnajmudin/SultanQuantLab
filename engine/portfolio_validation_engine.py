"""
==================================================
SULTAN QUANT OS
Portfolio Validation Engine
Version : 1.0.0
==================================================

Responsibilities:

- Validate institutional portfolio contract
- Validate portfolio composition
- Validate allocation consistency
- Validate portfolio exposure
- Validate portfolio risk
- Validate institutional decision readiness
- Preserve backward compatibility
- Never crash the institutional pipeline

Architecture:

Institutional Portfolio Result
            |
            v
Portfolio Contract Validation
            |
            +--> Portfolio Integrity
            |
            +--> Allocation Validation
            |
            +--> Exposure Validation
            |
            +--> Risk Validation
            |
            +--> Decision Validation
            |
            v
Validation Result
"""

from copy import deepcopy


# ============================================================
# VALIDATION STATUS
# ============================================================

STATUS_VALID = "VALID"
STATUS_INVALID = "INVALID"
STATUS_WARNING = "WARNING"


# ============================================================
# PORTFOLIO EVALUATION STATUS
# ============================================================

STRATEGY_STATUS_SUCCESS = "SUCCESS"


# ============================================================
# REQUIRED TOP LEVEL CONTRACT
# ============================================================

REQUIRED_PORTFOLIO_KEYS = (
    "regime",
    "portfolio",
    "best",
    "allocation",
    "risk",
    "decision",
    "exposure",
    "summary",
)


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_float(
    value,
    default=0.0,
):
    """
    Safely convert a value to float.
    """

    try:

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_dict(
    value,
):
    """
    Return a dictionary or an empty dictionary.
    """

    if isinstance(
        value,
        dict,
    ):

        return value

    return {}


def _safe_list(
    value,
):
    """
    Return a list or an empty list.
    """

    if isinstance(
        value,
        list,
    ):

        return value

    return []


# ============================================================
# EMPTY VALIDATION RESULT
# ============================================================

def _empty_validation_result():
    """
    Return the stable empty validation contract.
    """

    return {

        "status":
            STATUS_VALID,

        "valid":
            True,

        "errors":
            [],

        "warnings":
            [],

        "checks":
            {},

        "summary":
            {},

    }


# ============================================================
# VALIDATION MESSAGE
# ============================================================

def _add_error(
    result,
    message,
):
    """
    Add a validation error.
    """

    result[
        "errors"
    ].append(
        str(message)
    )

    result[
        "valid"
    ] = False

    result[
        "status"
    ] = STATUS_INVALID


def _add_warning(
    result,
    message,
):
    """
    Add a validation warning.
    """

    result[
        "warnings"
    ].append(
        str(message)
    )

    if result[
        "status"
    ] == STATUS_VALID:

        result[
            "status"
        ] = STATUS_WARNING


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_portfolio_contract(
    portfolio_result,
):
    """
    Validate the top-level Institutional Portfolio contract.

    Required keys:

        - regime
        - portfolio
        - best
        - allocation
        - risk
        - decision
        - exposure
        - summary

    Returns
    -------

    dict

        {
            "valid": bool,
            "missing_keys": list,
        }
    """

    if not isinstance(
        portfolio_result,
        dict,
    ):

        return {

            "valid":
                False,

            "missing_keys":
                list(
                    REQUIRED_PORTFOLIO_KEYS
                ),

        }

    missing_keys = [

        key

        for key in REQUIRED_PORTFOLIO_KEYS

        if key not in portfolio_result

    ]

    return {

        "valid":
            len(
                missing_keys
            )
            == 0,

        "missing_keys":
            missing_keys,

    }


# ============================================================
# PORTFOLIO VALIDATION
# ============================================================

def validate_portfolio_items(
    portfolio,
):
    """
    Validate portfolio strategy items.

    A portfolio item must be a dictionary.

    Strategies with FAILED / INSUFFICIENT_DATA status are
    allowed to remain inside the portfolio result because
    they are part of the diagnostic contract.

    Returns
    -------

    dict

        {
            "valid": bool,
            "total": int,
            "successful": int,
            "failed": int,
            "invalid_items": int,
        }
    """

    portfolio = _safe_list(
        portfolio
    )

    total = len(
        portfolio
    )

    successful = 0

    failed = 0

    invalid_items = 0

    for item in portfolio:

        if not isinstance(
            item,
            dict,
        ):

            invalid_items += 1

            continue

        status = item.get(
            "evaluation_status",
            STRATEGY_STATUS_SUCCESS,
        )

        if status == STRATEGY_STATUS_SUCCESS:

            successful += 1

        else:

            failed += 1

    return {

        "valid":
            invalid_items == 0,

        "total":
            total,

        "successful":
            successful,

        "failed":
            failed,

        "invalid_items":
            invalid_items,

    }


# ============================================================
# ALLOCATION NORMALIZATION
# ============================================================

def _normalize_allocation(
    allocation,
):
    """
    Normalize allocation into a list of dictionaries.

    Supported formats:

        [
            {
                "name": "...",
                "allocation": 0.5,
            }
        ]

    or:

        {
            "strategy_a": 0.5,
            "strategy_b": 0.5,
        }
    """

    if isinstance(
        allocation,
        dict,
    ):

        normalized = []

        for name, value in allocation.items():

            normalized.append(

                {

                    "name":
                        name,

                    "allocation":
                        _safe_float(
                            value,
                            0.0,
                        ),

                }

            )

        return normalized

    if not isinstance(
        allocation,
        list,
    ):

        return []

    normalized = []

    for item in allocation:

        if not isinstance(
            item,
            dict,
        ):

            continue

        normalized_item = deepcopy(
            item
        )

        allocation_value = normalized_item.get(
            "allocation",
            normalized_item.get(
                "weight",
                0.0,
            ),
        )

        normalized_item[
            "allocation"
        ] = _safe_float(
            allocation_value,
            0.0,
        )

        normalized.append(
            normalized_item
        )

    return normalized


# ============================================================
# ALLOCATION VALIDATION
# ============================================================

def validate_allocation(
    allocation,
    tolerance=0.0001,
):
    """
    Validate portfolio allocation.

    Rules:

        - Allocation must not be negative
        - Empty allocation is allowed
        - Non-empty allocation should sum to approximately 1.0

    Returns
    -------

    dict

        {
            "valid": bool,
            "total_allocation": float,
            "negative_items": int,
            "count": int,
        }
    """

    allocation = _normalize_allocation(
        allocation
    )

    count = len(
        allocation
    )

    negative_items = 0

    total_allocation = 0.0

    for item in allocation:

        value = _safe_float(
            item.get(
                "allocation",
                0.0,
            ),
            0.0,
        )

        if value < 0:

            negative_items += 1

        total_allocation += value

    total_allocation = round(
        total_allocation,
        10,
    )

    if count == 0:

        return {

            "valid":
                True,

            "total_allocation":
                0.0,

            "negative_items":
                0,

            "count":
                0,

        }

    valid = (

        negative_items == 0

        and

        abs(
            total_allocation
            -
            1.0
        )
        <= tolerance

    )

    return {

        "valid":
            valid,

        "total_allocation":
            total_allocation,

        "negative_items":
            negative_items,

        "count":
            count,

    }


# ============================================================
# EXPOSURE VALIDATION
# ============================================================

def validate_exposure(
    allocation,
    exposure,
    tolerance=0.0001,
):
    """
    Validate reported exposure against normalized allocation.
    """

    allocation = _normalize_allocation(
        allocation
    )

    calculated_exposure = round(

        sum(

            _safe_float(
                item.get(
                    "allocation",
                    0.0,
                ),
                0.0,
            )

            for item in allocation

        ),

        10,

    )

    reported_exposure = _safe_float(
        exposure,
        0.0,
    )

    valid = (

        abs(
            calculated_exposure
            -
            reported_exposure
        )
        <= tolerance

    )

    return {

        "valid":
            valid,

        "calculated_exposure":
            calculated_exposure,

        "reported_exposure":
            reported_exposure,

    }


# ============================================================
# RISK VALIDATION
# ============================================================

def validate_risk(
    risk,
):
    """
    Validate portfolio risk result.

    Empty risk is allowed because an empty portfolio may not
    produce a risk calculation.
    """

    risk = _safe_dict(
        risk
    )

    if not risk:

        return {

            "valid":
                True,

            "empty":
                True,

        }

    risk_score = risk.get(
        "risk_score",
        None,
    )

    if risk_score is None:

        return {

            "valid":
                True,

            "empty":
                False,

        }

    risk_score = _safe_float(
        risk_score,
        -1.0,
    )

    return {

        "valid":
            risk_score >= 0.0,

        "empty":
            False,

    }


# ============================================================
# DECISION VALIDATION
# ============================================================

def validate_decision(
    decision,
):
    """
    Validate institutional decision result.

    Empty decision is allowed for backward compatibility and
    safe pipeline behavior.
    """

    decision = _safe_dict(
        decision
    )

    if not decision:

        return {

            "valid":
                True,

            "empty":
                True,

            "status":
                None,

        }

    status = decision.get(
        "status",
        None,
    )

    return {

        "valid":
            True,

        "empty":
            False,

        "status":
            status,

    }


# ============================================================
# BEST STRATEGY VALIDATION
# ============================================================

def validate_best_strategy(
    portfolio,
    best,
):
    """
    Validate that the selected best strategy is consistent with
    the normalized portfolio.

    Empty best is allowed when no successful strategy exists.
    """

    portfolio = _safe_list(
        portfolio
    )

    successful = [

        item

        for item in portfolio

        if isinstance(
            item,
            dict,
        )

        and

        item.get(
            "evaluation_status",
            STRATEGY_STATUS_SUCCESS,
        )
        == STRATEGY_STATUS_SUCCESS

    ]

    if best is None:

        return {

            "valid":
                len(
                    successful
                )
                == 0,

            "has_best":
                False,

        }

    if not isinstance(
        best,
        dict,
    ):

        return {

            "valid":
                False,

            "has_best":
                True,

        }

    best_name = best.get(
        "name",
        None,
    )

    if best_name is None:

        return {

            "valid":
                False,

            "has_best":
                True,

        }

    successful_names = {

        item.get(
            "name",
            None,
        )

        for item in successful

    }

    return {

        "valid":
            best_name
            in
            successful_names,

        "has_best":
            True,

    }


# ============================================================
# MAIN VALIDATION ENGINE
# ============================================================

def validate_institutional_portfolio(
    portfolio_result,
):
    """
    Validate the complete Institutional Portfolio result.

    This function is intentionally non-destructive.

    It never modifies the supplied portfolio result and always
    returns a stable validation contract.

    Returns
    -------

    {
        "status": "VALID" | "WARNING" | "INVALID",
        "valid": bool,
        "errors": [],
        "warnings": [],
        "checks": {},
        "summary": {},
    }
    """

    result = _empty_validation_result()

    # ========================================================
    # CONTRACT
    # ========================================================

    contract = validate_portfolio_contract(
        portfolio_result
    )

    result[
        "checks"
    ][
        "contract"
    ] = contract

    if not contract[
        "valid"
    ]:

        _add_error(

            result,

            "Missing required portfolio contract keys: "
            +
            ", ".join(
                contract[
                    "missing_keys"
                ]
            ),

        )

        result[
            "summary"
        ] = {

            "portfolio_items":
                0,

            "successful_strategies":
                0,

            "allocation_count":
                0,

            "exposure":
                0.0,

        }

        return result

    # ========================================================
    # SAFE COMPONENTS
    # ========================================================

    portfolio = _safe_list(
        portfolio_result.get(
            "portfolio",
            [],
        )
    )

    allocation = portfolio_result.get(
        "allocation",
        [],
    )

    exposure = portfolio_result.get(
        "exposure",
        0.0,
    )

    risk = portfolio_result.get(
        "risk",
        {},
    )

    decision = portfolio_result.get(
        "decision",
        {},
    )

    best = portfolio_result.get(
        "best",
        None,
    )

    # ========================================================
    # PORTFOLIO
    # ========================================================

    portfolio_check = validate_portfolio_items(
        portfolio
    )

    result[
        "checks"
    ][
        "portfolio"
    ] = portfolio_check

    if not portfolio_check[
        "valid"
    ]:

        _add_error(

            result,

            "Portfolio contains invalid strategy items.",

        )

    # ========================================================
    # ALLOCATION
    # ========================================================

    allocation_check = validate_allocation(
        allocation
    )

    result[
        "checks"
    ][
        "allocation"
    ] = allocation_check

    if not allocation_check[
        "valid"
    ]:

        _add_error(

            result,

            "Portfolio allocation is invalid.",

        )

    # ========================================================
    # EXPOSURE
    # ========================================================

    exposure_check = validate_exposure(
        allocation,
        exposure,
    )

    result[
        "checks"
    ][
        "exposure"
    ] = exposure_check

    if not exposure_check[
        "valid"
    ]:

        _add_error(

            result,

            "Reported exposure does not match allocation.",

        )

    # ========================================================
    # RISK
    # ========================================================

    risk_check = validate_risk(
        risk
    )

    result[
        "checks"
    ][
        "risk"
    ] = risk_check

    if not risk_check[
        "valid"
    ]:

        _add_error(

            result,

            "Portfolio risk is invalid.",

        )

    # ========================================================
    # DECISION
    # ========================================================

    decision_check = validate_decision(
        decision
    )

    result[
        "checks"
    ][
        "decision"
    ] = decision_check

    if not decision_check[
        "valid"
    ]:

        _add_error(

            result,

            "Portfolio decision is invalid.",

        )

    # ========================================================
    # BEST STRATEGY
    # ========================================================

    best_check = validate_best_strategy(
        portfolio,
        best,
    )

    result[
        "checks"
    ][
        "best"
    ] = best_check

    if not best_check[
        "valid"
    ]:

        _add_error(

            result,

            "Best strategy is inconsistent with portfolio.",

        )

    # ========================================================
    # WARNINGS
    # ========================================================

    if (
        portfolio_check[
            "total"
        ]
        > 0

        and

        portfolio_check[
            "successful"
        ]
        == 0
    ):

        _add_warning(

            result,

            "Portfolio contains no successful strategy.",

        )

    if (

        portfolio_check[
            "successful"
        ]
        > 0

        and

        allocation_check[
            "count"
        ]
        == 0
    ):

        _add_warning(

            result,

            "Successful strategies exist but no capital allocation was produced.",

        )

    # ========================================================
    # SUMMARY
    # ========================================================

    result[
        "summary"
    ] = {

        "portfolio_items":
            portfolio_check[
                "total"
            ],

        "successful_strategies":
            portfolio_check[
                "successful"
            ],

        "failed_strategies":
            portfolio_check[
                "failed"
            ],

        "allocation_count":
            allocation_check[
                "count"
            ],

        "allocation_total":
            allocation_check[
                "total_allocation"
            ],

        "exposure":
            exposure_check[
                "reported_exposure"
            ],

    }

    return result


# ============================================================
# BACKWARD / FRIENDLY ALIAS
# ============================================================

def validate_portfolio(
    portfolio_result,
):
    """
    Backward-friendly alias for the main validation engine.
    """

    return validate_institutional_portfolio(
        portfolio_result
    )


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "STATUS_VALID",

    "STATUS_INVALID",

    "STATUS_WARNING",

    "REQUIRED_PORTFOLIO_KEYS",

    "validate_portfolio_contract",

    "validate_portfolio_items",

    "validate_allocation",

    "validate_exposure",

    "validate_risk",

    "validate_decision",

    "validate_best_strategy",

    "validate_institutional_portfolio",

    "validate_portfolio",

]