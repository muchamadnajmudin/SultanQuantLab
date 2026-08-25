"""
==========================================
SULTAN QUANT OS
Portfolio Validation Engine
Version : 1.3.0
==========================================

Responsibilities:

- Validate institutional portfolio contracts
- Validate portfolio strategy results
- Validate allocation safely
- Validate exposure consistency
- Validate risk contract
- Validate decision contract
- Validate best strategy consistency
- Preserve backward compatibility
- Never mutate caller-owned input
- Fail safely on invalid input

Architecture:

Institutional Portfolio
        +
Contract Validation
        +
Portfolio Validation
        +
Allocation Validation
        +
Exposure Validation
        +
Risk Validation
        +
Decision Validation
        +
Best Strategy Validation
        ↓
VALID / WARNING / INVALID
"""

from copy import deepcopy


# ============================================================
# VALIDATION STATUS
# ============================================================

STATUS_VALID = "VALID"

STATUS_WARNING = "WARNING"

STATUS_INVALID = "INVALID"


# ============================================================
# PORTFOLIO CONTRACT
# ============================================================

REQUIRED_PORTFOLIO_KEYS = (

    "portfolio",

    "allocation",

    "exposure",

    "risk",

    "decision",

    "best",

    "regime",

    "summary",

)


STRUCTURAL_PORTFOLIO_KEYS = (

    "portfolio",

    "allocation",

    "exposure",

    "risk",

    "decision",

    "best",

)


COMPATIBLE_PORTFOLIO_KEYS = (

    "regime",

    "summary",

)


# ============================================================
# VALIDATION CONTRACT
# ============================================================

REQUIRED_VALIDATION_KEYS = (

    "status",

    "valid",

    "errors",

    "warnings",

    "checks",

    "summary",

)


# ============================================================
# SAFE HELPERS
# ============================================================

def _safe_dict(
    value,
):

    if isinstance(
        value,
        dict,
    ):

        return deepcopy(
            value
        )

    return {}


def _safe_list(
    value,
):

    if isinstance(
        value,
        list,
    ):

        return deepcopy(
            value
        )

    if isinstance(
        value,
        tuple,
    ):

        return list(
            deepcopy(
                value
            )
        )

    return []


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


def _safe_string(
    value,
    default="",
):

    if value is None:

        return default

    try:

        return str(
            value
        )

    except Exception:

        return default


def _append_unique(
    target,
    value,
):

    value = _safe_string(
        value,
        "",
    ).strip()

    if not value:

        return

    if value not in target:

        target.append(
            value
        )


def _strategy_name(
    strategy,
):

    if isinstance(
        strategy,
        str,
    ):

        return strategy.strip()

    if not isinstance(
        strategy,
        dict,
    ):

        return ""

    name = strategy.get(
        "name",
        strategy.get(
            "strategy",
            "",
        ),
    )

    return _safe_string(
        name,
        "",
    ).strip()


def _strategy_status(
    strategy,
):
    """
    Extract normalized strategy status.

    Supported fields:

    - evaluation_status
    - status

    evaluation_status has priority because it is used
    by the institutional portfolio strategy result.
    """

    if not isinstance(
        strategy,
        dict,
    ):

        return STATUS_INVALID

    status = strategy.get(
        "evaluation_status",
        strategy.get(
            "status",
            None,
        ),
    )

    if status is None:

        return "SUCCESS"

    return _safe_string(
        status,
        "",
    ).upper().strip()


def _is_successful_strategy(
    strategy,
):

    status = _strategy_status(
        strategy
    )

    return status in (

        "SUCCESS",

        "SUCCEEDED",

        "VALID",

        "APPROVED",

        "OK",

        "PASSED",

        "PASS",

    )


def _is_failed_strategy(
    strategy,
):

    status = _strategy_status(
        strategy
    )

    return status in (

        "FAILED",

        "FAIL",

        "ERROR",

        "INVALID",

        "BLOCKED",

        "REJECTED",

    )


# ============================================================
# ALLOCATION NORMALIZATION
# ============================================================

