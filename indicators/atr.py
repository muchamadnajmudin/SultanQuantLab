"""
==========================================
Sultan Quant Lab
Module : ATR Indicator
Version : 2.1
==========================================
"""

import pandas as pd
from ta.volatility import AverageTrueRange
import config.settings as settings


def add_atr(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menambahkan indikator ATR (Average True Range)
    menggunakan implementasi standar Wilder.
    """

    required_columns = ["high", "low", "close"]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"Kolom '{column}' tidak ditemukan."
            )

    atr = AverageTrueRange(
        high=df["high"],
        low=df["low"],
        close=df["close"],
        window=settings.ATR_PERIOD,
    )

    df["ATR"] = atr.average_true_range()

    return df