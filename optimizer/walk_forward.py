"""
============================================================
SULTAN QUANT OS
Walk Forward Optimization Engine
Version : 3.2.0
============================================================

Responsibilities:

- Split historical data
- Optimize training window
- Validate unseen testing window
- Collect WFO results
- Preserve failed/insufficient windows explicitly

WFO DOES NOT:

- calculate indicators
- create strategy signals
- replace backtest engine
- replace statistics engine
- perform portfolio governance
- perform portfolio allocation

Design principles:

- Training data is used only for optimization.
- Testing data is unseen by the optimizer.
- Failed windows are recorded, not silently discarded.
- Insufficient validation windows are distinguishable
  from genuine losing strategy windows.
- Existing WFO result fields are preserved.
- Existing public functions remain available.

============================================================
"""


from copy import deepcopy


from engine.loader import load_data

from engine.optimizer_engine import (
    optimize_dataframe,
)

from engine.indicator_engine import (
    calculate_indicators,
)

from engine.strategy_engine import (
    run_strategy,
)

from engine.backtest_engine import (
    run_backtest,
)

from engine.statistics_engine import (
    calculate_statistics,
)


# ============================================================
# STATUS CONSTANTS
# ============================================================

STATUS_SUCCESS = "SUCCESS"

STATUS_FAILED = "FAILED"

STATUS_INSUFFICIENT = "INSUFFICIENT_DATA"


# ============================================================
# DEFAULT CONFIG
# ============================================================

DEFAULT_CONFIG = {

    "train_size": 5000,

    "test_size": 1000,

    "step_size": 1000,

}


# ============================================================
# CONFIG VALIDATION
# ============================================================

def _validate_config(
    config,
):
    """
    Validate WFO configuration.

    Returns
    -------
    dict
        Independent copy of the validated configuration.

    Raises
    ------
    ValueError
        If a window parameter is invalid.
    """

    if config is None:

        config = DEFAULT_CONFIG

    if not isinstance(
        config,
        dict,
    ):

        raise TypeError(
            "WFO config must be a dictionary."
        )

    prepared = deepcopy(
        config
    )

    required_keys = (

        "train_size",

        "test_size",

        "step_size",

    )

    for key in required_keys:

        if key not in prepared:

            raise ValueError(
                f"Missing WFO config: {key}"
            )

        value = prepared[key]

        if isinstance(
            value,
            bool,
        ):

            raise ValueError(
                f"WFO config '{key}' must be a positive integer."
            )

        try:

            value = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            raise ValueError(
                f"WFO config '{key}' must be a positive integer."
            )

        if value <= 0:

            raise ValueError(
                f"WFO config '{key}' must be greater than zero."
            )

        prepared[key] = value

    return prepared


# ============================================================
# WINDOW GENERATOR
# ============================================================

def generate_windows(
    length,
    train_size,
    test_size,
    step_size,
):
    """
    Generate rolling walk-forward train/test windows.

    Parameters
    ----------
    length : int
        Total number of observations.

    train_size : int
        Number of observations used for training.

    test_size : int
        Number of observations used for out-of-sample
        validation.

    step_size : int
        Number of observations by which the window advances.

    Returns
    -------
    list[dict]

        Each window contains:

        - train_start
        - train_end
        - test_start
        - test_end
    """

    try:

        length = int(
            length
        )

        train_size = int(
            train_size
        )

        test_size = int(
            test_size
        )

        step_size = int(
            step_size
        )

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "WFO window parameters must be integers."
        )

    if length < 0:

        raise ValueError(
            "length cannot be negative."
        )

    if train_size <= 0:

        raise ValueError(
            "train_size must be greater than zero."
        )

    if test_size <= 0:

        raise ValueError(
            "test_size must be greater than zero."
        )

    if step_size <= 0:

        raise ValueError(
            "step_size must be greater than zero."
        )

    windows = []

    start = 0

    while True:

        train_start = start

        train_end = (
            train_start
            +
            train_size
        )

        test_start = train_end

        test_end = (
            test_start
            +
            test_size
        )

        if test_end > length:

            break

        windows.append(

            {

                "train_start":
                    train_start,

                "train_end":
                    train_end,

                "test_start":
                    test_start,

                "test_end":
                    test_end,

            }

        )

        start += step_size

    return windows