def _normalize_allocation(
    allocation,
):
    """
    Normalize supported allocation formats.

    Supported:

    List format:

        [
            {
                "name": "strategy_a",
                "allocation": 0.6,
            }
        ]

    Dictionary mapping:

        {
            "strategy_a": 0.6,
            "strategy_b": 0.4,
        }
    """

    if allocation is None:

        return []

    if isinstance(
        allocation,
        list,
    ):

        return deepcopy(
            allocation
        )

    if isinstance(
        allocation,
        tuple,
    ):

        return list(
            deepcopy(
                allocation
            )
        )

    if isinstance(
        allocation,
        dict,
    ):

        normalized = []

        for name, value in allocation.items():

            if isinstance(
                value,
                dict,
            ):

                item = deepcopy(
                    value
                )

                if (

                    "name"
                    not in
                    item

                    and

                    "strategy"
                    not in
                    item

                ):

                    item[
                        "name"
                    ] = name

                normalized.append(
                    item
                )

            else:

                normalized.append(

                    {

                        "name":
                            name,

                        "allocation":
                            value,

                    }

                )

        return normalized

    return None


# ============================================================
# CONTRACT VALIDATION
# ============================================================

def validate_portfolio_contract(
    portfolio,
):

    if not isinstance(
        portfolio,
        dict,
    ):

        return {

            "valid":
                False,

            "missing_keys":
                list(
                    REQUIRED_PORTFOLIO_KEYS
                ),

            "structural_missing_keys":
                list(
                    STRUCTURAL_PORTFOLIO_KEYS
                ),

            "compatible_missing_keys":
                list(
                    COMPATIBLE_PORTFOLIO_KEYS
                ),

        }

    missing_keys = []

    structural_missing_keys = []

    compatible_missing_keys = []

    for key in REQUIRED_PORTFOLIO_KEYS:

        if key not in portfolio:

            missing_keys.append(
                key
            )

    for key in STRUCTURAL_PORTFOLIO_KEYS:

        if key not in portfolio:

            structural_missing_keys.append(
                key
            )

    for key in COMPATIBLE_PORTFOLIO_KEYS:

        if key not in portfolio:

            compatible_missing_keys.append(
                key
            )

    return {

        "valid":
            len(
                structural_missing_keys
            )
            == 0,

        "missing_keys":
            missing_keys,

        "structural_missing_keys":
            structural_missing_keys,

        "compatible_missing_keys":
            compatible_missing_keys,

    }


# ============================================================
# PORTFOLIO ITEM VALIDATION
# ============================================================

def validate_portfolio_items(
    portfolio_items,
):

    if not isinstance(
        portfolio_items,
        list,
    ):

        return {

            "valid":
                False,

            "total":
                0,

            "successful":
                0,

            "failed":
                0,

            "invalid_items":
                1,

        }

    successful = 0

    failed = 0

    invalid_items = 0

    for item in portfolio_items:

        if not isinstance(
            item,
            dict,
        ):

            invalid_items += 1

            continue

        if _is_successful_strategy(
            item
        ):

            successful += 1

        else:

            failed += 1

    return {

        "valid":
            invalid_items == 0,

        "total":
            len(
                portfolio_items
            ),

        "successful":
            successful,

        "failed":
            failed,

        "invalid_items":
            invalid_items,

    }


# ============================================================
# ALLOCATION VALIDATION
# ============================================================

def validate_allocation(
    allocation,
):

    normalized = _normalize_allocation(
        allocation
    )

    if normalized is None:

        return {

            "valid":
                False,

            "total_allocation":
                0.0,

            "negative_items":
                0,

            "count":
                0,

        }

    if not normalized:

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

    total_allocation = 0.0

    negative_items = 0

    invalid_items = 0

    for item in normalized:

        if not isinstance(
            item,
            dict,
        ):

            invalid_items += 1

            continue

        raw_value = item.get(
            "allocation",
            item.get(
                "weight",
                None,
            ),
        )

        if raw_value is None:

            invalid_items += 1

            continue

        try:

            value = float(
                raw_value
            )

        except (
            TypeError,
            ValueError,
        ):

            invalid_items += 1

            continue

        if value < 0:

            negative_items += 1

        total_allocation += value

    valid = (

        invalid_items == 0

        and

        negative_items == 0

        and

        abs(
            total_allocation - 1.0
        )
        < 0.000001

    )

    return {

        "valid":
            valid,

        "total_allocation":
            total_allocation,

        "negative_items":
            negative_items,

        "count":
            len(
                normalized
            ),

    }


