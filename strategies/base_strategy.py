"""
==========================================
SULTAN QUANT OS
Base Strategy
Version : 1.1.0
==========================================

Responsibilities:

- Prepare dataframe
- Initialize BUY / SELL
- Initialize SL / TP
- Backward compatibility

"""

# ==================================================
# PREPARE DATAFRAME
# ==================================================

def prepare_dataframe(df):

    df = df.copy()

    if "BUY" not in df.columns:
        df["BUY"] = False

    if "SELL" not in df.columns:
        df["SELL"] = False

    if "SL" not in df.columns:
        df["SL"] = 0.0

    if "TP" not in df.columns:
        df["TP"] = 0.0

    return df


# ==================================================
# BACKWARD COMPATIBILITY
# ==================================================

def initialize_strategy(df):
    """
    Alias lama agar modul lama tetap berjalan.
    """
    return prepare_dataframe(df)