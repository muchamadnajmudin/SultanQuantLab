"""
==========================================
SULTAN QUANT OS
Portfolio Decision Engine
Version : 3.2.0
==========================================

Responsibilities:

- Evaluate portfolio quality
- Evaluate portfolio risk
- Select best strategy
- Evaluate WFO robustness
- Evaluate Monte Carlo robustness
- Evaluate overfitting risk
- Build institutional readiness gate
- Produce one final institutional decision
- Preserve backward compatibility

Institutional LIVE Gate:

Profit Factor      >= 2.0
Drawdown           <= 15%
WFO Stability      >= 80%
WFO Robustness     >= 90%
Monte Carlo Risk   == LOW
Monte Carlo Robust >= 90%
Portfolio Risk     must not be HIGH / CRITICAL
Qualified Strategy > 0

IMPORTANT:

The institutional gate is the SINGLE FINAL DECISION AUTHORITY.

The legacy function signature remains:

    evaluate_decision(risk, results)

Additional institutional evidence can be supplied
inside the risk/result dictionaries without breaking
existing callers.

Decision principle:

    All institutional gates must pass
    -> APPROVED
    Otherwise
    -> NEEDS OPTIMIZATION

Therefore:

    decision == "APPROVED"
        if and only if
    live_ready is True

No secondary legacy decision logic is allowed to
override the institutional gate.
"""


# ==================================================
# CONSTANTS
# ==================================================

LIVE_MIN_PROFIT_FACTOR = 2.0

LIVE_MAX_DRAWDOWN = 15.0

LIVE_MIN_WFO_STABILITY = 80.0

LIVE_MIN_WFO_ROBUSTNESS = 90.0

LIVE_MIN_MONTE_CARLO_ROBUSTNESS = 90.0

LIVE_ALLOWED_MONTE_CARLO_RISK = {
    "LOW",
}

BLOCKED_RISK_STATUSES = {
    "HIGH",
    "CRITICAL",
}


# ==================================================
# SAFE HELPERS
# ==================================================

def _safe_float(
    value,
    default=0.0,
):
    """
    Safely convert a value to float.

    Invalid values including NaN and infinity
    are converted to default.
    """

    try:

        result = float(
            value
        )

        if result != result:

            return default

        if result == float("inf"):

            return default

        if result == float("-inf"):

            return default

        return result

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_dict(
    value,
):
    """
    Return value when it is a dictionary.

    Otherwise return an empty dictionary.
    """

    if isinstance(
        value,
        dict,
    ):

        return value

    return {}


def _normalize_status(
    value,
    default="UNKNOWN",
):
    """
    Normalize status-like values.

    Example:

        " low "
        -> "LOW"
    """

    if value is None:

        return default

    try:

        return str(
            value
        ).strip().upper()

    except Exception:

        return default


def _get_nested(
    data,
    *keys,
    default=None,
):
    """
    Safely retrieve nested dictionary values.

    Example:

        _get_nested(
            data,
            "wfo",
            "stability_score",
        )
    """

    current = data

    for key in keys:

        if not isinstance(
            current,
            dict,
        ):

            return default

        current = current.get(
            key
        )

        if current is None:

            return default

    return current


# ==================================================
# STATISTICS
# ==================================================

def _get_drawdown(
    statistics,
):
    """
    Extract drawdown percentage.

    Preferred key:

        max_drawdown_percent

    Legacy fallback:

        max_drawdown
    """

    statistics = _safe_dict(
        statistics
    )

    return _safe_float(
        statistics.get(
            "max_drawdown_percent",
            statistics.get(
                "max_drawdown",
                0,
            ),
        )
    )


def _get_profit_factor(
    statistics,
):
    """
    Extract profit factor.
    """

    statistics = _safe_dict(
        statistics
    )

    return _safe_float(
        statistics.get(
            "profit_factor",
            0,
        )
    )


# ==================================================
# BEST STRATEGY
# ==================================================

def _select_best_strategy(
    results,
):
    """
    Select the strongest available strategy.

    Ranking:

        1. Strategy score
        2. Profit factor

    Existing strategy result structures are preserved.
    """

    valid_results = []

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue

        valid_results.append(
            item
        )

    if not valid_results:

        return None

    return max(
        valid_results,
        key=lambda x: (
            _safe_float(
                x.get(
                    "score",
                    0,
                )
            ),

            _get_profit_factor(
                x.get(
                    "statistics",
                    {},
                )
            ),
        ),
    )


# ==================================================
# QUALIFIED STRATEGIES
# ==================================================

