"""
==========================================
SULTAN QUANT OS
WFO Advanced Report Engine
Version : 5.3.0
==========================================

Responsibilities:

- Generate detailed WFO research report
- Summarize parameter stability
- Analyze validation performance
- Distinguish successful / failed / insufficient windows
- Report WFO reliability metrics
- Preserve backward-compatible report functions

Important:

FAILED, INSUFFICIENT_DATA, and UNKNOWN WFO windows are
technical/reliability events and must not be presented as
strategy losses or performance evidence.

Only SUCCESS windows are considered usable performance
windows.

This module does NOT:

- execute WFO
- optimize parameters
- calculate indicators
- run backtests
- modify Grid engines

==========================================
"""

from collections import Counter
from datetime import datetime


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_SUCCESS = "SUCCESS"

STATUS_FAILED = "FAILED"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

STATUS_UNKNOWN = "UNKNOWN"


# ============================================================
# HEADER
# ============================================================

def _header(
    title,
):

    return (
        "\n"
        + "=" * 60
        + "\n"
        + title
        + "\n"
        + "=" * 60
        + "\n"
    )


# ============================================================
# SAFE STATUS
# ============================================================

def _normalize_status(
    value,
    default=STATUS_UNKNOWN,
):

    if value is None:

        return default

    try:

        status = str(
            value
        ).strip().upper()

    except Exception:

        return default

    if not status:

        return default

    return status


# ============================================================
# WINDOW STATUS
# ============================================================

def _get_window_status(
    item,
):

    """
    Determine WFO window status.

    Priority:

    1. item.status
    2. item.evaluation_status
    3. validation.status
    4. validation.evaluation_status
    5. validation.error
    6. legacy fallback -> SUCCESS

    Legacy WFO results without explicit status remain supported.
    """

    if not isinstance(
        item,
        dict,
    ):

        return STATUS_UNKNOWN

    # --------------------------------------------------------
    # Item-level status
    # --------------------------------------------------------

    status = item.get(
        "status"
    )

    if status:

        return _normalize_status(
            status
        )

    status = item.get(
        "evaluation_status"
    )

    if status:

        return _normalize_status(
            status
        )

    # --------------------------------------------------------
    # Validation-level status
    # --------------------------------------------------------

    validation = item.get(
        "validation",
        {},
    )

    if not isinstance(
        validation,
        dict,
    ):

        validation = {}

    status = validation.get(
        "status"
    )

    if status:

        return _normalize_status(
            status
        )

    status = validation.get(
        "evaluation_status"
    )

    if status:

        return _normalize_status(
            status
        )

    # --------------------------------------------------------
    # Validation error
    # --------------------------------------------------------

    if validation.get(
        "error"
    ):

        return STATUS_FAILED

    # --------------------------------------------------------
    # Legacy result compatibility
    # --------------------------------------------------------

    return STATUS_SUCCESS


# ============================================================
# VALID WINDOW
# ============================================================

def _is_usable_window(
    item,
):

    """
    Determine whether a WFO window is usable as performance
    evidence.

    Only explicit SUCCESS windows are considered usable.

    FAILED:
        Technical/reliability failure.

    INSUFFICIENT_DATA:
        Insufficient evidence.

    UNKNOWN:
        Uncertain status and therefore not safe to treat as
        performance evidence.

    Legacy results without explicit status remain supported
    because _get_window_status() maps them to SUCCESS.
    """

    status = _get_window_status(
        item
    )

    return status == STATUS_SUCCESS


# ============================================================
# VALID PARAMETER
# ============================================================

def _get_parameter(
    item,
):

    if not isinstance(
        item,
        dict,
    ):

        return {}

    parameter = item.get(
        "best_parameter",
        {},
    )

    if not isinstance(
        parameter,
        dict,
    ):

        return {}

    return parameter


# ============================================================
# PARAMETER STABILITY
# ============================================================

