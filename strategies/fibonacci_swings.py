"""
==========================================
SULTAN QUANT OS
Fibonacci Swing Engine
Version : 1.1.0
==========================================

Responsibilities

- Detect Swing High
- Detect Swing Low
- Detect Higher High
- Detect Higher Low
- Detect Lower High
- Detect Lower Low
- Get Latest Swings
- Get Fibonacci Anchor

"""

import pandas as pd


# ==================================================
# DETECT SWINGS
# ==================================================

def detect_swings(
    df: pd.DataFrame,
    lookback: int = 2,
):

    df = df.copy()


    columns = [

        "SWING_HIGH",
        "SWING_LOW",

        "HH",
        "HL",
        "LH",
        "LL",

    ]


    for col in columns:

        if col not in df.columns:

            df[col] = False



    swing_highs = []

    swing_lows = []



    for i in range(

        lookback,

        len(df) - lookback,

    ):


        high = df.iloc[i]["high"]

        low = df.iloc[i]["low"]



        previous_highs = df.iloc[

            i - lookback:i

        ]["high"]



        next_highs = df.iloc[

            i + 1:i + lookback + 1

        ]["high"]



        previous_lows = df.iloc[

            i - lookback:i

        ]["low"]



        next_lows = df.iloc[

            i + 1:i + lookback + 1

        ]["low"]



        # --------------------------------------
        # Swing High
        # --------------------------------------

        if (

            high > previous_highs.max()

            and

            high > next_highs.max()

        ):


            df.at[

                df.index[i],

                "SWING_HIGH"

            ] = True



            swing_highs.append(

                (

                    i,

                    float(high),

                )

            )



        # --------------------------------------
        # Swing Low
        # --------------------------------------

        if (

            low < previous_lows.min()

            and

            low < next_lows.min()

        ):


            df.at[

                df.index[i],

                "SWING_LOW"

            ] = True



            swing_lows.append(

                (

                    i,

                    float(low),

                )

            )




    # ------------------------------------------
    # HH / LH
    # ------------------------------------------

    for j in range(

        1,

        len(swing_highs),

    ):


        prev = swing_highs[j - 1]

        curr = swing_highs[j]


        idx = curr[0]



        if curr[1] > prev[1]:


            df.at[

                df.index[idx],

                "HH"

            ] = True


        else:


            df.at[

                df.index[idx],

                "LH"

            ] = True




    # ------------------------------------------
    # HL / LL
    # ------------------------------------------

    for j in range(

        1,

        len(swing_lows),

    ):


        prev = swing_lows[j - 1]

        curr = swing_lows[j]


        idx = curr[0]



        if curr[1] > prev[1]:


            df.at[

                df.index[idx],

                "HL"

            ] = True


        else:


            df.at[

                df.index[idx],

                "LL"

            ] = True



    return df

# ==================================================
# LAST SWING HIGH
# ==================================================

def last_swing_high(df):

    swings = df[

        df["SWING_HIGH"]

    ]


    if swings.empty:

        return None


    return float(

        swings.iloc[-1]["high"]

    )



# ==================================================
# LAST SWING LOW
# ==================================================

def last_swing_low(df):

    swings = df[

        df["SWING_LOW"]

    ]


    if swings.empty:

        return None


    return float(

        swings.iloc[-1]["low"]

    )



# ==================================================
# LATEST SWINGS
# ==================================================

def latest_swings(df):

    high = last_swing_high(df)

    low = last_swing_low(df)


    return (

        float(high)

        if high is not None

        else None,


        float(low)

        if low is not None

        else None,

    )



# ==================================================
# FIBONACCI ANCHOR
# ==================================================

def fibonacci_anchor(df):

    high, low = latest_swings(df)


    if (

        high is None

        or

        low is None

    ):

        return None


    return {

        "swing_high": high,

        "swing_low": low,

    }



# ==================================================
# HAS VALID SWINGS
# ==================================================

def has_valid_swings(df):

    high, low = latest_swings(df)


    valid = (

        high is not None

        and

        low is not None

        and

        high > low

    )


    return bool(valid)



# ==================================================
# IMPULSE DIRECTION
# ==================================================

def impulse_direction(df):

    high, low = latest_swings(df)


    if (

        high is None

        or

        low is None

    ):

        return "UNKNOWN"


    if high > low:

        return "BULLISH"


    return "BEARISH"    