def _count_qualified_strategies(
    results,
):
    """
    Count strategies that are sufficiently qualified
    for institutional evaluation.

    Current qualification:

        evaluation_status not FAILED
        evaluation_status not INSUFFICIENT_DATA
        Profit Factor > 1.0
        Score > 0
    """

    count = 0

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue

        status = _normalize_status(
            item.get(
                "evaluation_status",
                "",
            ),
            default="",
        )

        if status in {
            "FAILED",
            "INSUFFICIENT_DATA",
        }:

            continue

        statistics = _safe_dict(
            item.get(
                "statistics",
                {},
            )
        )

        pf = _get_profit_factor(
            statistics
        )

        score = _safe_float(
            item.get(
                "score",
                0,
            )
        )

        if (
            pf > 1.0
            and score > 0
        ):

            count += 1

    return count


# ==================================================
# EXTRACT WFO
# ==================================================

def _extract_wfo(
    risk,
    results,
):
    """
    Search WFO evidence in both risk and strategy
    result structures.

    Supports current and legacy naming conventions.
    """

    risk = _safe_dict(
        risk
    )

    # --------------------------------------------------
    # PRIMARY WFO SOURCE
    # --------------------------------------------------

    wfo = risk.get(
        "wfo",
        risk.get(
            "walk_forward",
            risk.get(
                "walk_forward_analysis",
                {},
            ),
        ),
    )

    if not isinstance(
        wfo,
        dict,
    ):

        wfo = {}

    # --------------------------------------------------
    # RISK SUMMARY
    # --------------------------------------------------

    summary = risk.get(
        "summary",
        {},
    )

    if not isinstance(
        summary,
        dict,
    ):

        summary = {}

    # --------------------------------------------------
    # STABILITY
    # --------------------------------------------------

    stability = wfo.get(
        "stability_score",
        summary.get(
            "wfo_stability",
            risk.get(
                "wfo_stability",
                None,
            ),
        ),
    )

    # --------------------------------------------------
    # ROBUSTNESS
    # --------------------------------------------------

    robustness = wfo.get(
        "wfo_robustness_score",
        wfo.get(
            "robustness_score",
            summary.get(
                "wfo_robustness",
                risk.get(
                    "wfo_robustness",
                    None,
                ),
            ),
        ),
    )

    # --------------------------------------------------
    # OVERFITTING
    # --------------------------------------------------

    overfitting = wfo.get(
        "overfitting_risk",
        risk.get(
            "overfitting_risk",
            "UNKNOWN",
        ),
    )

    # --------------------------------------------------
    # FALLBACK TO STRATEGY RESULTS
    # --------------------------------------------------

    if (
        stability is None
        or robustness is None
        or _normalize_status(
            overfitting,
            default="UNKNOWN",
        ) == "UNKNOWN"
    ):

        for item in results:

            if not isinstance(
                item,
                dict,
            ):

                continue

            item_wfo = item.get(
                "wfo",
                item.get(
                    "walk_forward",
                    item.get(
                        "walk_forward_analysis",
                        {},
                    ),
                ),
            )

            if not isinstance(
                item_wfo,
                dict,
            ):

                continue

            if stability is None:

                stability = item_wfo.get(
                    "stability_score"
                )

            if robustness is None:

                robustness = item_wfo.get(
                    "wfo_robustness_score",
                    item_wfo.get(
                        "robustness_score"
                    ),
                )

            if (
                _normalize_status(
                    overfitting,
                    default="UNKNOWN",
                )
                == "UNKNOWN"
            ):

                overfitting = item_wfo.get(
                    "overfitting_risk",
                    "UNKNOWN",
                )

            if (
                stability is not None
                and robustness is not None
                and _normalize_status(
                    overfitting,
                    default="UNKNOWN",
                ) != "UNKNOWN"
            ):

                break

    return {

        "stability":
            None
            if stability is None
            else _safe_float(
                stability
            ),

        "robustness":
            None
            if robustness is None
            else _safe_float(
                robustness
            ),

        "overfitting_risk":
            _normalize_status(
                overfitting,
                default="UNKNOWN",
            ),

    }


# ==================================================
# EXTRACT MONTE CARLO
# ==================================================

