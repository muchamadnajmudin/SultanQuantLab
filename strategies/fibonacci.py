"""
==========================================
SULTAN QUANT OS
Fibonacci Retracement Strategy
Version : 2.0.0
==========================================

Responsibilities

- Generate Fibonacci Signal
- Detect Swing
- Calculate Fibonacci
- Inject Fibonacci Levels
- Fibonacci Confluence
- Confirmation Score
- Execute BUY
- Execute SELL

"""


from strategies.base_strategy import prepare_dataframe


from strategies.fibonacci_swings import (
    detect_swings,
    latest_swings,
)


from strategies.fibonacci_engine import (
    calculate_fibonacci,
)


from strategies.fibonacci_confirmation import (
    confirmation_score,
)


from strategies.confluence.fibonacci import (
    fibonacci_score,
    fibonacci_bias,
)


from strategies.fibonacci_trade import (
    execute_buy,
    execute_sell,
)



# ==================================================
# INJECT FIBONACCI LEVEL
# ==================================================

def inject_fibonacci_levels(
    df,
    levels,
):

    retracement = levels["retracement"]


    df["FIB_000"] = retracement["0.000"]

    df["FIB_236"] = retracement["0.236"]

    df["FIB_382"] = retracement["0.382"]

    df["FIB_500"] = retracement["0.500"]

    df["FIB_618"] = retracement["0.618"]

    df["FIB_705"] = retracement["0.705"]

    df["FIB_786"] = retracement["0.786"]

    df["FIB_1000"] = retracement["1.000"]


    return df




# ==================================================
# GENERATE SIGNAL
# ==================================================

def generate_signal(df):


    df = prepare_dataframe(df)



    # ------------------------------------------
    # INITIAL COLUMN
    # ------------------------------------------

    required = {

        "BUY": False,

        "SELL": False,

        "SL": 0.0,

        "TP": 0.0,

    }


    for column, value in required.items():

        if column not in df.columns:

            df[column] = value



    # ------------------------------------------
    # DETECT SWING
    # ------------------------------------------

    df = detect_swings(
        df
    )


    swing_high, swing_low = latest_swings(
        df
    )


    if (

        swing_high is None

        or

        swing_low is None

    ):

        return df



    # ------------------------------------------
    # CALCULATE FIBONACCI
    # ------------------------------------------

    levels = calculate_fibonacci(

        swing_high,

        swing_low,

    )



    # ------------------------------------------
    # INJECT LEVEL
    # ------------------------------------------

    df = inject_fibonacci_levels(

        df,

        levels,

    )



    # ------------------------------------------
    # TRADING LOOP
    # ------------------------------------------

    for i in range(len(df)):


        row = df.iloc[i]


        price = row["close"]


        atr = (

            row["ATR"]

            if "ATR" in row

            else 1.0

        )



        # --------------------------------------
        # CONFIRMATION
        # --------------------------------------

        confirm = confirmation_score(

            row,

        )



        # --------------------------------------
        # FIBONACCI CONFLUENCE
        # --------------------------------------

        fib_score = fibonacci_score(

            price,

            levels,

        )


        bias = fibonacci_bias(

            price,

            levels,

        )



        total_score = (

            confirm

            +

            fib_score

        )



        df.at[

            df.index[i],

            "FIB_SCORE"

        ] = fib_score



        df.at[

            df.index[i],

            "TOTAL_SCORE"

        ] = total_score



        # --------------------------------------
        # BUY
        # --------------------------------------

        if (

            bias in (

                "BUY",

                "STRONG_BUY",

            )

            and total_score >= 80

        ):


            df = execute_buy(

                df=df,

                index=i,

                entry=price,

                atr=atr,

                confirmation_score=confirm,

                pattern_score=fib_score,

                structure_score=0,

            )



        # --------------------------------------
        # SELL
        # --------------------------------------

        elif (

            bias in (

                "SELL",

                "STRONG_SELL",

            )

            and total_score <= -60

        ):


            df = execute_sell(

                df=df,

                index=i,

                entry=price,

                atr=atr,

                confirmation_score=confirm,

                pattern_score=fib_score,

                structure_score=0,

            )



    return df