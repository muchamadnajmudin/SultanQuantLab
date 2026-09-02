"""
==========================================
SULTAN QUANT OS
WFO CSV Exporter
Version : 5.3.0
==========================================

Responsibilities:

- Export WFO window results
- Save optimization history
- Create research dataset
- Preserve backward-compatible CSV columns
- Export WFO execution status
- Distinguish failed / insufficient windows
- Preserve usable validation metrics
- Support legacy WFO result structures
- Keep reliability information explicit

Compatibility:

Existing function contract is preserved:

    export_wfo_csv(
        results,
        filename=None,
    )

Existing CSV columns are preserved.

Additional columns:

- Status
- Reason
- Valid Window

Important:

FAILED, INSUFFICIENT_DATA, and UNKNOWN windows are NOT
converted into artificial trading losses.

Their unavailable performance metrics are exported as
empty CSV fields instead of zero.

Only SUCCESS windows are considered valid performance
evidence.

Grid modules are intentionally not touched.

==========================================
"""


from pathlib import Path
import csv


# ============================================================
# OUTPUT
# ============================================================

OUTPUT_FILE = Path(
    "reports/output/wfo_results.csv"
)


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_SUCCESS = "SUCCESS"

STATUS_FAILED = "FAILED"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"

STATUS_UNKNOWN = "UNKNOWN"


# ============================================================
# NORMALIZE STATUS
# ============================================================

def _normalize_status(
    value,
    default=STATUS_UNKNOWN,
):
    """
    Normalize WFO status.

    Supported statuses:

    SUCCESS
    FAILED
    INSUFFICIENT_DATA
    UNKNOWN
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
# GET EXPLICIT TRADE COUNT
# ============================================================

def _get_explicit_trade_count(
    validation,
):
    """
    Retrieve explicit trade count when available.

    Supported keys:

    - total_trades
    - trade_count
    - number_of_trades
    - num_trades

    Returns
    -------
    int | None

        None means no explicit trade-count information
        is available.
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
    8. legacy result fallback -> SUCCESS

    Legacy WFO results without explicit status remain
    supported.

    Important:

    An explicit zero-trade result is classified as
    INSUFFICIENT_DATA rather than as a strategy loss.
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

        # ----------------------------------------------------
        # Explicit validation error
        # ----------------------------------------------------

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
    # Legacy WFO result
    #
    # Older results did not have status information.
    # Preserve compatibility.
    # --------------------------------------------------------

    return STATUS_SUCCESS


# ============================================================
# GET REASON
# ============================================================

def _get_reason(
    item,
    validation,
):
    """
    Retrieve the most useful reason/error message.
    """

    if isinstance(
        item,
        dict,
    ):

        reason = item.get(
            "reason"
        )

        if reason:

            return str(
                reason
            )

        error = item.get(
            "error"
        )

        if error:

            return str(
                error
            )

    if isinstance(
        validation,
        dict,
    ):

        reason = validation.get(
            "reason"
        )

        if reason:

            return str(
                reason
            )

        error = validation.get(
            "error"
        )

        if error:

            return str(
                error
            )

    # --------------------------------------------------------
    # Automatic reason for explicit zero-trade result
    # --------------------------------------------------------

    trade_count = _get_explicit_trade_count(
        validation
    )

    if trade_count is not None:

        if trade_count <= 0:

            return "Not enough trades"

    # --------------------------------------------------------
    # Automatic reason for empty trades collection
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

                return "Not enough trades"

    return ""


# ============================================================
# VALIDATION VALUE
# ============================================================

def _validation_value(
    validation,
    key,
    status,
):
    """
    Return a validation metric only when the window is usable.

    FAILED, INSUFFICIENT_DATA, and UNKNOWN windows return an
    empty CSV field rather than a misleading zero.

    Only SUCCESS windows are treated as performance evidence.
    """

    if status != STATUS_SUCCESS:

        return ""

    if not isinstance(
        validation,
        dict,
    ):

        return ""

    return validation.get(
        key,
        "",
    )


# ============================================================
# RESULTS NORMALIZATION
# ============================================================