def _extract_monte_carlo(
    risk,
    results,
):
    """
    Search Monte Carlo evidence in current and
    legacy result structures.
    """

    risk = _safe_dict(
        risk
    )

    # --------------------------------------------------
    # RISK SUMMARY
    # --------------------------------------------------

    summary = risk.get(
        "summary",
        {},
    )

    if not isinstance(
        summary,
        dict,
    ):

        summary = {}

    # --------------------------------------------------
    # PRIMARY MONTE CARLO SOURCE
    # --------------------------------------------------

    mc = risk.get(
        "monte_carlo",
        risk.get(
            "monte_carlo_analysis",
            {},
        ),
    )

    if not isinstance(
        mc,
        dict,
    ):

        mc = {}

    # --------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------

    risk_level = mc.get(
        "risk_level",
        mc.get(
            "risk",
            summary.get(
                "monte_carlo",
                risk.get(
                    "monte_carlo_risk",
                    "UNKNOWN",
                ),
            ),
        ),
    )

    # --------------------------------------------------
    # ROBUSTNESS
    # --------------------------------------------------

    robustness = mc.get(
        "robustness_score",
        mc.get(
            "monte_carlo_robustness",
            summary.get(
                "monte_carlo_robustness",
                risk.get(
                    "monte_carlo_robustness",
                    None,
                ),
            ),
        ),
    )

    # --------------------------------------------------
    # FALLBACK TO STRATEGY RESULTS
    # --------------------------------------------------

    if (
        robustness is None
        or _normalize_status(
            risk_level,
            default="UNKNOWN",
        ) == "UNKNOWN"
    ):

        for item in results:

            if not isinstance(
                item,
                dict,
            ):

                continue

            item_mc = item.get(
                "monte_carlo",
                item.get(
                    "monte_carlo_analysis",
                    {},
                ),
            )

            if not isinstance(
                item_mc,
                dict,
            ):

                continue

            if robustness is None:

                robustness = item_mc.get(
                    "robustness_score",
                    item_mc.get(
                        "monte_carlo_robustness"
                    ),
                )

            if (
                _normalize_status(
                    risk_level,
                    default="UNKNOWN",
                )
                == "UNKNOWN"
            ):

                risk_level = item_mc.get(
                    "risk_level",
                    item_mc.get(
                        "risk",
                        "UNKNOWN",
                    ),
                )

            if (
                robustness is not None
                and _normalize_status(
                    risk_level,
                    default="UNKNOWN",
                ) != "UNKNOWN"
            ):

                break

    return {

        "risk":
            _normalize_status(
                risk_level,
                default="UNKNOWN",
            ),

        "robustness":
            None
            if robustness is None
            else _safe_float(
                robustness
            ),

    }


# ==================================================
# INSTITUTIONAL GATE
# ==================================================

