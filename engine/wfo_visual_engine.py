"""
==========================================
SULTAN QUANT OS
WFO Visual Engine
Version : 5.3.0
==========================================

Responsibilities:

- Generate WFO equity visualization
- Generate parameter stability chart
- Create WFO research graphics
- Exclude failed / insufficient windows
- Preserve backward-compatible function names
- Preserve stable visual output filenames
- Preserve legacy WFO result compatibility

Important:

FAILED and INSUFFICIENT_DATA WFO windows are excluded from
performance visualizations.

They are technical/reliability events, not strategy losses.

Grid modules are intentionally not touched.

==========================================
"""

from pathlib import Path
from collections import Counter
import math

import matplotlib.pyplot as plt


# ============================================================
# CONFIG
# ============================================================

OUTPUT_DIR = Path(
    "reports/output"
)


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_SUCCESS = "SUCCESS"

STATUS_FAILED = "FAILED"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

STATUS_UNKNOWN = "UNKNOWN"


# ============================================================
# PREPARE OUTPUT
# ============================================================

def _prepare_output():
    """
    Create WFO output directory if necessary.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# NORMALIZE STATUS
# ============================================================

def _normalize_status(
    value,
    default=STATUS_UNKNOWN,
):
    """
    Normalize WFO status safely.
    """

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
# GET VALIDATION
# ============================================================

def _get_validation(
    item,
):
    """
    Safely retrieve validation dictionary.
    """

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
# SAFE INTEGER
# ============================================================

def _safe_integer(
    value,
):
    """
    Convert value to integer safely.

    Returns None when conversion is not possible.
    """

    if value is None:

        return None

    try:

        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return None


# ============================================================
# EXPLICIT TRADE COUNT
# ============================================================

def _get_explicit_trade_count(
    validation,
):
    """
    Retrieve explicit trade count when present.

    Supported legacy / institutional keys:

    - total_trades
    - trade_count
    - number_of_trades
    - num_trades

    Returns
    -------
    int | None

        None means that no explicit trade-count evidence
        exists.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return None

    keys = (
        "total_trades",
        "trade_count",
        "number_of_trades",
        "num_trades",
    )

    for key in keys:

        if key not in validation:

            continue

        value = _safe_integer(
            validation.get(
                key
            )
        )

        if value is not None:

            return value

    return None


# ============================================================
# GET WINDOW STATUS
# ============================================================

def _get_window_status(
    item,
    validation,
):
    """
    Determine WFO window status.

    Priority:

    1. item.status
    2. item.evaluation_status
    3. validation.status
    4. validation.evaluation_status
    5. validation.error
    6. explicit trade count
    7. explicit trades collection
    8. legacy fallback -> SUCCESS

    Older WFO result structures did not contain explicit
    status information. They remain supported.

    An explicit zero-trade result is treated as
    INSUFFICIENT_DATA rather than as a losing strategy.
    """

    # --------------------------------------------------------
    # Item-level status
    # --------------------------------------------------------

    if isinstance(
        item,
        dict,
    ):

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

    if isinstance(
        validation,
        dict,
    ):

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

        if validation.get(
            "error"
        ):

            return STATUS_FAILED

    # --------------------------------------------------------
    # Explicit trade-count evidence
    # --------------------------------------------------------

    trade_count = _get_explicit_trade_count(
        validation
    )

    if trade_count is not None:

        if trade_count <= 0:

            return STATUS_INSUFFICIENT

        return STATUS_SUCCESS

    # --------------------------------------------------------
    # Explicit trades collection
    # --------------------------------------------------------

    if isinstance(
        validation,
        dict,
    ) and "trades" in validation:

        trades = validation.get(
            "trades"
        )

        if isinstance(
            trades,
            (
                list,
                tuple,
            ),
        ):

            if len(
                trades
            ) == 0:

                return STATUS_INSUFFICIENT

            return STATUS_SUCCESS

    # --------------------------------------------------------
    # Legacy result
    # --------------------------------------------------------

    return STATUS_SUCCESS


