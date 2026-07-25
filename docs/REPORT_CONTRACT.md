# ==================================================
# SULTAN QUANT OS
# REPORT ENGINE CONTRACT
# Version : 2.5.0
# ==================================================


# 1. DOCUMENT PURPOSE


Dokumen ini menjelaskan kontrak resmi modul Report Engine pada Sultan Quant OS.


Report Engine bertugas untuk:

- membuat laporan hasil backtest
- mengubah data statistik menjadi laporan yang mudah dibaca
- menghasilkan format laporan text dan HTML
- menghubungkan hasil analisis dengan visual report


Report Engine adalah modul PRESENTATION.


Report Engine BUKAN:

- Backtest Engine
- Statistics Engine
- Strategy Engine
- Visual Engine
- Trade Logger



==================================================


# 2. DESIGN PRINCIPLE


Report Engine hanya menerima hasil akhir.


Alur:


Statistics Engine

        |

        v

Report Engine

        |

        +----------------+

        |                |

        v                v

TXT Report        HTML Report



Report Engine tidak boleh:

- menghitung profit
- menghitung drawdown
- membuat trade
- membuat signal



==================================================


# 3. MODULE LOCATION


Main module:


reports/report_engine.py



Writer:


reports/report_writer.py



Template:


reports/report_template.py



HTML Generator:


reports/html_report.py



Output:


reports/output/



==================================================


# 4. REPORT ENGINE CONTRACT


## generate_report()


Function:


generate_report(
    statistics: dict
)



Input:


Dictionary hasil Statistics Engine.



Contoh:


{
total_trade:61,
winner:26,
loser:35,
net_profit:88.75,
profit_factor:1.96
}



Output:


String laporan text.



Contoh:


"SULTAN QUANT REPORT

Total Trade : 61

Net Profit : 88.75
"



Catatan:


Function ini TIDAK menyimpan file.



==================================================


# 5. REPORT WRITER CONTRACT


File:


reports/report_writer.py



Function:


save_report(
    report,
    filename
)



Input:


report:

String hasil generate_report()



filename:

Lokasi file output.



Output:


File TXT.



Contoh:


reports/output/backtest_report.txt



==================================================


# 6. HTML REPORT CONTRACT


File:


reports/html_report.py



Function:


generate_html_report(
    statistics,
    output_file
)



Input:


statistics dictionary



Output:


HTML report file.



Output contoh:


reports/output/backtest_report.html



==================================================


# 7. HTML TEMPLATE CONTRACT


File:


reports/report_template.py



Fungsi:


Menyediakan template HTML.



Template harus mendukung:


- Strategy information

- Symbol

- Timeframe

- Generated date

- Performance cards

- Equity Curve

- Drawdown chart

- Profit Distribution

- Monthly Returns

- Trade Journal link



==================================================


# 8. REPORT OUTPUT STRUCTURE



reports/output/


backtest_report.txt


backtest_report.html


trade_journal.csv


equity_curve.png


drawdown.png


profit_distribution.png


monthly_returns.png



==================================================


# 9. PIPELINE POSITION



Main Pipeline:


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



==================================================


# 10. CURRENT FEATURES


Version 2.5.0:


DONE:


- Text Report

- HTML Report

- Performance Dashboard

- Chart Integration

- Trade Journal Integration

- Visual Report Linking



==================================================


# 11. FUTURE DEVELOPMENT


Sprint 2.6:


Planned:


- PDF Report

- Excel Report

- Interactive Dashboard

- Report Comparison


Sprint 3.0:


Institutional Report:


- Multi Strategy Report

- Portfolio Report

- Risk Analysis Report

- AI Generated Summary



==================================================


# 12. DEVELOPMENT RULES


1. Jangan mengubah nama function tanpa update contract.


2. Jangan mengubah input/output tanpa update semua caller.


3. Report Engine hanya membaca hasil analisis.


4. Perhitungan statistik tetap di Statistics Engine.


5. Grafik tetap dibuat oleh Visual Engine.


6. Template HTML tidak boleh berisi logic perhitungan.



==================================================


# 13. CURRENT STATUS


Sprint 1.0 Foundation

DONE


Sprint 2.0 Statistics

DONE


Sprint 2.1 Optimizer

DONE


Sprint 2.2 Trade Journal

DONE


Sprint 2.3 Visual Analytics

DONE


Sprint 2.4 HTML Report

DONE



Current Version:


v2.5.0-stable



Git Tag:


v2.5.0-stable



==================================================


# END OF REPORT CONTRACT
==================================================