def analyze_parameter_stability(
    results: list[dict],
):

    """
    Analyze parameter stability across usable WFO windows.

    FAILED, INSUFFICIENT_DATA, and UNKNOWN windows are
    excluded because they do not provide valid performance
    evidence.

    Legacy results without status are treated as SUCCESS.
    """

    if not isinstance(
        results,
        list,
    ):

        return {}

    parameters = []

    for item in results:

        if not _is_usable_window(
            item
        ):

            continue

        parameter = _get_parameter(
            item
        )

        parameters.append(

            (

                parameter.get(
                    "RSI_OVERSOLD",
                    0,
                ),

                parameter.get(
                    "RSI_OVERBOUGHT",
                    0,
                ),

            )

        )

    if not parameters:

        return {}

    counter = Counter(
        parameters
    )

    most_common = (
        counter.most_common(
            1
        )
    )

    if not most_common:

        return {}

    return {

        "most_used":
            most_common[0][0],

        "frequency":
            most_common[0][1],

        "total":
            len(
                parameters
            ),

    }


# ============================================================
# SCORE
# ============================================================

def calculate_wfo_score(
    analysis: dict,
):

    """
    Calculate legacy WFO score.

    This function intentionally preserves the existing scoring
    contract so existing consumers and tests remain compatible.

    Score components:

    - stability contribution: maximum 50
    - PF >= 1: +25
    - PF >= 1.5: +25
    """

    if not isinstance(
        analysis,
        dict,
    ):

        return 0

    stability = analysis.get(
        "stability_score",
        0,
    )

    avg_pf = analysis.get(
        "average_profit_factor",
        0,
    )

    try:

        stability = float(
            stability
        )

    except (
        TypeError,
        ValueError,
    ):

        stability = 0

    try:

        avg_pf = float(
            avg_pf
        )

    except (
        TypeError,
        ValueError,
    ):

        avg_pf = 0

    score = 0

    score += min(
        max(
            stability,
            0,
        ),
        50,
    )

    if avg_pf >= 1:

        score += 25

    if avg_pf >= 1.5:

        score += 25

    return round(
        score,
        2,
    )


# ============================================================
# VALIDATION DATA
# ============================================================

def _get_validation(
    item,
):

    if not isinstance(
        item,
        dict,
    ):

        return {}

    validation = item.get(
        "validation",
        {},
    )

    if not isinstance(
        validation,
        dict,
    ):

        return {}

    return validation


# ============================================================
# REPORT
# ============================================================