def _evaluate_institutional_gate(
    pf,
    drawdown,
    risk_status,
    wfo,
    monte_carlo,
    qualified_strategies,
):
    """
    Evaluate ALL institutional gates.

    This function is the single source of truth for
    LIVE readiness.

    Every gate must pass.

    Returns:

        live_ready
        readiness
        decision
        failed_gates
        gate_results
    """

    failures = []

    # ==================================================
    # PROFIT FACTOR
    # ==================================================

    pf_pass = (
        pf >= LIVE_MIN_PROFIT_FACTOR
    )

    if not pf_pass:

        failures.append(
            "Profit Factor below 2.0"
        )

    # ==================================================
    # DRAWDOWN
    # ==================================================

    drawdown_pass = (
        drawdown <= LIVE_MAX_DRAWDOWN
    )

    if not drawdown_pass:

        failures.append(
            "Drawdown above 15%"
        )

    # ==================================================
    # WFO STABILITY
    # ==================================================

    wfo_stability = wfo.get(
        "stability"
    )

    wfo_stability_pass = (
        wfo_stability is not None
        and wfo_stability
        >= LIVE_MIN_WFO_STABILITY
    )

    if not wfo_stability_pass:

        failures.append(
            "WFO stability below 80%"
        )

    # ==================================================
    # WFO ROBUSTNESS
    # ==================================================

    wfo_robustness = wfo.get(
        "robustness"
    )

    wfo_robustness_pass = (
        wfo_robustness is not None
        and wfo_robustness
        >= LIVE_MIN_WFO_ROBUSTNESS
    )

    if not wfo_robustness_pass:

        failures.append(
            "WFO robustness below 90%"
        )

    # ==================================================
    # OVERFITTING
    # ==================================================

    overfitting_risk = _normalize_status(
        wfo.get(
            "overfitting_risk",
            "UNKNOWN",
        ),
        default="UNKNOWN",
    )

    overfitting_pass = (
        overfitting_risk
        not in {
            "HIGH",
            "CRITICAL",
            "UNKNOWN",
        }
    )

    if not overfitting_pass:

        if overfitting_risk == "UNKNOWN":

            failures.append(
                "WFO overfitting risk is unknown"
            )

        else:

            failures.append(
                "WFO overfitting risk is high"
            )

    # ==================================================
    # MONTE CARLO RISK
    # ==================================================

    mc_risk = _normalize_status(
        monte_carlo.get(
            "risk",
            "UNKNOWN",
        ),
        default="UNKNOWN",
    )

    mc_risk_pass = (
        mc_risk
        in LIVE_ALLOWED_MONTE_CARLO_RISK
    )

    if not mc_risk_pass:

        failures.append(
            "Monte Carlo risk is not LOW"
        )

    # ==================================================
    # MONTE CARLO ROBUSTNESS
    # ==================================================

    mc_robustness = monte_carlo.get(
        "robustness"
    )

    mc_robustness_pass = (
        mc_robustness is not None
        and mc_robustness
        >= LIVE_MIN_MONTE_CARLO_ROBUSTNESS
    )

    if not mc_robustness_pass:

        failures.append(
            "Monte Carlo robustness below 90%"
        )

    # ==================================================
    # PORTFOLIO RISK
    # ==================================================

    normalized_risk_status = _normalize_status(
        risk_status,
        default="UNKNOWN",
    )

    portfolio_risk_pass = (
        normalized_risk_status
        not in BLOCKED_RISK_STATUSES
        and normalized_risk_status
        != "UNKNOWN"
    )

    if not portfolio_risk_pass:

        if normalized_risk_status == "UNKNOWN":

            failures.append(
                "Portfolio risk is unknown"
            )

        else:

            failures.append(
                "Portfolio risk is HIGH or CRITICAL"
            )

    # ==================================================
    # QUALIFIED STRATEGY
    # ==================================================

    strategy_pass = (
        qualified_strategies > 0
    )

    if not strategy_pass:

        failures.append(
            "No qualified strategy available"
        )

    # ==================================================
    # FINAL GATE
    # ==================================================

    live_ready = (
        len(failures) == 0
    )

    if live_ready:

        readiness = (
            "READY FOR LIVE TRADING"
        )

        decision = (
            "APPROVED"
        )

    else:

        readiness = (
            "NOT READY FOR LIVE TRADING"
        )

        decision = (
            "NEEDS OPTIMIZATION"
        )

    return {

        "live_ready":
            live_ready,

        "readiness":
            readiness,

        "decision":
            decision,

        "failed_gates":
            failures,

        "gate_results": {

            "profit_factor":
                pf_pass,

            "drawdown":
                drawdown_pass,

            "wfo_stability":
                wfo_stability_pass,

            "wfo_robustness":
                wfo_robustness_pass,

            "overfitting":
                overfitting_pass,

            "monte_carlo_risk":
                mc_risk_pass,

            "monte_carlo_robustness":
                mc_robustness_pass,

            "portfolio_risk":
                portfolio_risk_pass,

            "qualified_strategy":
                strategy_pass,

        },

    }


# ==================================================
# NO STRATEGY RESULT
# ==================================================

def _no_strategy_result(
    reason,
    qualified_strategies=0,
):
    """
    Standardized result when no strategy is available.
    """

    return {

        "decision":
            "NO TRADE",

        "best_strategy":
            None,

        "profit_factor":
            0,

        "drawdown":
            0,

        "score":
            0,

        "risk_status":
            "UNKNOWN",

        "readiness":
            "NOT READY FOR LIVE TRADING",

        "live_ready":
            False,

        "failed_gates": [
            reason
        ],

        "gate_results": {},

        "qualified_strategies":
            qualified_strategies,

        "reason":
            reason,

        "wfo_stability":
            None,

        "wfo_robustness":
            None,

        "overfitting_risk":
            "UNKNOWN",

        "monte_carlo_risk":
            "UNKNOWN",

        "monte_carlo_robustness":
            None,

    }


# ==================================================
# MAIN DECISION
# ==================================================

