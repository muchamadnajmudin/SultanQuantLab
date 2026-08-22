"""
==========================================
SULTAN QUANT OS
Portfolio Decision Engine
Version : 3.0.0
==========================================

Responsibilities:

- Evaluate portfolio quality
- Evaluate portfolio risk
- Select best strategy
- Evaluate WFO robustness
- Evaluate Monte Carlo robustness
- Evaluate overfitting risk
- Build institutional readiness gate
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

Important:

The legacy function signature remains:

    evaluate_decision(risk, results)

Additional institutional evidence can be supplied
inside the risk/result dictionaries without breaking
existing callers.
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

    try:

        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return default


def _safe_dict(
    value,
):

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

        if pf > 1.0 and score > 0:

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

    # ----------------------------------------------
    # RISK -> WFO
    # ----------------------------------------------

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

    # ----------------------------------------------
    # RISK SUMMARY
    # ----------------------------------------------

    summary = risk.get(
        "summary",
        {},
    )

    if not isinstance(
        summary,
        dict,
    ):

        summary = {}

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

    overfitting = wfo.get(
        "overfitting_risk",
        risk.get(
            "overfitting_risk",
            "UNKNOWN",
        ),
    )

    # ----------------------------------------------
    # STRATEGY FALLBACK
    # ----------------------------------------------

    if (
        stability is None
        or robustness is None
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
                    {},
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

            if overfitting == "UNKNOWN":

                overfitting = item_wfo.get(
                    "overfitting_risk",
                    "UNKNOWN",
                )

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

    summary = risk.get(
        "summary",
        {},
    )

    if not isinstance(
        summary,
        dict,
    ):

        summary = {}

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

    # ----------------------------------------------
    # STRATEGY FALLBACK
    # ----------------------------------------------

    if (
        robustness is None
        or _normalize_status(
            risk_level
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

            if _normalize_status(
                risk_level
            ) == "UNKNOWN":

                risk_level = item_mc.get(
                    "risk_level",
                    item_mc.get(
                        "risk",
                        "UNKNOWN",
                    ),
                )

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

    failures = []

    # ----------------------------------------------
    # PROFIT FACTOR
    # ----------------------------------------------

    pf_pass = (
        pf >= LIVE_MIN_PROFIT_FACTOR
    )

    if not pf_pass:

        failures.append(
            "Profit Factor below 2.0"
        )

    # ----------------------------------------------
    # DRAWDOWN
    # ----------------------------------------------

    drawdown_pass = (
        drawdown <= LIVE_MAX_DRAWDOWN
    )

    if not drawdown_pass:

        failures.append(
            "Drawdown above 15%"
        )

    # ----------------------------------------------
    # WFO STABILITY
    # ----------------------------------------------

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

    # ----------------------------------------------
    # WFO ROBUSTNESS
    # ----------------------------------------------

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

    # ----------------------------------------------
    # OVERFITTING
    # ----------------------------------------------

    overfitting_risk = _normalize_status(
        wfo.get(
            "overfitting_risk",
            "UNKNOWN",
        )
    )

    overfitting_pass = (
        overfitting_risk
        not in {
            "HIGH",
            "CRITICAL",
        }
    )

    if not overfitting_pass:

        failures.append(
            "WFO overfitting risk is high"
        )

    # ----------------------------------------------
    # MONTE CARLO RISK
    # ----------------------------------------------

    mc_risk = _normalize_status(
        monte_carlo.get(
            "risk",
            "UNKNOWN",
        )
    )

    mc_risk_pass = (
        mc_risk
        in LIVE_ALLOWED_MONTE_CARLO_RISK
    )

    if not mc_risk_pass:

        failures.append(
            "Monte Carlo risk is not LOW"
        )

    # ----------------------------------------------
    # MONTE CARLO ROBUSTNESS
    # ----------------------------------------------

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

    # ----------------------------------------------
    # PORTFOLIO RISK
    # ----------------------------------------------

    normalized_risk_status = _normalize_status(
        risk_status,
        default="UNKNOWN",
    )

    portfolio_risk_pass = (
        normalized_risk_status
        not in BLOCKED_RISK_STATUSES
    )

    if not portfolio_risk_pass:

        failures.append(
            "Portfolio risk is HIGH or CRITICAL"
        )

    # ----------------------------------------------
    # QUALIFIED STRATEGIES
    # ----------------------------------------------

    strategy_pass = (
        qualified_strategies > 0
    )

    if not strategy_pass:

        failures.append(
            "No qualified strategy available"
        )

    # ----------------------------------------------
    # FINAL
    # ----------------------------------------------

    live_ready = not failures

    if live_ready:

        readiness = (
            "READY FOR LIVE TRADING"
        )

        decision = "APPROVED"

    else:

        readiness = (
            "NOT READY FOR LIVE TRADING"
        )

        decision = "NEEDS OPTIMIZATION"

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
# MAIN DECISION
# ==================================================

def evaluate_decision(
    risk,
    results,
):
    """
    Institutional portfolio decision.

    Backward compatible with:

        evaluate_decision(
            risk,
            results,
        )

    Returns both the legacy decision and the new
    institutional readiness gate.
    """

    if not results:

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
                "No strategy available"
            ],

            "gate_results": {},

            "qualified_strategies":
                0,

            "reason":
                "No strategy available",

        }

    if not isinstance(
        risk,
        dict,
    ):

        risk = {}

    # ==================================================
    # BEST STRATEGY
    # ==================================================

    best = _select_best_strategy(
        results
    )

    if best is None:

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
                "No valid strategy available"
            ],

            "gate_results": {},

            "qualified_strategies":
                0,

            "reason":
                "No valid strategy available",

        }

    # ==================================================
    # CORE METRICS
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

    risk_status = _normalize_status(
        risk.get(
            "status",
            "HIGH",
        ),
        default="HIGH",
    )

    # ==================================================
    # INSTITUTIONAL EVIDENCE
    # ==================================================

    wfo = _extract_wfo(
        risk,
        results,
    )

    monte_carlo = _extract_monte_carlo(
        risk,
        results,
    )

    qualified_strategies = (
        _count_qualified_strategies(
            results
        )
    )

    # ==================================================
    # INSTITUTIONAL GATE
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
    # LEGACY DECISION COMPATIBILITY
    # ==================================================

    if risk_status in BLOCKED_RISK_STATUSES:

        legacy_decision = "BLOCKED"

        legacy_reason = (
            "Portfolio risk is too high."
        )

    elif pf < 1.0:

        legacy_decision = "NOT RECOMMENDED"

        legacy_reason = (
            "Best strategy has negative "
            "trading expectancy."
        )

    elif pf < 1.2:

        legacy_decision = "NEEDS OPTIMIZATION"

        legacy_reason = (
            "Profit factor is below "
            "institutional minimum."
        )

    elif drawdown > 30:

        legacy_decision = "NEEDS OPTIMIZATION"

        legacy_reason = (
            "Portfolio drawdown is excessive."
        )

    elif drawdown > 20:

        legacy_decision = "CAUTIOUS"

        legacy_reason = (
            "Drawdown is elevated."
        )

    elif pf >= 2.0:

        legacy_decision = "APPROVED"

        legacy_reason = (
            "Strategy meets strong "
            "profitability threshold."
        )

    else:

        legacy_decision = "NEEDS OPTIMIZATION"

        legacy_reason = (
            "Strategy is profitable but "
            "does not yet meet institutional "
            "quality threshold."
        )

    # ==================================================
    # INSTITUTIONAL REASON
    # ==================================================

    if gate["live_ready"]:

        reason = (
            "All institutional readiness "
            "gates passed."
        )

    else:

        reason = "; ".join(
            gate["failed_gates"]
        )

    # ==================================================
    # RETURN
    # ==================================================

    return {

        # ----------------------------------------------
        # LEGACY
        # ----------------------------------------------

        "decision":
            legacy_decision,

        "best_strategy":
            best.get(
                "name"
            ),

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

        "risk_status":
            risk_status,

        "reason":
            reason,

        # ----------------------------------------------
        # INSTITUTIONAL
        # ----------------------------------------------

        "readiness":
            gate["readiness"],

        "live_ready":
            gate["live_ready"],

        "failed_gates":
            gate["failed_gates"],

        "gate_results":
            gate["gate_results"],

        "qualified_strategies":
            qualified_strategies,

        # ----------------------------------------------
        # WFO
        # ----------------------------------------------

        "wfo_stability":
            wfo["stability"],

        "wfo_robustness":
            wfo["robustness"],

        "overfitting_risk":
            wfo["overfitting_risk"],

        # ----------------------------------------------
        # MONTE CARLO
        # ----------------------------------------------

        "monte_carlo_risk":
            monte_carlo["risk"],

        "monte_carlo_robustness":
            monte_carlo["robustness"],

    }