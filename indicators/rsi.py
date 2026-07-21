"""
==========================================
Sultan Quant Lab
Module : RSI Indicator
Version : 2.1
Method : Wilder RSI
==========================================
"""

import pandas as pd
import config.settings as settings


def add_rsi(df: pd.DataFrame) -> pd.DataFrame:

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = (
        gain
        .ewm(
            alpha=1 / settings.RSI_PERIOD,
            adjust=False
        )
        .mean()
    )

    avg_loss = (
        loss
        .ewm(
            alpha=1 / settings.RSI_PERIOD,
            adjust=False
        )
        .mean()
    )

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    return df