def evaluate_decision(
    risk,
    results,
):
    """
    Evaluate final institutional portfolio decision.

    Backward compatible with:

        evaluate_decision(
            risk,
            results,
        )

    IMPORTANT:

    The institutional gate is now the SINGLE FINAL
    DECISION AUTHORITY.

    Therefore:

        gate passed
            -> decision = APPROVED

        gate failed
            -> decision = NEEDS OPTIMIZATION

    The only exception is absence of any usable strategy,
    which remains:

        decision = NO TRADE
    """

    # ==================================================
    # NO RESULTS
    # ==================================================

    if not results:

        return _no_strategy_result(
            "No strategy available"
        )

    # ==================================================
    # NORMALIZE RISK
    # ==================================================

    if not isinstance(
        risk,
        dict,
    ):

        risk = {}

    # ==================================================
    # SELECT BEST STRATEGY
    # ==================================================

    best = _select_best_strategy(
        results
    )

    if best is None:

        return _no_strategy_result(
            "No valid strategy available"
        )

    # ==================================================
    # BEST STRATEGY STATISTICS
    # ==================================================

    statistics = _safe_dict(
        best.get(
            "statistics",
            {},
        )
    )

    pf = _get_profit_factor(
        statistics
    )

    drawdown = _get_drawdown(
        statistics
    )

    score = _safe_float(
        best.get(
            "score",
            0,
        )
    )

    # ==================================================
    # PORTFOLIO RISK STATUS
    # ==================================================

    risk_status = _normalize_status(
        risk.get(
            "status",
            "UNKNOWN",
        ),
        default="UNKNOWN",
    )

    # ==================================================
    # EXTRACT WFO EVIDENCE
    # ==================================================

    wfo = _extract_wfo(
        risk,
        results,
    )

    # ==================================================
    # EXTRACT MONTE CARLO EVIDENCE
    # ==================================================

    monte_carlo = _extract_monte_carlo(
        risk,
        results,
    )

    # ==================================================
    # QUALIFIED STRATEGIES
    # ==================================================

    qualified_strategies = (
        _count_qualified_strategies(
            results
        )
    )

    # ==================================================
    # FINAL INSTITUTIONAL GATE
    # ==================================================

    gate = _evaluate_institutional_gate(
        pf=pf,

        drawdown=drawdown,

        risk_status=risk_status,

        wfo=wfo,

        monte_carlo=monte_carlo,

        qualified_strategies=qualified_strategies,
    )

    # ==================================================
    # SINGLE FINAL DECISION
    #
    # IMPORTANT:
    #
    # Do NOT re-evaluate PF / DD / risk here.
    #
    # The institutional gate has already evaluated
    # ALL evidence.
    # ==================================================

    decision = gate[
        "decision"
    ]

    # ==================================================
    # FINAL REASON
    # ==================================================

    if gate[
        "live_ready"
    ]:

        reason = (
            "All institutional readiness "
            "gates passed."
        )

    else:

        reason = "; ".join(
            gate[
                "failed_gates"
            ]
        )

    # ==================================================
    # FINAL RESULT
    # ==================================================

    return {

        # --------------------------------------------------
        # FINAL DECISION
        # --------------------------------------------------

        "decision":
            decision,

        # --------------------------------------------------
        # BEST STRATEGY
        # --------------------------------------------------

        "best_strategy":
            best.get(
                "name"
            ),

        # --------------------------------------------------
        # CORE METRICS
        # --------------------------------------------------

        "profit_factor":
            round(
                pf,
                2,
            ),

        "drawdown":
            round(
                drawdown,
                2,
            ),

        "score":
            round(
                score,
                2,
            ),

        # --------------------------------------------------
        # PORTFOLIO RISK
        # --------------------------------------------------

        "risk_status":
            risk_status,

        # --------------------------------------------------
        # REASON
        # --------------------------------------------------

        "reason":
            reason,

        # --------------------------------------------------
        # INSTITUTIONAL READINESS
        # --------------------------------------------------

        "readiness":
            gate[
                "readiness"
            ],

        "live_ready":
            gate[
                "live_ready"
            ],

        "failed_gates":
            gate[
                "failed_gates"
            ],

        "gate_results":
            gate[
                "gate_results"
            ],

        # --------------------------------------------------
        # STRATEGY QUALIFICATION
        # --------------------------------------------------

        "qualified_strategies":
            qualified_strategies,

        # --------------------------------------------------
        # WFO EVIDENCE
        # --------------------------------------------------

        "wfo_stability":
            wfo[
                "stability"
            ],

        "wfo_robustness":
            wfo[
                "robustness"
            ],

        "overfitting_risk":
            wfo[
                "overfitting_risk"
            ],

        # --------------------------------------------------
        # MONTE CARLO EVIDENCE
        # --------------------------------------------------

        "monte_carlo_risk":
            monte_carlo[
                "risk"
            ],

        "monte_carlo_robustness":
            monte_carlo[
                "robustness"
            ],

    }