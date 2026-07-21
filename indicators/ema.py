"""
==========================================
Sultan Quant Lab
Module : EMA Indicator
Version : 2.1
==========================================
"""

import pandas as pd
import config.settings as settings


def add_ema(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menambahkan EMA ke DataFrame.
    """

    if "close" not in df.columns:
        raise ValueError("Kolom 'close' tidak ditemukan.")

    df["EMA20"] = df["close"].ewm(
        span=settings.EMA_FAST,
        adjust=False,
    ).mean()

    df["EMA50"] = df["close"].ewm(
        span=settings.EMA_MIDDLE,
        adjust=False,
    ).mean()

    df["EMA200"] = df["close"].ewm(
        span=settings.EMA_SLOW,
        adjust=False,
    ).mean()

    return df