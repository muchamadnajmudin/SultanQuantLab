"""
============================================================
SULTAN QUANT OS
Walk Forward Optimization Engine
Version : 3.1.0
============================================================

Responsibilities:

- Split historical data
- Optimize training window
- Validate unseen testing window
- Collect WFO results

WFO DOES NOT:

- calculate indicators
- create strategy signals
- replace backtest engine
- replace statistics engine

============================================================
"""

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
# DEFAULT CONFIG
# ============================================================

DEFAULT_CONFIG = {

    "train_size": 5000,

    "test_size": 1000,

    "step_size": 1000,

}


# ============================================================
# WINDOW GENERATOR
# ============================================================

def generate_windows(
    length,
    train_size,
    test_size,
    step_size,
):

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

    return calculate_statistics(
        trades
    )


# ============================================================
# WALK FORWARD EXECUTION
# ============================================================

def run_walk_forward(
    data_file,
    parameter_grid,
    config=None,
):

    if config is None:

        config = DEFAULT_CONFIG

    df = load_data(
        data_file
    )

    windows = generate_windows(

        length=len(
            df
        ),

        train_size=
            config[
                "train_size"
            ],

        test_size=
            config[
                "test_size"
            ],

        step_size=
            config[
                "step_size"
            ],

    )

    results = []

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

        train_df = df.iloc[

            window[
                "train_start"
            ]:

            window[
                "train_end"
            ]

        ]

        test_df = df.iloc[

            window[
                "test_start"
            ]:

            window[
                "test_end"
            ]

        ]

        # ----------------------------------------------------
        # TRAINING OPTIMIZATION
        # ----------------------------------------------------

        optimization = optimize_dataframe(

            train_df,

            parameter_grid,

        )

        if not optimization:

            continue

        best_parameter = optimization[0]

        # ----------------------------------------------------
        # OUT OF SAMPLE TEST
        # ----------------------------------------------------

        validation = validate_test_window(

            test_df,

            best_parameter,

        )

        results.append(

            {

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

                    best_parameter,

                "validation":

                    validation,

            }

        )

    return results


# ============================================================
# PUBLIC CONTRACT
# ============================================================

__all__ = [

    "DEFAULT_CONFIG",

    "generate_windows",

    "validate_test_window",

    "run_walk_forward",

]