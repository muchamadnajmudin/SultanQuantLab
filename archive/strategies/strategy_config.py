"""
==========================================
Sultan Quant Lab
Strategy Configuration
Version : 0.3.1
==========================================
"""

# ==========================
# EMA
# ==========================

EMA_FAST = 20
EMA_MIDDLE = 50
EMA_SLOW = 200

# ==========================
# RSI
# ==========================

RSI_PERIOD = 2

RSI_OVERSOLD = 10
RSI_OVERBOUGHT = 90

# ==========================
# ADX
# ==========================

ADX_PERIOD = 14

ADX_MIN = 25

# ==========================
# ATR
# ==========================

ATR_PERIOD = 14

ATR_SL_MULTIPLIER = 1.0
ATR_TP_MULTIPLIER = 2.0

# ==========================
# STOCHASTIC
# ==========================

STOCH_K = 21
STOCH_D = 2
STOCH_SMOOTH = 2

STOCH_OVERSOLD = 10
STOCH_OVERBOUGHT = 90

# ==========================
# ENTRY
# ==========================

ENTRY_NEXT_CANDLE = True

# ==========================
# RISK
# ==========================

RISK_PER_TRADE = 0.01