==================================================
SULTAN QUANT OS
MODULE CONTRACT v2.5.0
==================================================


PURPOSE

Dokumen ini adalah kontrak antar modul Sultan Quant OS.

Setiap pengembangan baru wajib mengikuti kontrak ini agar:

- Interface tetap stabil
- Modul tidak saling merusak
- Pipeline tetap berjalan
- Pengembangan dapat dilanjutkan lintas versi



==================================================
ARSITEKTUR UTAMA
==================================================


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

   +-----------------------------+

   |                             |

   v                             v

reports                     engine.trade_logger

   |

   +-----------------------------+

   |

   v

reports.report_engine

   |

   v

reports.report_writer

   |

   v

reports.html_report

   |

   v

engine.visual_engine



==================================================
1. ENGINE LOADER
==================================================


File:

engine/loader.py


Function:

load_data(
    filepath
)


Input:

- Path file CSV


Output:

- pandas DataFrame


Contract:

Loader hanya bertugas membaca data.

Tidak boleh:

- Menghitung indikator
- Membuat signal
- Melakukan backtest



==================================================
2. INDICATOR ENGINE
==================================================


File:

engine/indicator_engine.py


Function:

calculate_indicators(
    df
)


Input:

- DataFrame OHLC


Output:

- DataFrame dengan indikator


Current indicators:

- EMA
- RSI
- Stochastic
- ATR
- ADX


Contract:

Indicator Engine hanya menghitung indikator.

Tidak boleh:

- Membuat entry
- Membuat exit
- Mengelola posisi



==================================================
3. STRATEGY ENGINE
==================================================


File:

engine/strategy_engine.py


Function:

run_strategy(
    df,
    strategy
)


Input:

- DataFrame indikator
- Strategy configuration


Output:

- DataFrame dengan signal


Contract:

Strategy Engine bertugas:

- Menentukan entry signal
- Menentukan exit logic


Tidak boleh:

- Menjalankan order
- Menghitung statistik



==================================================
4. BACKTEST ENGINE
==================================================


File:

engine/backtest_engine.py


Function:

run_backtest(
    df
)


Input:

- DataFrame dengan signal


Output:

- list Trade object


Contract:

Backtest Engine bertugas:

- Simulasi transaksi
- Entry
- Exit
- Profit/Loss


Tidak boleh:

- Membuat laporan
- Mengoptimasi parameter



==================================================
5. STATISTICS ENGINE
==================================================


File:

engine/statistics_engine.py


Function:

calculate_statistics(
    trades
)


Input:

- list Trade


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
    average_win,
    average_loss,
    expectancy,
    average_trade,
    max_drawdown,
    sharpe_ratio
}



Contract:

Statistics Engine hanya melakukan analisis performa.


Tidak boleh:

- Menyimpan file
- Membuat grafik
- Membuat HTML



==================================================
6. TRADE LOGGER
==================================================


File:

engine/trade_logger.py


Function:

save_trade_journal(
    trades,
    filename
)


Input:

- list Trade
- lokasi file


Output:

- CSV Trade Journal



Contract:

Trade Logger hanya menyimpan histori transaksi.



==================================================
7. REPORT ENGINE
==================================================


File:

reports/report_engine.py


Function:


generate_report(
    statistics
)


Input:

- dict statistics


Output:

- string laporan


Contoh:


report = generate_report(stats)



Contract:

Report Engine:

- Membuat isi laporan
- Tidak menyimpan file



==================================================
8. REPORT WRITER
==================================================


File:

reports/report_writer.py


Function:


save_report(
    report,
    filename
)


Input:

- string report
- path output


Output:

- file TXT



Contract:

Report Writer hanya bertugas menulis file.



==================================================
9. HTML REPORT ENGINE
==================================================


File:

reports/html_report.py


Function:


generate_html_report(
    statistics
)


Input:

- dict statistics


Output:

- file HTML


Output:

reports/output/backtest_report.html



Contract:

HTML Report Engine:

- Menghasilkan laporan visual HTML
- Menggunakan template
- Menampilkan statistik
- Menghubungkan grafik
- Menghubungkan trade journal



Tidak boleh:

- Mengubah statistik
- Menjalankan backtest



==================================================
10. VISUAL ENGINE
==================================================


File:

engine/visual_engine.py


Function:


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



Contract:

Visual Engine hanya membuat visualisasi.



==================================================
11. OPTIMIZER ENGINE
==================================================


File:

engine/optimizer_engine.py


Function:


optimize(
    data_file,
    parameter_grid
)


Input:

- CSV data
- Parameter grid



Output:

- list dictionary hasil optimasi



Contoh:


[
 {
  "parameter": "...",
  "profit_factor": 2.1,
  "net_profit": 100
 }
]



Contract:


Optimizer Engine bertugas:

- Menjalankan variasi parameter
- Membandingkan hasil
- Melakukan ranking



Tidak boleh:

- Mengubah strategy engine
- Mengubah backtest engine



==================================================
12. OPTIMIZER RUNNER
==================================================


File:

optimizer/optimizer_runner.py



Tugas:


- Menentukan parameter grid
- Menjalankan optimizer
- Menampilkan hasil terbaik



==================================================
13. MAIN PIPELINE
==================================================


File:

main.py



TUGAS:

Sebagai orchestrator.



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

generate_html_report()

        |

save_trade_journal()

        |

generate_visual_reports()



main.py tidak boleh:

- Mengandung logika trading
- Mengandung rumus indikator
- Mengandung optimasi



==================================================
14. REPORT OUTPUT
==================================================


Folder:


reports/output/


Berisi:


backtest_report.txt

backtest_report.html

trade_journal.csv

equity_curve.png

drawdown.png

profit_distribution.png

monthly_returns.png



==================================================
ATURAN PENGEMBANGAN
==================================================


1.

Jangan mengubah nama fungsi lama.


2.

Jangan mengubah jumlah parameter fungsi tanpa update semua caller.


3.

File baru wajib mengikuti kontrak.


4.

Sebelum coding:


- cek siapa import modul
- cek fungsi yang dipanggil
- cek return value


5.

Setiap perubahan wajib:


Compile:


python -m compileall .


Test:


python main.py


Commit:


git add .

git commit

git push



==================================================
CURRENT STATUS
==================================================


Sprint 1.0 Foundation

DONE ✅


Sprint 2.0 Statistics

DONE ✅


Sprint 2.1 Optimizer

DONE ✅


Sprint 2.2 Trade Journal

DONE ✅


Sprint 2.3 Visual Analytics

DONE ✅


Sprint 2.4 HTML Report

DONE ✅



NEXT:


Sprint 2.5 Optimizer Pro


==================================================
END OF CONTRACT
==================================================