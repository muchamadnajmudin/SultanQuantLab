"""
==========================================
SULTAN QUANT OS
Institutional Portfolio Engine
Version : 4.5.2
==========================================

Responsibilities:

- Execute institutional strategy evaluation
- Normalize portfolio strategy results
- Detect market regime
- Build portfolio candidates
- Build dynamic allocation
- Calculate portfolio risk
- Calculate portfolio exposure
- Evaluate institutional portfolio decision
- Preserve backward compatibility

IMPORTANT:

This module is the single source of truth for
institutional portfolio orchestration.

portfolio_engine.py remains responsible for:

    - Strategy evaluation
    - Strategy ranking
    - Strategy memory
    - Legacy portfolio operations
"""

from engine.portfolio_engine import (
    run_portfolio,
    get_best_strategy,
    portfolio_summary,
)

from engine.allocation_engine import (
    build_allocation,
)

from risk.portfolio_risk import (
    calculate_portfolio_risk,
)

from engine.decision_engine import (
    evaluate_decision,
)


# ==================================================
# CONSTANTS
# ==================================================

UNKNOWN_REGIME = "UNKNOWN"

STATUS_SUCCESS = "SUCCESS"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

STATUS_FAILED = "FAILED"


# ==================================================
# SAFE FLOAT
# ==================================================

def _safe_float(
    value,
    default=0.0,
):

    """
    Safely convert value to float.

    Invalid values and NaN return default.
    """

    try:

        result = float(
            value
        )

        if result != result:

            return default

        return result

    except (
        TypeError,
        ValueError,
    ):

        return default


# ==================================================
# NORMALIZE EVALUATION STATUS
# ==================================================

