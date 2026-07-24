"""
==========================================
SULTAN QUANT OS
CSV Exporter
Version : 2.1
==========================================
"""

from pathlib import Path

import pandas as pd


# =====================================================
# CSV EXPORTER
# =====================================================

def export_results(
    results: list[dict],
    filename: str,
) -> Path:
    """
    Export optimizer results to CSV.

    Parameters
    ----------
    results : list[dict]
        Optimizer result.

    filename : str
        Full output filename.

        Example:
            reports/output/optimizer_results.csv

    Returns
    -------
    Path
        Saved csv file path.
    """

    filepath = Path(filename)

    # Buat folder jika belum ada
    filepath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = pd.DataFrame(results)

    df.to_csv(
        filepath,
        index=False,
        encoding="utf-8",
    )

    return filepath