def generate_wfo_advanced_report(
    analysis: dict,
    results: list[dict],
):

    """
    Generate the complete WFO research report.

    Backward compatibility:

    - Function name preserved.
    - Parameters preserved.
    - Existing report sections preserved.
    - Legacy WFO results without explicit status supported.

    Reliability-aware behavior:

    - SUCCESS windows are shown as performance windows.
    - FAILED windows are shown as technical failures.
    - INSUFFICIENT_DATA windows are shown separately.
    - UNKNOWN windows are not treated as performance evidence.
    """

    if not isinstance(
        analysis,
        dict,
    ):

        analysis = {}

    if not isinstance(
        results,
        list,
    ):

        results = []

    report = ""

    # ========================================================
    # HEADER
    # ========================================================

    report += _header(
        "SULTAN QUANT OS\n"
        "ADVANCED WFO REPORT"
    )

    report += (

        f"Generated : "
        f"{datetime.now():%Y-%m-%d %H:%M:%S}\n\n"

    )

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    report += (

        f"Total Window      : "
        f"{analysis.get('total_window', 0)}\n"

    )

    report += (

        f"Valid Window      : "
        f"{analysis.get('valid_window', analysis.get('total_window', 0))}\n"

    )

    report += (

        f"Failed Window     : "
        f"{analysis.get('failed_window', 0)}\n"

    )

    report += (

        f"Insufficient      : "
        f"{analysis.get('insufficient_window', 0)}\n"

    )

    report += (

        f"Usable Window     : "
        f"{analysis.get('usable_window_ratio', 0)}%\n"

    )

    report += (

        f"Average PF        : "
        f"{analysis.get('average_profit_factor', 0)}\n"

    )

    report += (

        f"Average Net       : "
        f"{analysis.get('average_net_profit', 0)}\n"

    )

    report += (

        f"Stability Score   : "
        f"{analysis.get('stability_score', 0)}%\n"

    )

    report += (

        f"Overfitting Risk  : "
        f"{analysis.get('overfitting_risk', 'UNKNOWN')}\n"

    )

    # ========================================================
    # WFO SCORE
    # ========================================================

    score = calculate_wfo_score(
        analysis
    )

    report += (

        f"WFO Score         : "
        f"{score}/100\n"

    )

    # ========================================================
    # INSTITUTIONAL ROBUSTNESS
    # ========================================================

    robustness = analysis.get(
        "wfo_robustness_score",
        0,
    )

    overfitting_score = analysis.get(
        "overfitting_score",
        100,
    )

    report += (

        f"WFO Robustness    : "
        f"{robustness}/100\n"

    )

    report += (

        f"Overfitting Score : "
        f"{overfitting_score}/100\n"

    )

    # ========================================================
    # RELIABILITY
    # ========================================================

    report += _header(
        "WFO RELIABILITY"
    )

    report += (

        f"Valid Window Ratio        : "
        f"{analysis.get('valid_window_ratio', 0)}%\n"

    )

    report += (

        f"Failed Window Ratio       : "
        f"{analysis.get('failed_window_ratio', 0)}%\n"

    )

    report += (

        f"Insufficient Window Ratio : "
        f"{analysis.get('insufficient_window_ratio', 0)}%\n"

    )

    report += (

        f"Usable Window Ratio       : "
        f"{analysis.get('usable_window_ratio', 0)}%\n"

    )

    # ========================================================
    # PERFORMANCE CONSISTENCY
    # ========================================================

    report += _header(
        "PERFORMANCE CONSISTENCY"
    )

    report += (

        f"PF >= 1 Ratio       : "
        f"{analysis.get('pf_ge_1_ratio', 0)}%\n"

    )

    report += (

        f"Median PF           : "
        f"{analysis.get('median_profit_factor', 0)}\n"

    )

    report += (

        f"Best PF             : "
        f"{analysis.get('best_profit_factor', 0)}\n"

    )

    report += (

        f"Worst PF            : "
        f"{analysis.get('worst_profit_factor', 0)}\n"

    )

    report += (

        f"PF Std Dev          : "
        f"{analysis.get('std_profit_factor', 0)}\n"

    )

    report += (

        f"Median Net Profit   : "
        f"{analysis.get('median_net_profit', 0)}\n"

    )

    report += (

        f"Best Net Profit     : "
        f"{analysis.get('best_net_profit', 0)}\n"

    )

    report += (

        f"Worst Net Profit    : "
        f"{analysis.get('worst_net_profit', 0)}\n"

    )

    report += (

        f"Net Profit Std Dev  : "
        f"{analysis.get('std_net_profit', 0)}\n"

    )

    report += (

        f"PF Consistency      : "
        f"{analysis.get('pf_consistency_score', 0)}/100\n"

    )

    report += (

        f"Return Consistency  : "
        f"{analysis.get('return_consistency_score', 0)}/100\n"

    )

    # ========================================================
    # STREAK ANALYSIS
    # ========================================================

    report += _header(
        "STREAK ANALYSIS"
    )

    report += (

        f"Max Losing Streak  : "
        f"{analysis.get('max_losing_streak', 0)}\n"

    )

    report += (

        f"Max Winning Streak : "
        f"{analysis.get('max_winning_streak', 0)}\n"

    )

    # ========================================================
    # PARAMETER STABILITY
    # ========================================================

    stability = analyze_parameter_stability(
        results
    )

    report += _header(
        "PARAMETER STABILITY"
    )

    if stability:

        report += (

            f"Most Used RSI Parameter : "
            f"{stability['most_used']}\n"

        )

        report += (

            f"Frequency              : "
            f"{stability['frequency']}/"
            f"{stability['total']}\n"

        )

    else:

        report += (
            "No usable parameter data available.\n"
        )

    # ========================================================
    # WINDOW SUMMARY
    # ========================================================

    report += _header(
        "WINDOW SUMMARY"
    )

    if not results:

        report += (
            "No WFO windows available.\n"
        )

        return report

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue

        status = _get_window_status(
            item
        )

        validation = _get_validation(
            item
        )

        report += (

            f"\nWindow "
            f"{item.get('window', '?')}\n"

        )

        report += (

            f"Status    : "
            f"{status}\n"

        )

        # ----------------------------------------------------
        # Technical failure
        # ----------------------------------------------------

        if status == STATUS_FAILED:

            reason = item.get(
                "reason",
                validation.get(
                    "error",
                    "Unknown failure",
                ),
            )

            report += (

                f"Reason    : "
                f"{reason}\n"

            )

            report += "-" * 40

            continue

        # ----------------------------------------------------
        # Insufficient data
        # ----------------------------------------------------

        if status == STATUS_INSUFFICIENT:

            reason = item.get(
                "reason",
                "Insufficient data",
            )

            report += (

                f"Reason    : "
                f"{reason}\n"

            )

            report += "-" * 40

            continue

        # ----------------------------------------------------
        # Unknown status
        # ----------------------------------------------------

        if status == STATUS_UNKNOWN:

            reason = item.get(
                "reason",
                validation.get(
                    "error",
                    "Unknown WFO status",
                ),
            )

            report += (

                f"Reason    : "
                f"{reason}\n"

            )

            report += "-" * 40

            continue

        # ----------------------------------------------------
        # Usable window
        # ----------------------------------------------------

        report += (

            f"Parameter : "
            f"{item.get('best_parameter', {})}\n"

        )

        report += (

            f"PF        : "
            f"{validation.get('profit_factor', 0)}\n"

        )

        report += (

            f"Net       : "
            f"{validation.get('net_profit', 0)}\n"

        )

        report += "-" * 40

    return report


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "STATUS_SUCCESS",

    "STATUS_FAILED",

    "STATUS_INSUFFICIENT",

    "STATUS_UNKNOWN",

    "analyze_parameter_stability",

    "calculate_wfo_score",

    "generate_wfo_advanced_report",

]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_analysis = {

        "total_window": 7,

        "valid_window": 5,

        "failed_window": 1,

        "insufficient_window": 1,

        "valid_window_ratio": 71.43,

        "failed_window_ratio": 14.29,

        "insufficient_window_ratio": 14.29,

        "usable_window_ratio": 71.43,

        "average_profit_factor": 1.16,

        "average_net_profit": 9.0,

        "stability_score": 60.0,

        "pf_ge_1_ratio": 60.0,

        "median_profit_factor": 1.20,

        "best_profit_factor": 1.50,

        "worst_profit_factor": 0.80,

        "std_profit_factor": 0.30,

        "median_net_profit": 15,

        "best_net_profit": 25,

        "worst_net_profit": -10,

        "std_net_profit": 14.2,

        "max_losing_streak": 1,

        "max_winning_streak": 2,

        "pf_consistency_score": 72.5,

        "return_consistency_score": 68.4,

        "wfo_robustness_score": 67.3,

        "overfitting_score": 20,

        "overfitting_risk": "MEDIUM",

    }

    sample_results = [

        {

            "window": 1,

            "status": "SUCCESS",

            "best_parameter": {

                "RSI_OVERSOLD": 10,

                "RSI_OVERBOUGHT": 90,

            },

            "validation": {

                "profit_factor": 1.50,

                "net_profit": 25,

            },

        },

        {

            "window": 2,

            "status": "SUCCESS",

            "best_parameter": {

                "RSI_OVERSOLD": 10,

                "RSI_OVERBOUGHT": 90,

            },

            "validation": {

                "profit_factor": 1.20,

                "net_profit": 15,

            },

        },

        {

            "window": 3,

            "status": "SUCCESS",

            "best_parameter": {

                "RSI_OVERSOLD": 15,

                "RSI_OVERBOUGHT": 85,

            },

            "validation": {

                "profit_factor": 0.80,

                "net_profit": -10,

            },

        },

        {

            "window": 4,

            "status": "SUCCESS",

            "best_parameter": {

                "RSI_OVERSOLD": 10,

                "RSI_OVERBOUGHT": 90,

            },

            "validation": {

                "profit_factor": 1.40,

                "net_profit": 20,

            },

        },

        {

            "window": 5,

            "status": "SUCCESS",

            "best_parameter": {

                "RSI_OVERSOLD": 15,

                "RSI_OVERBOUGHT": 95,

            },

            "validation": {

                "profit_factor": 0.90,

                "net_profit": -5,

            },

        },

        {

            "window": 6,

            "status": "FAILED",

            "reason": "Optimization failed",

            "validation": {},

        },

        {

            "window": 7,

            "status": "INSUFFICIENT_DATA",

            "reason": "Not enough trades",

            "validation": {},

        },

    ]

    report = generate_wfo_advanced_report(

        sample_analysis,

        sample_results,

    )

    print(report)