def _normalize_results(
    results,
):
    """
    Safely normalize WFO results to a list.

    Invalid top-level input returns an empty list.
    Invalid individual items are handled during export.
    """

    if not isinstance(
        results,
        (
            list,
            tuple,
        ),
    ):

        return []

    return list(
        results
    )


# ============================================================
# EXPORT
# ============================================================

def export_wfo_csv(
    results: list[dict],
    filename=None,
):
    """
    Export WFO results to CSV.

    Parameters
    ----------
    results : list[dict]

        WFO execution results.

    filename : str | Path | None

        Optional custom output path.

    Returns
    -------
    pathlib.Path

        Generated CSV path.

    Backward compatibility
    ----------------------

    Function signature remains:

        export_wfo_csv(results, filename=None)

    Existing columns remain available.

    Reliability behavior
    --------------------

    SUCCESS:

        Performance metrics are exported.

    FAILED:

        Performance metrics are blank.

    INSUFFICIENT_DATA:

        Performance metrics are blank.

    UNKNOWN:

        Performance metrics are blank.

    Legacy result without explicit status:

        Treated as SUCCESS unless explicit validation
        evidence identifies insufficient data or failure.
    """

    # ========================================================
    # NORMALIZE RESULTS
    # ========================================================

    results = _normalize_results(
        results
    )

    # ========================================================
    # OUTPUT PATH
    # ========================================================

    if filename:

        output = Path(
            filename
        )

    else:

        output = OUTPUT_FILE

    # ========================================================
    # PREPARE DIRECTORY
    # ========================================================

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # WRITE CSV
    # ========================================================

    with open(
        output,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(
            file
        )

        # ====================================================
        # HEADER
        #
        # Existing columns are preserved.
        #
        # New reliability columns are appended.
        # ====================================================

        writer.writerow([

            # ------------------------------------------------
            # Existing columns
            # ------------------------------------------------

            "Window",

            "Train Start",
            "Train End",

            "Test Start",
            "Test End",

            "RSI Oversold",
            "RSI Overbought",

            "Profit Factor",

            "Net Profit",

            "Win Rate",

            "Drawdown",

            # ------------------------------------------------
            # Reliability columns
            # ------------------------------------------------

            "Status",

            "Reason",

            "Valid Window",

        ])

        # ====================================================
        # RESULTS
        # ====================================================

        for item in results:

            # ------------------------------------------------
            # Defensive handling
            # ------------------------------------------------

            if not isinstance(
                item,
                dict,
            ):

                item = {}

            # ------------------------------------------------
            # Validation
            # ------------------------------------------------

            validation = _get_validation(
                item
            )

            # ------------------------------------------------
            # Parameter
            # ------------------------------------------------

            parameter = item.get(
                "best_parameter",
                {},
            )

            if not isinstance(
                parameter,
                dict,
            ):

                parameter = {}

            # ------------------------------------------------
            # Training
            # ------------------------------------------------

            training = item.get(
                "training",
                {},
            )

            if not isinstance(
                training,
                dict,
            ):

                training = {}

            # ------------------------------------------------
            # Testing
            # ------------------------------------------------

            testing = item.get(
                "testing",
                {},
            )

            if not isinstance(
                testing,
                dict,
            ):

                testing = {}

            # ------------------------------------------------
            # Status
            # ------------------------------------------------

            status = _get_window_status(
                item,
                validation,
            )

            # ------------------------------------------------
            # Reason
            # ------------------------------------------------

            reason = _get_reason(
                item,
                validation,
            )

            # ------------------------------------------------
            # Valid window
            #
            # Only SUCCESS is valid performance evidence.
            # ------------------------------------------------

            valid_window = (
                1
                if status == STATUS_SUCCESS
                else 0
            )

            # =================================================
            # ROW
            # =================================================

            writer.writerow([

                # ------------------------------------------------
                # Window
                # ------------------------------------------------

                item.get(
                    "window",
                    "",
                ),

                # ------------------------------------------------
                # Training
                # ------------------------------------------------

                training.get(
                    "start",
                    "",
                ),

                training.get(
                    "end",
                    "",
                ),

                # ------------------------------------------------
                # Testing
                # ------------------------------------------------

                testing.get(
                    "start",
                    "",
                ),

                testing.get(
                    "end",
                    "",
                ),

                # ------------------------------------------------
                # Parameters
                # ------------------------------------------------

                parameter.get(
                    "RSI_OVERSOLD",
                    "",
                ),

                parameter.get(
                    "RSI_OVERBOUGHT",
                    "",
                ),

                # ------------------------------------------------
                # Validation metrics
                #
                # Failed / insufficient / unknown windows
                # produce empty fields instead of artificial
                # zero values.
                # ------------------------------------------------

                _validation_value(
                    validation,
                    "profit_factor",
                    status,
                ),

                _validation_value(
                    validation,
                    "net_profit",
                    status,
                ),

                _validation_value(
                    validation,
                    "win_rate",
                    status,
                ),

                _validation_value(
                    validation,
                    "max_drawdown",
                    status,
                ),

                # ------------------------------------------------
                # Reliability
                # ------------------------------------------------

                status,

                reason,

                valid_window,

            ])

    # ========================================================
    # RETURN
    # ========================================================

    return output


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "OUTPUT_FILE",

    "STATUS_SUCCESS",

    "STATUS_FAILED",

    "STATUS_INSUFFICIENT",

    "STATUS_UNKNOWN",

    "export_wfo_csv",

]