# ============================================================
# EXPOSURE VALIDATION
# ============================================================

def validate_exposure(
    allocation,
    exposure,
):

    normalized = _normalize_allocation(
        allocation
    )

    if normalized is None:

        return {

            "valid":
                False,

            "calculated_exposure":
                0.0,

            "reported_exposure":
                _safe_float(
                    exposure,
                    0.0,
                ),

        }

    calculated_exposure = 0.0

    for item in normalized:

        if not isinstance(
            item,
            dict,
        ):

            continue

        raw_value = item.get(
            "allocation",
            item.get(
                "weight",
                0.0,
            ),
        )

        calculated_exposure += _safe_float(
            raw_value,
            0.0,
        )

    if isinstance(
        exposure,
        dict,
    ):

        reported_exposure = _safe_float(
            exposure.get(
                "total",
                exposure.get(
                    "exposure",
                    0.0,
                ),
            ),
            0.0,
        )

    else:

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
        < 0.000001

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

    if risk is None:

        risk = {}

    if not isinstance(
        risk,
        dict,
    ):

        return {

            "valid":
                False,

            "empty":
                False,

        }

    if not risk:

        return {

            "valid":
                True,

            "empty":
                True,

        }

    risk_score = risk.get(
        "risk_score",
        risk.get(
            "score",
            None,
        ),
    )

    if risk_score is None:

        return {

            "valid":
                True,

            "empty":
                False,

        }

    try:

        risk_score = float(
            risk_score
        )

    except (
        TypeError,
        ValueError,
    ):

        return {

            "valid":
                False,

            "empty":
                False,

        }

    valid = (

        risk_score >= 0

        and

        risk_score <= 100

    )

    return {

        "valid":
            valid,

        "empty":
            False,

    }


# ============================================================
# DECISION VALIDATION
# ============================================================

