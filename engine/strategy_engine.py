"""
==========================================
Sultan Quant Lab
Module : Strategy Engine
Version : 2.1
==========================================
"""

import pandas as pd

from strategies.xau_strategy import generate_signal


def run_strategy(
    df: pd.DataFrame,
    strategy: str = "xau_strategy",
    **params,
) -> pd.DataFrame:
    """
    Menjalankan strategy yang dipilih.

    Parameters
    ----------
    strategy : str
        Nama strategy.
    params :
        Parameter yang diteruskan ke strategy.
    """

    if strategy == "xau_strategy":

        return generate_signal(
            df,
            **params,
        )

    raise ValueError(
        f"Strategy '{strategy}' tidak ditemukan."
    )