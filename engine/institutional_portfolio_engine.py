"""
==========================================
SULTAN QUANT OS
Institutional Portfolio Engine
Version : 4.5.1
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

Architecture:

Market Data
    |
    v
Portfolio Engine
    |
    v
Strategy Results
    |
    v
Institutional Portfolio Engine
    |
    +--> Result Normalization
    |
    +--> Market Regime Detection
    |
    +--> Portfolio Allocation
    |        |
    |        +--> Strategy Intelligence
    |        +--> Strategy Memory
    |        +--> Regime-Aware Allocation
    |
    +--> Portfolio Risk
    |
    +--> Portfolio Decision
    |
    v
Institutional Portfolio Result

IMPORTANT:

institutional_portfolio_engine.py is the institutional
orchestration layer.

portfolio_engine.py remains responsible for strategy
evaluation and legacy portfolio operations.

==========================================
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
    Safely convert a value to float.

    Invalid values including NaN are converted to default.
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
    Determine evaluation status for one strategy.

    Priority:

    1. Existing evaluation_status
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

    # ----------------------------------------------
    # FAILED
    # ----------------------------------------------

    if result.get(
        "error"
    ):

        return STATUS_FAILED

    # ----------------------------------------------
    # STATISTICS BASED
    # ----------------------------------------------

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

    # ----------------------------------------------
    # TRADES BASED
    # ----------------------------------------------

    trades = result.get(
        "trades",
        None,
    )

    if trades is not None:

        try:

            if len(
                trades
            ) > 0:

                return STATUS_SUCCESS

            return STATUS_INSUFFICIENT

        except TypeError:

            return STATUS_INSUFFICIENT

    return STATUS_INSUFFICIENT


# ==================================================
# NORMALIZE PORTFOLIO RESULTS
# ==================================================

def _normalize_portfolio_results(
    results,
):
    """
    Guarantee compatibility between legacy portfolio
    results and the institutional portfolio contract.

    Every valid strategy result receives:

        evaluation_status
        rank
        score
        grade
        market_regime
        weight
        router_recommended

    Existing strategy metadata is preserved.
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

        # ------------------------------------------
        # EVALUATION STATUS
        # ------------------------------------------

        result[
            "evaluation_status"
        ] = _normalize_evaluation_status(
            result
        )

        # ------------------------------------------
        # SAFE DEFAULTS
        # ------------------------------------------

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

        # ------------------------------------------
        # NORMALIZE NUMERIC FIELDS
        # ------------------------------------------

        result[
            "score"
        ] = _safe_float(
            result.get(
                "score",
                0,
            )
        )

        result[
            "weight"
        ] = _safe_float(
            result.get(
                "weight",
                0,
            )
        )

        # ------------------------------------------
        # NORMALIZE RANK
        # ------------------------------------------

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

        # ------------------------------------------
        # MARKET REGIME
        # ------------------------------------------

        if not result.get(
            "market_regime"
        ):

            result[
                "market_regime"
            ] = UNKNOWN_REGIME

        # ------------------------------------------
        # ROUTER FLAG
        # ------------------------------------------

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
# SAFE MARKET REGIME
# ==================================================