def validate_decision(
    decision,
):

    if decision is None:

        decision = {}

    if not isinstance(
        decision,
        dict,
    ):

        return {

            "valid":
                False,

            "empty":
                False,

            "status":
                "",

        }

    if not decision:

        return {

            "valid":
                True,

            "empty":
                True,

            "status":
                "",

        }

    status = _safe_string(
        decision.get(
            "status",
            "",
        ),
        "",
    ).strip()

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
    portfolio_items,
    best,
):

    portfolio_items = _safe_list(
        portfolio_items
    )

    successful_names = []

    for item in portfolio_items:

        if not isinstance(
            item,
            dict,
        ):

            continue

        if _is_successful_strategy(
            item
        ):

            name = _strategy_name(
                item
            )

            if name:

                successful_names.append(
                    name
                )

    best_name = _strategy_name(
        best
    )

    if not successful_names:

        return {

            "valid":
                True,

            "has_best":
                bool(
                    best_name
                ),

        }

    if not best_name:

        return {

            "valid":
                False,

            "has_best":
                False,

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
# MAIN INSTITUTIONAL PORTFOLIO VALIDATION
# ============================================================

def validate_institutional_portfolio(
    portfolio,
):

    safe_portfolio = _safe_dict(
        portfolio
    )

    if not isinstance(
        portfolio,
        dict,
    ):

        return {

            "status":
                STATUS_INVALID,

            "valid":
                False,

            "errors": [

                "Portfolio must be a dictionary"

            ],

            "warnings": [],

            "checks": {

                "contract":
                    validate_portfolio_contract(
                        {}
                    ),

                "portfolio":
                    validate_portfolio_items(
                        []
                    ),

                "allocation":
                    validate_allocation(
                        []
                    ),

                "exposure":
                    validate_exposure(
                        [],
                        0.0,
                    ),

                "risk":
                    validate_risk(
                        {}
                    ),

                "decision":
                    validate_decision(
                        {}
                    ),

                "best":
                    validate_best_strategy(
                        [],
                        None,
                    ),

            },

            "summary": {

                "portfolio_items":
                    0,

                "successful_strategies":
                    0,

                "failed_strategies":
                    0,

                "allocation_count":
                    0,

                "allocation_total":
                    0.0,

                "exposure":
                    0.0,

            },

        }

    contract = validate_portfolio_contract(
        safe_portfolio
    )

    portfolio_items = _safe_list(
        safe_portfolio.get(
            "portfolio",
            [],
        )
    )

    allocation = safe_portfolio.get(
        "allocation",
        [],
    )

    exposure = safe_portfolio.get(
        "exposure",
        0.0,
    )

    risk = safe_portfolio.get(
        "risk",
        {},
    )

    decision = safe_portfolio.get(
        "decision",
        {},
    )

    best = safe_portfolio.get(
        "best",
        safe_portfolio.get(
            "best_strategy",
            None,
        ),
    )

    portfolio_check = validate_portfolio_items(
        portfolio_items
    )

    allocation_check = validate_allocation(
        allocation
    )

    exposure_check = validate_exposure(
        allocation,
        exposure,
    )

    risk_check = validate_risk(
        risk
    )

    decision_check = validate_decision(
        decision
    )

    best_check = validate_best_strategy(
        portfolio_items,
        best,
    )

    checks = {

        "contract":
            contract,

        "portfolio":
            portfolio_check,

        "allocation":
            allocation_check,

        "exposure":
            exposure_check,

        "risk":
            risk_check,

        "decision":
            decision_check,

        "best":
            best_check,

    }

    errors = []

    warnings = []

    if not contract.get(
        "valid",
        False,
    ):

        for key in contract.get(
            "structural_missing_keys",
            [],
        ):

            _append_unique(
                errors,
                (
                    "Missing required portfolio key: "
                    f"{key}"
                ),
            )

    for key in contract.get(
        "compatible_missing_keys",
        [],
    ):

        _append_unique(
            warnings,
            (
                "Compatible portfolio key missing: "
                f"{key}"
            ),
        )

    if not portfolio_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Portfolio contains invalid strategy items",
        )

    if not allocation_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Portfolio allocation is invalid",
        )

    if not exposure_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Portfolio exposure is inconsistent",
        )

    if not risk_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Portfolio risk is invalid",
        )

    if not decision_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Portfolio decision is invalid",
        )

    if not best_check.get(
        "valid",
        False,
    ):

        _append_unique(
            errors,
            "Best strategy is inconsistent with portfolio",
        )

    successful = portfolio_check.get(
        "successful",
        0,
    )

    failed = portfolio_check.get(
        "failed",
        0,
    )

    allocation_count = allocation_check.get(
        "count",
        0,
    )

    if (

        portfolio_check.get(
            "total",
            0,
        )
        > 0

        and

        successful == 0

        and

        failed > 0

    ):

        _append_unique(
            warnings,
            "No successful strategies in portfolio",
        )

    if (

        successful > 0

        and

        allocation_count == 0

    ):

        _append_unique(
            warnings,
            (
                "Successful strategy exists without "
                "portfolio allocation"
            ),
        )

    if errors:

        status = STATUS_INVALID

        valid = False

    elif warnings:

        status = STATUS_WARNING

        valid = True

    else:

        status = STATUS_VALID

        valid = True

    return {

        "status":
            status,

        "valid":
            valid,

        "errors":
            errors,

        "warnings":
            warnings,

        "checks":
            checks,

        "summary": {

            "portfolio_items":
                portfolio_check.get(
                    "total",
                    0,
                ),

            "successful_strategies":
                successful,

            "failed_strategies":
                failed,

            "allocation_count":
                allocation_count,

            "allocation_total":
                allocation_check.get(
                    "total_allocation",
                    0.0,
                ),

            "exposure":
                exposure_check.get(
                    "reported_exposure",
                    0.0,
                ),

        },

    }


# ============================================================
# BACKWARD FRIENDLY ALIAS
# ============================================================

def validate_portfolio(
    portfolio,
):

    return validate_institutional_portfolio(
        portfolio
    )


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [

    "STATUS_VALID",

    "STATUS_WARNING",

    "STATUS_INVALID",

    "REQUIRED_PORTFOLIO_KEYS",

    "REQUIRED_VALIDATION_KEYS",

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