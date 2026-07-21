# SULTANQUANT_AI_CONTEXT.md

# ==========================================

# SULTAN QUANT LAB

# AI PROJECT CONTEXT

# Version : 1.0

# ==========================================

## PROJECT

Nama Project
SultanQuantLab

Nama Platform
SultanQuant OS

Lead Architect
ChatGPT

Product Owner
Muchamad Najmudin

Bahasa
Python

Target Broker
MetaTrader 5

Target Market

* XAUUSD
* Forex
* Crypto
* Saham

---

# VISI

Membangun framework trading profesional yang dapat digunakan untuk:

* Research Strategy
* Backtesting
* Optimizer
* Portfolio Analysis
* AI Trading Assistant
* Auto Trading
* Telegram Notification
* Professional Reporting

Framework harus modular sehingga mudah dikembangkan.

---

# FILOSOFI PENGEMBANGAN

Prioritas:

1.

Kode yang benar lebih penting daripada kode yang cepat.

2.

Arsitektur lebih penting daripada menambah fitur.

3.

Setiap Sprint harus menghasilkan modul yang selesai.

4.

Tidak mengubah modul yang stabil tanpa alasan kuat.

5.

Semua perubahan harus kompatibel dengan versi sebelumnya.

---

# STRUKTUR PROJECT

config/

engine/

indicators/

strategies/

reports/

tests/

main.py

---

# MODULE YANG SUDAH SELESAI

EMA

RSI (Wilder)

ATR

ADX

Stochastic

Loader

Strategy Engine

Backtest Engine

Risk Engine

Statistics Engine

Trade Object

Report Engine

---

# TRADE OBJECT

Versi

2.1

Field utama

direction

entry_time

symbol

timeframe

strategy

entry_price

exit_price

stop_loss

take_profit

lot_size

risk_reward

profit

profit_percent

status

exit_reason

score

confidence

---

# STATISTICS ENGINE

Versi

2.2

Sudah menghitung:

Total Trade

Winner

Loser

Win Rate

Gross Profit

Gross Loss

Net Profit

Profit Factor

Average Win

Average Loss

Expectancy

Average RR

Maximum Drawdown

Recovery Factor

Sharpe Ratio

Equity Curve

Win Streak

Loss Streak

---

# ROADMAP

CORE ENGINE

✔ selesai

PERFORMANCE ENGINE

Sedang dikerjakan

Target:

Sortino Ratio

Calmar Ratio

MAR Ratio

Kelly Criterion

Risk of Ruin

SQN

Annual Return

Walk Forward Analysis

Monte Carlo

Optimizer

Portfolio

MT5 Integration

Telegram

Dashboard

AI

EA

---

# ATURAN CODING

Gunakan Python.

Gunakan dataclass bila cocok.

Kode harus mudah dibaca.

Hindari duplikasi.

Setiap fungsi memiliki satu tanggung jawab utama.

Pisahkan engine sesuai fungsinya.

---

# ATURAN KERJA

Product Owner tidak perlu menentukan arsitektur.

Lead Architect menentukan:

Roadmap

Sprint

Refactoring

Standar coding

Urutan pengembangan

Product Owner bertugas:

Menjalankan program.

Melaporkan error.

Menguji hasil.

Memberikan ide.

---

# STATUS TERAKHIR

Sprint

2.3

Sedang dikerjakan:

Performance Engine

Belum dimulai:

Walk Forward Analysis

Monte Carlo

Optimizer

Portfolio

MT5 Integration

---

# CARA MELANJUTKAN PROYEK

Jika membuka chat baru:

1.

Upload file ini.

2.

Tulis:

"Lanjutkan SultanQuantLab dari AI Context."

Lead Architect akan membaca file ini terlebih dahulu sebelum melakukan perubahan.

Jangan memulai coding sebelum membaca AI Context.

---

# CATATAN

File ini adalah sumber kebenaran utama proyek.

Semua keputusan baru harus memperbarui file ini.

Versi harus dinaikkan setiap Sprint selesai.

Contoh:

Version 1.1

Version 1.2

Version 2.0