def _detect_regime(
    results,
):
    """
    Extract market regime from normalized strategy
    results.

    Priority:

    1. market_regime
    2. regime
    3. metadata.market_regime
    4. metadata.regime
    """

    if not results:

        return UNKNOWN_REGIME

    if not isinstance(
        results,
        list,
    ):

        return UNKNOWN_REGIME

    # ----------------------------------------------
    # DIRECT REGIME
    # ----------------------------------------------

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

    # ----------------------------------------------
    # NESTED METADATA
    # ----------------------------------------------

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
    """
    Safely execute the underlying portfolio engine.
    """

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
    Safely obtain best strategy.
    """

    if not results:

        return None

    try:

        best = get_best_strategy(
            results
        )

    except Exception:

        return None

    return best


# ==================================================
# NORMALIZE ALLOCATION ITEM
# ==================================================

def _normalize_allocation_item(
    item,
):
    """
    Normalize one allocation item.
    """

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
    Guarantee allocation is always returned as a list.
    """

    if allocation is None:

        return []

    # ----------------------------------------------
    # LIST
    # ----------------------------------------------

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

    # ----------------------------------------------
    # DICT
    # ----------------------------------------------

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
    Build portfolio allocation while preserving
    compatibility with current and legacy
    allocation_engine APIs.

    Supported APIs:

        build_allocation(
            results,
            max_strategies=top_n,
            regime=regime,
        )

        build_allocation(
            results,
            max_strategies=top_n,
        )

        build_allocation(
            results,
            top_n=top_n,
            regime=regime,
        )

        build_allocation(
            results,
            top_n=top_n,
        )

        build_allocation(
            results,
        )

    The regime-aware API is preferred.

    Fallbacks intentionally preserve compatibility with
    legacy allocation engines and monkeypatched tests.
    """

    if not results:

        return []

    # ----------------------------------------------
    # NORMALIZE TOP_N
    # ----------------------------------------------

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

    # ----------------------------------------------
    # NORMALIZE REGIME
    # ----------------------------------------------

    if not regime:

        regime = UNKNOWN_REGIME

    # ----------------------------------------------
    # NEW REGIME-AWARE API
    #
    # build_allocation(
    #     results,
    #     max_strategies=top_n,
    #     regime=regime,
    # )
    # ----------------------------------------------

    try:

        allocation = build_allocation(
            results,
            max_strategies=top_n,
            regime=regime,
        )

        return _normalize_allocation(
            allocation
        )

    except TypeError:

        pass

    except Exception:

        return []

    # ----------------------------------------------
    # CURRENT API WITHOUT REGIME
    #
    # build_allocation(
    #     results,
    #     max_strategies=top_n,
    # )
    # ----------------------------------------------

    try:

        allocation = build_allocation(
            results,
            max_strategies=top_n,
        )

        return _normalize_allocation(
            allocation
        )

    except TypeError:

        pass

    except Exception:

        return []

    # ----------------------------------------------
    # LEGACY REGIME-AWARE API
    #
    # build_allocation(
    #     results,
    #     top_n=top_n,
    #     regime=regime,
    # )
    # ----------------------------------------------

    try:

        allocation = build_allocation(
            results,
            top_n=top_n,
            regime=regime,
        )

        return _normalize_allocation(
            allocation
        )

    except TypeError:

        pass

    except Exception:

        return []

    # ----------------------------------------------
    # BACKWARD-COMPATIBLE API
    #
    # build_allocation(
    #     results,
    #     top_n=top_n,
    # )
    #
    # Required for legacy implementations and existing
    # monkeypatched tests.
    # ----------------------------------------------

    try:

        allocation = build_allocation(
            results,
            top_n=top_n,
        )

        return _normalize_allocation(
            allocation
        )

    except TypeError:

        pass

    except Exception:

        return []

    # ----------------------------------------------
    # FINAL LEGACY API
    #
    # build_allocation(
    #     results
    # )
    # ----------------------------------------------

    try:

        allocation = build_allocation(
            results
        )

    except Exception:

        return []

    return _normalize_allocation(
        allocation
    )


# ==================================================
# PORTFOLIO EXPOSURE
# ==================================================

def _calculate_exposure(
    allocation,
):
    """
    Calculate total portfolio exposure.
    """

    if not allocation:

        return 0.0

    # ----------------------------------------------
    # DICT
    # ----------------------------------------------

    if isinstance(
        allocation,
        dict,
    ):

        exposure = 0.0

        for value in allocation.values():

            exposure += _safe_float(
                value
            )

        return round(
            exposure,
            4,
        )

    # ----------------------------------------------
    # LIST
    # ----------------------------------------------

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

            if "allocation" in item:

                value = item.get(
                    "allocation"
                )

            elif "weight" in item:

                value = item.get(
                    "weight"
                )

            elif "weight_pct" in item:

                value = item.get(
                    "weight_pct"
                )

            else:

                value = 0.0

            exposure += _safe_float(
                value
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
    """
    Safely calculate portfolio risk.
    """

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
# SAFE PORTFOLIO DECISION
# ==================================================

def _safe_evaluate_decision(
    risk,
    results,
):
    """
    Safely evaluate institutional portfolio decision.

    Decision Engine remains the owner of the actual
    decision logic.
    """

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
# SAFE PORTFOLIO SUMMARY
# ==================================================

def _safe_portfolio_summary(
    results,
):
    """
    Safely generate portfolio summary.
    """

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
# EMPTY INSTITUTIONAL PORTFOLIO
# ==================================================

def _empty_institutional_portfolio():
    """
    Return the stable empty institutional portfolio
    contract.
    """

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

    Parameters
    ----------
    df : pandas.DataFrame
        Market OHLCV data.

    top_n : int
        Maximum number of strategies considered by
        allocation engine.

    Returns
    -------
    dict

        {
            "regime": str,
            "portfolio": list,
            "best": dict | None,
            "allocation": list,
            "risk": dict,
            "decision": dict,
            "exposure": float,
            "summary": dict,
        }
    """

    # ==================================================
    # SAFE EMPTY RESULT
    # ==================================================

    if df is None:

        return _empty_institutional_portfolio()

    # ==================================================
    # NORMALIZE TOP_N
    # ==================================================

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
    # RUN STRATEGY PORTFOLIO
    # ==================================================

    results = _safe_run_portfolio(
        df
    )

    # ==================================================
    # NORMALIZE PORTFOLIO RESULTS
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
    # ==================================================

    best = _safe_get_best_strategy(
        results
    )

    # ==================================================
    # PORTFOLIO ALLOCATION
    # ==================================================

    allocation = _safe_build_allocation(
        results,
        top_n=top_n,
        regime=regime,
    )

    # ==================================================
    # PORTFOLIO RISK
    # ==================================================

    risk = _safe_calculate_portfolio_risk(
        allocation
    )

    # ==================================================
    # PORTFOLIO DECISION
    # ==================================================

    decision = _safe_evaluate_decision(
        risk,
        results,
    )

    # ==================================================
    # PORTFOLIO EXPOSURE
    # ==================================================

    exposure = _calculate_exposure(
        allocation
    )

    # ==================================================
    # PORTFOLIO SUMMARY
    # ==================================================

    summary = _safe_portfolio_summary(
        results
    )

    # ==================================================
    # RETURN
    # ==================================================

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
    """
    Backward-compatible alias for
    build_institutional_portfolio().
    """

    return build_institutional_portfolio(
        df,
        top_n=top_n,
    )


# ==================================================
# BUILD PORTFOLIO WRAPPER
# ==================================================

def build_portfolio_from_data(
    df,
    top_n=3,
):
    """
    Execute institutional portfolio construction
    directly from market data.
    """

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