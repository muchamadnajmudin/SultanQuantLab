"""
==========================================
SULTAN QUANT OS
Report Writer
Version : 2.1
==========================================
"""

from pathlib import Path


# =====================================================
# REPORT WRITER
# =====================================================

def save_report(
    report: str,
    filename: str,
) -> Path:
    """
    Save report to text file.

    Parameters
    ----------
    report : str
        Report text.

    filename : str
        Full output filename.
        Example:
            reports/output/backtest_report.txt

    Returns
    -------
    Path
        Saved file path.
    """

    filepath = Path(filename)

    # Buat folder jika belum ada
    filepath.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    filepath.write_text(
        report,
        encoding="utf-8",
    )

    return filepath