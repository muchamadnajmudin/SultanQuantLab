"""
==========================================
Sultan Quant Lab
Module : Stochastic Indicator
Version : 2.1
Method : MT5 Compatible
==========================================
"""

import pandas as pd
import config.settings as settings


def add_stochastic(
    df: pd.DataFrame,
) -> pd.DataFrame:

    lowest_low = (
        df["low"]
        .rolling(
            window=settings.STOCH_K
        )
        .min()
    )

    highest_high = (
        df["high"]
        .rolling(
            window=settings.STOCH_K
        )
        .max()
    )


    denominator = highest_high - lowest_low


    fast_k = (
        100
        * (df["close"] - lowest_low)
        / denominator.replace(0, 1)
    )


    slow_k = (
        fast_k
        .rolling(
            window=settings.STOCH_SMOOTH
        )
        .mean()
    )


    slow_d = (
        slow_k
        .rolling(
            window=settings.STOCH_D
        )
        .mean()
    )


    df["%K"] = slow_k
    df["%D"] = slow_d


    return df