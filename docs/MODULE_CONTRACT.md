==================================================
SULTAN QUANT OS
MODULE CONTRACT v2.5.0
==================================================


ARSITEKTUR UTAMA

DATA FLOW:

CSV DATA
   |
   v
engine.loader
   |
   v
engine.indicator_engine
   |
   v
engine.strategy_engine
   |
   v
engine.backtest_engine
   |
   v
engine.statistics_engine
   |
   +----------------+
   |                |
   v                v
reports         trade_logger
   |
   v
visual_engine


==================================================
1. ENGINE LOADER
==================================================

File:
engine/loader.py

Fungsi:

load_data(
    filepath
)

Input:
- path CSV

Output:
- pandas DataFrame


==================================================
2. INDICATOR ENGINE
==================================================

File:
engine/indicator_engine.py

Fungsi:

calculate_indicators(
    df
)

Input:
- DataFrame OHLC

Output:
- DataFrame dengan indikator


==================================================
3. STRATEGY ENGINE
==================================================

File:
engine/strategy_engine.py

Fungsi:

run_strategy(
    df,
    strategy
)

Input:
- DataFrame indikator
- strategy config

Output:
- DataFrame dengan signal


==================================================
4. BACKTEST ENGINE
==================================================

File:
engine/backtest_engine.py

Fungsi:

run_backtest(
    df
)

Input:
- DataFrame signal

Output:
- list trades


==================================================
5. STATISTICS ENGINE
==================================================

File:
engine/statistics_engine.py

Fungsi:

calculate_statistics(
    trades
)

Input:
- list trade

Output:
- dict statistics


Contoh output:

{
total_trade,
winner,
loser,
win_rate,
gross_profit,
gross_loss,
net_profit,
profit_factor,
expectancy,
average_trade,
max_drawdown,
sharpe_ratio
}


==================================================
6. TRADE LOGGER
==================================================

File:
engine/trade_logger.py

Fungsi:

save_trade_journal(
    trades,
    filename
)

Input:
- list trade
- lokasi file

Output:
- CSV


==================================================
7. REPORT ENGINE
==================================================

File:
reports/report_engine.py


KONTRAK PENTING:

generate_report(
    statistics
)

Input:
- dict statistics

Output:
- STRING laporan


Tidak menyimpan file.

Contoh:

report = generate_report(stats)


==================================================
8. REPORT WRITER
==================================================

File:
reports/report_writer.py


Fungsi:

save_report(
    report,
    filename
)

Input:
- string report
- path output


Output:
- file txt


==================================================
9. VISUAL ENGINE
==================================================

File:
engine/visual_engine.py


Fungsi:

generate_visual_reports(
    stats,
    trades
)


Input:
- statistics dict
- trades


Output:

list file grafik


Contoh:

[
equity_curve.png,
drawdown.png,
profit_distribution.png,
monthly_returns.png
]


==================================================
10. MAIN PIPELINE
==================================================

File:

main.py


TUGAS:

Hanya sebagai orchestrator.


ALUR:

load_data()
        |
calculate_indicators()
        |
run_strategy()
        |
run_backtest()
        |
calculate_statistics()
        |
generate_report()
        |
save_report()
        |
save_trade_journal()
        |
generate_visual_reports()


==================================================
ATURAN PENGEMBANGAN
==================================================

1. Jangan mengubah nama fungsi lama.

2. Jangan mengubah jumlah parameter fungsi tanpa update semua caller.

3. File baru harus mengikuti kontrak lama.

4. Sebelum coding modul:
   - cek siapa import modul
   - cek fungsi yang dipanggil
   - cek return value

5. main.py adalah sumber kebenaran alur.


==================================================
STATUS TERAKHIR
==================================================

Sprint 1.0 Foundation          DONE
Sprint 2.0 Statistics          DONE
Sprint 2.1 Optimizer           DONE
Sprint 2.2 Trade Journal       DONE
Sprint 2.3 Visual Analytics    DONE

Output:

reports/output/

- backtest_report.txt
- trade_journal.csv
- equity_curve.png
- drawdown.png
- profit_distribution.png
- monthly_returns.png


NEXT:

Sprint 2.4 HTML Report
==================================================