# ============================================================
# VALID WFO RESULTS
# ============================================================

def _get_successful_results(
    results,
):
    """
    Return only usable WFO windows.

    FAILED and INSUFFICIENT_DATA windows are excluded.

    Invalid/non-dict items are ignored safely.
    """

    successful = []

    if not isinstance(
        results,
        (
            list,
            tuple,
        ),
    ):

        return successful

    for item in results:

        if not isinstance(
            item,
            dict,
        ):

            continue

        validation = _get_validation(
            item
        )

        status = _get_window_status(
            item,
            validation,
        )

        if status != STATUS_SUCCESS:

            continue

        successful.append(
            item
        )

    return successful


# ============================================================
# SAFE NET PROFIT
# ============================================================

def _get_net_profit(
    validation,
):
    """
    Safely retrieve finite numeric net profit.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return 0.0

    value = validation.get(
        "net_profit",
        0,
    )

    try:

        result = float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0

    if not math.isfinite(
        result
    ):

        return 0.0

    return result


# ============================================================
# SAFE WINDOW NUMBER
# ============================================================

def _get_window_number(
    item,
    fallback,
):
    """
    Retrieve numeric WFO window identifier safely.

    Falls back to sequential index when legacy results do not
    contain a valid window number.
    """

    if not isinstance(
        item,
        dict,
    ):

        return fallback

    value = item.get(
        "window"
    )

    number = _safe_integer(
        value
    )

    if number is None:

        return fallback

    return number


# ============================================================
# WFO EQUITY CURVE
# ============================================================

def save_wfo_equity_curve(
    results: list[dict],
):
    """
    Generate WFO cumulative validation-profit curve.

    Only SUCCESS windows are included.

    FAILED and INSUFFICIENT_DATA windows do not create
    artificial equity points.

    Original WFO window numbers are retained on the x-axis
    whenever available.
    """

    _prepare_output()

    successful_results = _get_successful_results(
        results
    )

    if not successful_results:

        return None

    equity = []

    window_numbers = []

    balance = 0.0

    for index, item in enumerate(
        successful_results,
        start=1,
    ):

        validation = _get_validation(
            item
        )

        profit = _get_net_profit(
            validation
        )

        balance += profit

        equity.append(
            balance
        )

        window_numbers.append(
            _get_window_number(
                item,
                index,
            )
        )

    if not equity:

        return None

    # ========================================================
    # PLOT
    # ========================================================

    plt.figure(
        figsize=(10, 5)
    )

    plt.plot(
        window_numbers,
        equity,
    )

    plt.title(
        "WFO Equity Curve"
    )

    plt.xlabel(
        "Validation Window"
    )

    plt.ylabel(
        "Cumulative Profit"
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    # ========================================================
    # SAVE
    # ========================================================

    file_path = (
        OUTPUT_DIR
        /
        "wfo_equity_curve.png"
    )

    plt.savefig(
        file_path,
        dpi=150,
    )

    plt.close()

    return file_path


# ============================================================
# PARAMETER KEY
# ============================================================

def _get_parameter_key(
    item,
):
    """
    Return normalized RSI parameter representation.

    Example:

        10/90
    """

    if not isinstance(
        item,
        dict,
    ):

        return None

    parameter = item.get(
        "best_parameter",
        {},
    )

    if not isinstance(
        parameter,
        dict,
    ):

        return None

    oversold = parameter.get(
        "RSI_OVERSOLD"
    )

    overbought = parameter.get(
        "RSI_OVERBOUGHT"
    )

    if oversold is None:

        return None

    if overbought is None:

        return None

    return (
        f"{oversold}"
        "/"
        f"{overbought}"
    )


# ============================================================
# PARAMETER STABILITY
# ============================================================

def save_parameter_stability_chart(
    results: list[dict],
):
    """
    Generate WFO parameter stability chart.

    Only SUCCESS windows are included.

    Invalid or missing parameter records are ignored.
    """

    _prepare_output()

    successful_results = _get_successful_results(
        results
    )

    parameters = []

    for item in successful_results:

        key = _get_parameter_key(
            item
        )

        if key is None:

            continue

        parameters.append(
            key
        )

    if not parameters:

        return None

    counter = Counter(
        parameters
    )

    labels = list(
        counter.keys()
    )

    values = list(
        counter.values()
    )

    # ========================================================
    # PLOT
    # ========================================================

    plt.figure(
        figsize=(10, 5)
    )

    plt.bar(
        labels,
        values,
    )

    plt.title(
        "WFO Parameter Stability"
    )

    plt.xlabel(
        "Parameter"
    )

    plt.ylabel(
        "Frequency"
    )

    plt.xticks(
        rotation=45
    )

    plt.grid(
        True
    )

    plt.tight_layout()

    # ========================================================
    # SAVE
    # ========================================================

    file_path = (
        OUTPUT_DIR
        /
        "wfo_parameter_stability.png"
    )

    plt.savefig(
        file_path,
        dpi=150,
    )

    plt.close()

    return file_path


# ============================================================
# MAIN
# ============================================================

def generate_wfo_visual_reports(
    results: list[dict],
):
    """
    Generate all WFO visual reports.

    Returns
    -------
    list[Path]

        Generated visual files.
    """

    files = []

    # --------------------------------------------------------
    # Equity
    # --------------------------------------------------------

    equity = save_wfo_equity_curve(
        results
    )

    if equity:

        files.append(
            equity
        )

    # --------------------------------------------------------
    # Parameter stability
    # --------------------------------------------------------

    stability = (
        save_parameter_stability_chart(
            results
        )
    )

    if stability:

        files.append(
            stability
        )

    return files


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "OUTPUT_DIR",

    "STATUS_SUCCESS",

    "STATUS_FAILED",

    "STATUS_INSUFFICIENT",

    "STATUS_UNKNOWN",

    "save_wfo_equity_curve",

    "save_parameter_stability_chart",

    "generate_wfo_visual_reports",

]


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    sample_results = [

        {
            "window": 1,

            "status": "SUCCESS",

            "best_parameter": {
                "RSI_OVERSOLD": 10,
                "RSI_OVERBOUGHT": 90,
            },

            "validation": {
                "total_trades": 10,
                "net_profit": 100,
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
                "total_trades": 8,
                "net_profit": -25,
            },
        },

        {
            "window": 3,

            "status": "SUCCESS",

            "best_parameter": {
                "RSI_OVERSOLD": 5,
                "RSI_OVERBOUGHT": 95,
            },

            "validation": {
                "total_trades": 12,
                "net_profit": 75,
            },
        },

        {
            "window": 4,

            "status": "FAILED",

            "reason":
                "Optimization failed",

            "validation": {},
        },

        {
            "window": 5,

            "status":
                "INSUFFICIENT_DATA",

            "reason":
                "Not enough trades",

            "validation": {},
        },

        {
            "window": 6,

            "best_parameter": {
                "RSI_OVERSOLD": 10,
                "RSI_OVERBOUGHT": 90,
            },

            "validation": {
                "total_trades": 0,
                "net_profit": 0,
            },
        },

    ]

    generated_files = (
        generate_wfo_visual_reports(
            sample_results
        )
    )

    print()
    print("=" * 60)
    print("SULTAN QUANT OS")
    print("WFO VISUAL ENGINE 5.3.0")
    print("=" * 60)
    print()

    if generated_files:

        print(
            "Generated Files:"
        )

        for file_path in generated_files:

            print(
                f" - {file_path}"
            )

    else:

        print(
            "No visual report generated."
        )

    print()
    print(
        "WFO VISUAL ENGINE COMPLETE"
    )