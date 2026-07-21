# Sultan Quant Lab

Version : 0.3.0

---

# Project Objective

Membangun platform riset trading profesional yang mampu:

- Backtest Strategy
- Optimize Parameter
- Walk Forward Test
- Monte Carlo
- Multi Strategy
- Export EA MT5

---

# Market

Symbol

XAUUSDc

Broker

HFM

Timeframe

M1

---

# Indicator

EMA

20
50
200

RSI

Period = 2

Oversold = 10

Overbought = 90

ADX

Period = 14

Trend Filter = 25

ATR

Period = 14

Stop Loss = ATR × 1

Take Profit = ATR × 2

Stochastic

21,2,2

Oversold = 10

Overbought = 90

---

# BUY RULE

EMA20 > EMA50 > EMA200

ADX > 25

RSI(2) < 10

Stochastic berada di bawah 10

Golden Cross

Entry pada OPEN candle berikutnya

---

# SELL RULE

EMA20 < EMA50 < EMA200

ADX > 25

RSI(2) > 90

Stochastic berada di atas 90

Death Cross

Entry pada OPEN candle berikutnya

---

# Exit

Take Profit

atau

Stop Loss

---

# Risk Management

Risk

1%

Stop Loss

ATR × 1

Take Profit

ATR × 2

---

# Coding Standard

Seluruh parameter berada di folder config.

Tidak ada angka langsung (magic number) di dalam Strategy.

Semua test harus lulus sebelum Sprint berikutnya.

Metode coding

Hapus File

↓

Copy

↓

Paste

↓

Save

↓

Test

---

# Roadmap

Phase 1

Loader

Indicator

Strategy

Phase 2

Backtest

Trade Log

Report

Phase 3

Optimizer

Walk Forward

Monte Carlo

Phase 4

EA MT5

Telegram AI

Dashboard