def _normalize_evaluation_status(
    result,
):

    """
    Determine evaluation status.

    Priority:

        1. Explicit existing status
        2. Explicit error
        3. Statistics trade count
        4. Trades collection
        5. INSUFFICIENT_DATA
    """

    existing_status = result.get(
        "evaluation_status"
    )

    if existing_status:

        return str(
            existing_status
        )


    if result.get(
        "error"
    ):

        return STATUS_FAILED


    statistics = result.get(
        "statistics",
        {},
    )


    if isinstance(
        statistics,
        dict,
    ):

        total_trade = statistics.get(
            "total_trade",
            statistics.get(
                "total_trades",
                None,
            ),
        )


        if total_trade is not None:

            try:

                total_trade = int(
                    float(
                        total_trade
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                total_trade = 0


            if total_trade > 0:

                return STATUS_SUCCESS


            return STATUS_INSUFFICIENT


    trades = result.get(
        "trades"
    )


    if trades is not None:

        try:

            if len(
                trades
            ) > 0:

                return STATUS_SUCCESS


        except TypeError:

            pass


    return STATUS_INSUFFICIENT


# ==================================================
# NORMALIZE PORTFOLIO RESULTS
# ==================================================

def _normalize_portfolio_results(
    results,
):

    """
    Normalize all strategy results to the stable
    institutional contract.
    """

    normalized_results = []


    if not isinstance(
        results,
        list,
    ):

        return normalized_results


    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue


        result = item.copy()


        # ==============================================
        # STATUS
        # ==============================================

        result[
            "evaluation_status"
        ] = _normalize_evaluation_status(
            result
        )


        # ==============================================
        # DEFAULTS
        # ==============================================

        result.setdefault(
            "rank",
            0,
        )

        result.setdefault(
            "score",
            0,
        )

        result.setdefault(
            "grade",
            "N/A",
        )

        result.setdefault(
            "market_regime",
            UNKNOWN_REGIME,
        )

        result.setdefault(
            "weight",
            0,
        )

        result.setdefault(
            "router_recommended",
            False,
        )


        # ==============================================
        # NUMERIC NORMALIZATION
        # ==============================================

        result[
            "score"
        ] = _safe_float(
            result.get(
                "score"
            )
        )


        result[
            "weight"
        ] = _safe_float(
            result.get(
                "weight"
            )
        )


        try:

            result[
                "rank"
            ] = int(
                float(
                    result.get(
                        "rank",
                        0,
                    )
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            result[
                "rank"
            ] = 0


        # ==============================================
        # REGIME
        # ==============================================

        if not result.get(
            "market_regime"
        ):

            result[
                "market_regime"
            ] = UNKNOWN_REGIME


        # ==============================================
        # ROUTER FLAG
        # ==============================================

        result[
            "router_recommended"
        ] = bool(
            result.get(
                "router_recommended",
                False,
            )
        )


        normalized_results.append(
            result
        )


    return normalized_results


# ==================================================
# DETECT REGIME
# ==================================================

def _detect_regime(
    results,
):

    """
    Extract market regime from normalized results.
    """

    if not isinstance(
        results,
        list,
    ):

        return UNKNOWN_REGIME


    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue


        regime = item.get(
            "market_regime"
        )


        if (
            regime
            and regime != UNKNOWN_REGIME
        ):

            return str(
                regime
            )


        regime = item.get(
            "regime"
        )


        if regime:

            return str(
                regime
            )


    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue


        metadata = item.get(
            "metadata"
        )


        if not isinstance(
            metadata,
            dict,
        ):

            continue


        regime = metadata.get(
            "market_regime"
        )


        if regime:

            return str(
                regime
            )


        regime = metadata.get(
            "regime"
        )


        if regime:

            return str(
                regime
            )


    return UNKNOWN_REGIME


# ==================================================
# SAFE RUN PORTFOLIO
# ==================================================

def _safe_run_portfolio(
    df,
):

    try:

        results = run_portfolio(
            df
        )

    except Exception:

        return []


    if not isinstance(
        results,
        list,
    ):

        return []


    return results


# ==================================================
# SAFE BEST STRATEGY
# ==================================================

def _safe_get_best_strategy(
    results,
):

    """
    Obtain best strategy from normalized results.
    """

    if not results:

        return None


    try:

        best = get_best_strategy(
            results
        )

    except Exception:

        return None


    if not isinstance(
        best,
        dict,
    ):

        return None


    return best


# ==================================================
# NORMALIZE ALLOCATION ITEM
# ==================================================

def _normalize_allocation_item(
    item,
):

    if not isinstance(
        item,
        dict,
    ):

        return None


    normalized = dict(
        item
    )


    if "allocation" in normalized:

        normalized[
            "allocation"
        ] = _safe_float(
            normalized.get(
                "allocation"
            )
        )


    elif "weight" in normalized:

        normalized[
            "allocation"
        ] = _safe_float(
            normalized.get(
                "weight"
            )
        )


    elif "weight_pct" in normalized:

        normalized[
            "allocation"
        ] = _safe_float(
            normalized.get(
                "weight_pct"
            )
        )


    else:

        normalized[
            "allocation"
        ] = 0.0


    return normalized


# ==================================================
# NORMALIZE ALLOCATION
# ==================================================

def _normalize_allocation(
    allocation,
):

    """
    Normalize allocation to a stable list contract.
    """

    if allocation is None:

        return []


    if isinstance(
        allocation,
        list,
    ):

        normalized = []


        for item in allocation:

            normalized_item = (
                _normalize_allocation_item(
                    item
                )
            )


            if normalized_item is not None:

                normalized.append(
                    normalized_item
                )


        return normalized


    if isinstance(
        allocation,
        dict,
    ):

        normalized = []


        for name, weight in allocation.items():

            normalized.append(
                {

                    "name":
                        name,

                    "allocation":
                        _safe_float(
                            weight
                        ),

                }
            )


        return normalized


    return []


# ==================================================
# SAFE BUILD ALLOCATION
# ==================================================

def _safe_build_allocation(
    results,
    top_n=3,
    regime=None,
):

    """
    Build allocation while preserving compatibility with:

        Current regime-aware API
        Current API
        Legacy API
        Monkeypatched tests
    """

    if not results:

        return []


    try:

        top_n = int(
            top_n
        )

    except (
        TypeError,
        ValueError,
    ):

        top_n = 3


    if top_n < 1:

        top_n = 1


    if not regime:

        regime = UNKNOWN_REGIME


    attempts = [

        lambda: build_allocation(
            results,
            max_strategies=top_n,
            regime=regime,
        ),

        lambda: build_allocation(
            results,
            max_strategies=top_n,
        ),

        lambda: build_allocation(
            results,
            top_n=top_n,
            regime=regime,
        ),

        lambda: build_allocation(
            results,
            top_n=top_n,
        ),

        lambda: build_allocation(
            results
        ),

    ]


    for attempt in attempts:

        try:

            allocation = attempt()

            return _normalize_allocation(
                allocation
            )

        except TypeError:

            continue

        except Exception:

            return []


    return []


# ==================================================
# PORTFOLIO EXPOSURE
# ==================================================

def _calculate_exposure(
    allocation,
):

    """
    Calculate total normalized portfolio exposure.
    """

    if not allocation:

        return 0.0


    if isinstance(
        allocation,
        dict,
    ):

        return round(

            sum(
                _safe_float(
                    value
                )

                for value

                in allocation.values()
            ),

            4,
        )


    if isinstance(
        allocation,
        list,
    ):

        exposure = 0.0


        for item in allocation:

            if not isinstance(
                item,
                dict,
            ):

                continue


            exposure += _safe_float(
                item.get(
                    "allocation",
                    item.get(
                        "weight",
                        item.get(
                            "weight_pct",
                            0,
                        ),
                    ),
                )
            )


        return round(
            exposure,
            4,
        )


    return 0.0


# ==================================================
# SAFE PORTFOLIO RISK
# ==================================================

def _safe_calculate_portfolio_risk(
    allocation,
):

    if not allocation:

        return {}


    try:

        risk = calculate_portfolio_risk(
            allocation
        )

    except Exception:

        return {}


    if isinstance(
        risk,
        dict,
    ):

        return risk


    return {}


# ==================================================
# SAFE DECISION
# ==================================================

def _safe_evaluate_decision(
    risk,
    results,
):

    try:

        decision = evaluate_decision(
            risk,
            results,
        )

    except Exception:

        return {}


    if isinstance(
        decision,
        dict,
    ):

        return decision


    return {}


# ==================================================
# SAFE SUMMARY
# ==================================================

def _safe_portfolio_summary(
    results,
):

    if not results:

        return {}


    try:

        summary = portfolio_summary(
            results
        )

    except Exception:

        return {}


    if isinstance(
        summary,
        dict,
    ):

        return summary


    return {}


# ==================================================
# EMPTY CONTRACT
# ==================================================

def _empty_institutional_portfolio():

    return {

        "regime":
            UNKNOWN_REGIME,

        "portfolio":
            [],

        "best":
            None,

        "allocation":
            [],

        "risk":
            {},

        "decision":
            {},

        "exposure":
            0.0,

        "summary":
            {},

    }


# ==================================================
# BUILD INSTITUTIONAL PORTFOLIO
# ==================================================

def build_institutional_portfolio(
    df,
    top_n=3,
):

    """
    Build complete institutional portfolio.

    This is the canonical institutional portfolio
    orchestration entry point.
    """

    if df is None:

        return _empty_institutional_portfolio()


    try:

        top_n = int(
            top_n
        )

    except (
        TypeError,
        ValueError,
    ):

        top_n = 3


    if top_n < 1:

        top_n = 1


    # ==================================================
    # STRATEGY EVALUATION
    # ==================================================

    results = _safe_run_portfolio(
        df
    )


    # ==================================================
    # NORMALIZATION
    # ==================================================

    results = _normalize_portfolio_results(
        results
    )


    # ==================================================
    # MARKET REGIME
    # ==================================================

    regime = _detect_regime(
        results
    )


    # ==================================================
    # BEST STRATEGY
    #
    # Uses normalized results.
    # ==================================================

    best = _safe_get_best_strategy(
        results
    )


    # ==================================================
    # ALLOCATION
    # ==================================================

    allocation = _safe_build_allocation(
        results,
        top_n=top_n,
        regime=regime,
    )


    # ==================================================
    # RISK
    # ==================================================

    risk = _safe_calculate_portfolio_risk(
        allocation
    )


    # ==================================================
    # DECISION
    # ==================================================

    decision = _safe_evaluate_decision(
        risk,
        results,
    )


    # ==================================================
    # EXPOSURE
    # ==================================================

    exposure = _calculate_exposure(
        allocation
    )


    # ==================================================
    # SUMMARY
    # ==================================================

    summary = _safe_portfolio_summary(
        results
    )


    return {

        "regime":
            regime,

        "portfolio":
            results,

        "best":
            best,

        "allocation":
            allocation,

        "risk":
            risk,

        "decision":
            decision,

        "exposure":
            exposure,

        "summary":
            summary,

    }


# ==================================================
# BACKWARD-COMPATIBLE ALIAS
# ==================================================

def run_institutional_portfolio(
    df,
    top_n=3,
):

    return build_institutional_portfolio(
        df,
        top_n=top_n,
    )


# ==================================================
# BUILD PORTFOLIO FROM DATA
# ==================================================

def build_portfolio_from_data(
    df,
    top_n=3,
):

    return build_institutional_portfolio(
        df,
        top_n=top_n,
    )


# ==================================================
# PUBLIC API
# ==================================================

__all__ = [

    "build_institutional_portfolio",

    "run_institutional_portfolio",

    "build_portfolio_from_data",

]