# ============================================================
# VALIDATE TEST WINDOW
# ============================================================

def validate_test_window(
    df,
    parameter,
):
    """
    Validate one unseen testing window.

    Pipeline:

        test data
            ↓
        indicators
            ↓
        strategy
            ↓
        backtest
            ↓
        statistics

    The function preserves the historical behavior of
    returning the statistics dictionary directly.

    Status classification is handled by the WFO execution
    layer so existing callers remain compatible.
    """

    if parameter is None:

        raise ValueError(
            "WFO validation parameter cannot be None."
        )

    if not isinstance(
        parameter,
        dict,
    ):

        raise TypeError(
            "WFO validation parameter must be a dictionary."
        )

    required_parameters = (

        "RSI_OVERSOLD",

        "RSI_OVERBOUGHT",

    )

    for key in required_parameters:

        if key not in parameter:

            raise ValueError(
                f"Missing WFO parameter: {key}"
            )

    data = df.copy()

    data = calculate_indicators(
        data
    )

    data = run_strategy(

        data,

        rsi_oversold=
            parameter[
                "RSI_OVERSOLD"
            ],

        rsi_overbought=
            parameter[
                "RSI_OVERBOUGHT"
            ],

    )

    trades = run_backtest(
        data
    )

    validation = calculate_statistics(
        trades
    )

    if validation is None:

        return {}

    return validation


# ============================================================
# DETECT INSUFFICIENT VALIDATION
# ============================================================

def _is_insufficient_validation(
    validation,
):
    """
    Determine whether validation contains enough trading
    information to be treated as a usable performance window.

    Important:

    A zero net profit is NOT automatically considered
    insufficient.

    If explicit trade-count information exists, it is used.

    Otherwise the historical statistics result is preserved
    and considered usable.
    """

    if not isinstance(
        validation,
        dict,
    ):

        return True

    total_trade = validation.get(
        "total_trade",
        validation.get(
            "total_trades",
            None,
        ),
    )

    if total_trade is not None:

        try:

            return int(
                float(
                    total_trade
                )
            ) <= 0

        except (
            TypeError,
            ValueError,
        ):

            return True

    trades = validation.get(
        "trades",
        None,
    )

    if trades is not None:

        try:

            return len(
                trades
            ) == 0

        except TypeError:

            return True

    # --------------------------------------------------------
    # Legacy statistics dictionaries do not necessarily expose
    # trade-count information. Preserve them as usable.
    # --------------------------------------------------------

    return False


# ============================================================
# WALK FORWARD EXECUTION
# ============================================================