# ============================================================
# TEST / DEMO
# ============================================================

if __name__ == "__main__":

    sample_results = [

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        {
            "window": 1,

            "status": "SUCCESS",

            "training": {
                "start": 0,
                "end": 5000,
            },

            "testing": {
                "start": 5000,
                "end": 6000,
            },

            "best_parameter": {
                "RSI_OVERSOLD": 10,
                "RSI_OVERBOUGHT": 90,
            },

            "validation": {
                "profit_factor": 1.42,
                "net_profit": 125.50,
                "win_rate": 61.2,
                "max_drawdown": 45.20,
            },
        },

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        {
            "window": 2,

            "status": "SUCCESS",

            "training": {
                "start": 1000,
                "end": 6000,
            },

            "testing": {
                "start": 6000,
                "end": 7000,
            },

            "best_parameter": {
                "RSI_OVERSOLD": 15,
                "RSI_OVERBOUGHT": 85,
            },

            "validation": {
                "profit_factor": 1.18,
                "net_profit": -25.00,
                "win_rate": 48.5,
                "max_drawdown": 80.10,
            },
        },

        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        {
            "window": 3,

            "status": "FAILED",

            "reason":
                "Optimization failed",

            "training": {
                "start": 2000,
                "end": 7000,
            },

            "testing": {
                "start": 7000,
                "end": 8000,
            },

            "validation": {},
        },

        # ----------------------------------------------------
        # INSUFFICIENT
        # ----------------------------------------------------

        {
            "window": 4,

            "status":
                "INSUFFICIENT_DATA",

            "reason":
                "Not enough trades",

            "training": {
                "start": 3000,
                "end": 8000,
            },

            "testing": {
                "start": 8000,
                "end": 9000,
            },

            "validation": {},
        },

        # ----------------------------------------------------
        # LEGACY ZERO-TRADE RESULT
        #
        # No explicit status.
        # Must become INSUFFICIENT_DATA.
        # ----------------------------------------------------

        {
            "window": 5,

            "training": {
                "start": 4000,
                "end": 9000,
            },

            "testing": {
                "start": 9000,
                "end": 10000,
            },

            "best_parameter": {
                "RSI_OVERSOLD": 10,
                "RSI_OVERBOUGHT": 90,
            },

            "validation": {
                "total_trades": 0,
                "net_profit": 0,
                "profit_factor": 0,
            },
        },

    ]

    generated_file = export_wfo_csv(
        sample_results
    )

    print()
    print("=" * 60)
    print("SULTAN QUANT OS")
    print("WFO CSV EXPORTER 5.3.0")
    print("=" * 60)
    print()
    print(
        f"Generated : {generated_file}"
    )
    print()
    print(
        "WFO CSV EXPORT COMPLETE"
    )