def run_walk_forward(
    data_file,
    parameter_grid,
    config=None,
):
    """
    Execute Walk Forward Optimization.

    Parameters
    ----------
    data_file : str | Path
        Historical market data.

    parameter_grid : dict
        Optimization parameter grid.

    config : dict | None
        WFO window configuration.

    Returns
    -------
    list[dict]

        WFO window results.

    Existing result fields are preserved:

        window
        training
        testing
        best_parameter
        validation

    Additional fields:

        status
        reason

    Technical failures are recorded explicitly rather than
    silently removed from the result set.
    """

    # ========================================================
    # PREPARE CONFIG
    # ========================================================

    prepared_config = _validate_config(
        config
    )

    # ========================================================
    # VALIDATE PARAMETER GRID
    # ========================================================

    if not isinstance(
        parameter_grid,
        dict,
    ):

        raise TypeError(
            "parameter_grid must be a dictionary."
        )

    prepared_parameter_grid = deepcopy(
        parameter_grid
    )

    # ========================================================
    # LOAD DATA
    # ========================================================

    df = load_data(
        data_file
    )

    if df is None:

        raise ValueError(
            "WFO data loader returned no data."
        )

    try:

        data_length = len(
            df
        )

    except TypeError:

        raise TypeError(
            "WFO data must be a sized data object."
        )

    # ========================================================
    # GENERATE WINDOWS
    # ========================================================

    windows = generate_windows(

        length=data_length,

        train_size=
            prepared_config[
                "train_size"
            ],

        test_size=
            prepared_config[
                "test_size"
            ],

        step_size=
            prepared_config[
                "step_size"
            ],

    )

    results = []

    # ========================================================
    # EXECUTE WINDOWS
    # ========================================================

    for index, window in enumerate(
        windows
    ):

        print()

        print(
            "=" * 50
        )

        print(
            f"WFO WINDOW {index + 1}"
        )

        print(
            "=" * 50
        )

        # ----------------------------------------------------
        # SLICE TRAINING DATA
        # ----------------------------------------------------

        train_df = df.iloc[

            window[
                "train_start"
            ]:

            window[
                "train_end"
            ]

        ]

        # ----------------------------------------------------
        # SLICE TESTING DATA
        # ----------------------------------------------------

        test_df = df.iloc[

            window[
                "test_start"
            ]:

            window[
                "test_end"
            ]

        ]

        # ----------------------------------------------------
        # BASE RESULT
        # ----------------------------------------------------

        window_result = {

            "window":

                index + 1,

            "training":

                {

                    "start":
                        window[
                            "train_start"
                        ],

                    "end":
                        window[
                            "train_end"
                        ],

                },

            "testing":

                {

                    "start":
                        window[
                            "test_start"
                        ],

                    "end":
                        window[
                            "test_end"
                        ],

                },

            "best_parameter":

                {},

            "validation":

                {},

            "status":

                STATUS_SUCCESS,

        }

        # ====================================================
        # TRAINING OPTIMIZATION
        # ====================================================

        try:

            optimization = optimize_dataframe(

                train_df,

                prepared_parameter_grid,

            )

        except Exception as exc:

            window_result[
                "status"
            ] = STATUS_FAILED

            window_result[
                "reason"
            ] = (
                f"Optimization failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            results.append(
                window_result
            )

            continue

        # ----------------------------------------------------
        # NO OPTIMIZATION RESULT
        # ----------------------------------------------------

        if not optimization:

            window_result[
                "status"
            ] = STATUS_FAILED

            window_result[
                "reason"
            ] = (
                "Optimization returned no result."
            )

            results.append(
                window_result
            )

            continue

        # ----------------------------------------------------
        # BEST PARAMETER
        # ----------------------------------------------------

        best_parameter = optimization[0]

        if not isinstance(
            best_parameter,
            dict,
        ):

            window_result[
                "status"
            ] = STATUS_FAILED

            window_result[
                "reason"
            ] = (
                "Optimization returned an "
                "invalid best parameter."
            )

            results.append(
                window_result
            )

            continue

        window_result[
            "best_parameter"
        ] = deepcopy(
            best_parameter
        )

        # ====================================================
        # OUT-OF-SAMPLE TEST
        # ====================================================

        try:

            validation = (
                validate_test_window(

                    test_df,

                    best_parameter,

                )
            )

        except Exception as exc:

            window_result[
                "status"
            ] = STATUS_FAILED

            window_result[
                "reason"
            ] = (
                f"Validation failed: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )

            results.append(
                window_result
            )

            continue

        # ----------------------------------------------------
        # VALIDATION RESULT
        # ----------------------------------------------------

        if not isinstance(
            validation,
            dict,
        ):

            window_result[
                "status"
            ] = STATUS_FAILED

            window_result[
                "reason"
            ] = (
                "Validation returned "
                "an invalid result."
            )

            results.append(
                window_result
            )

            continue

        window_result[
            "validation"
        ] = deepcopy(
            validation
        )

        # ----------------------------------------------------
        # INSUFFICIENT DATA
        # ----------------------------------------------------

        if _is_insufficient_validation(
            validation
        ):

            window_result[
                "status"
            ] = STATUS_INSUFFICIENT

            window_result[
                "reason"
            ] = (
                "Validation window contains "
                "insufficient trading data."
            )

        else:

            window_result[
                "status"
            ] = STATUS_SUCCESS

        # ----------------------------------------------------
        # STORE RESULT
        # ----------------------------------------------------

        results.append(
            window_result
        )

    return results


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "DEFAULT_CONFIG",

    "STATUS_SUCCESS",

    "STATUS_FAILED",

    "STATUS_INSUFFICIENT",

    "generate_windows",

    "validate_test_window",

    "run_walk_forward",

]