# ==================================================
# SULTAN QUANT OS
# RISK ENGINE CONTRACT
# Version : 2.5.0
# ==================================================


# 1. DOCUMENT PURPOSE


Dokumen ini menjelaskan kontrak resmi modul Risk Engine pada Sultan Quant OS.


Risk Engine bertugas untuk:

- mengatur risiko per transaksi
- menghitung ukuran posisi
- mengontrol batas risiko
- mendukung pengembangan money management


Risk Engine adalah modul RISK MANAGEMENT.


Risk Engine BUKAN:

- Strategy Engine
- Signal Generator
- Backtest Engine
- Statistics Engine
- Execution Engine



==================================================


# 2. DESIGN PRINCIPLE


Risk Engine bekerja setelah signal dibuat.


Alur:


Market Data

    |

    v

Indicator Engine

    |

    v

Strategy Engine

    |

    v

Risk Engine

    |

    v

Backtest Engine



Risk Engine menentukan:

- berapa risiko
- berapa ukuran posisi
- batas kerugian


Risk Engine tidak menentukan:

- kapan entry
- arah BUY / SELL



==================================================


# 3. MODULE LOCATION


File:


engine/risk_engine.py



==================================================


# 4. CURRENT RESPONSIBILITY


Version 2.5.0:


Risk Engine bertanggung jawab untuk:


## Risk Per Trade


Menggunakan:


RISK_PER_TRADE



Contoh:


Risk 1%


dari balance:


10000


maka:


Maximum risk:

100



==================================================


# 5. CONFIGURATION CONTRACT


Sumber konfigurasi:


config/settings.py



Parameter:


RISK_PER_TRADE = 0.01


MAX_OPEN_TRADES = 1


INITIAL_BALANCE = 10000.0



==================================================


# 6. FUNCTION CONTRACT


## calculate_position_size()


Function:


calculate_position_size(
    balance,
    risk_percent,
    stop_loss_distance
)



Input:


balance:

Total modal



risk_percent:

Persentase risiko



stop_loss_distance:

Jarak stop loss



Output:


Position size



Formula:


Risk Amount:


balance * risk_percent



Position Size:


risk_amount / stop_loss_distance



==================================================


# 7. STOP LOSS CONTRACT


Stop Loss berasal dari:


ATR Engine



Parameter:


ATR_PERIOD


ATR_SL_MULTIPLIER



Default:


ATR_PERIOD = 14


ATR_SL_MULTIPLIER = 1.0



Risk Engine hanya menerima nilai SL.


Risk Engine tidak menghitung ATR.



==================================================


# 8. TAKE PROFIT CONTRACT


Take Profit berasal dari:


ATR Model



Parameter:


ATR_TP_MULTIPLIER



Default:


ATR_TP_MULTIPLIER = 2.0



Risk Engine tidak menentukan strategi exit.



==================================================


# 9. BACKTEST INTEGRATION


Alur:


Strategy Signal

        |

        v

Risk Calculation

        |

        v

Trade Execution Simulation

        |

        v

Statistics Engine



==================================================


# 10. CURRENT FEATURES


Version 2.5.0:


DONE:


- Risk Parameter Configuration

- ATR Based Risk Support

- Maximum Open Trade Control

- Risk Per Trade Support



==================================================


# 11. LIMITATION


Version 2.5.0 BELUM mendukung:


- Dynamic Position Sizing

- Portfolio Risk

- Correlation Risk

- Risk Parity

- Kelly Criterion

- Monte Carlo Risk Simulation



==================================================


# 12. FUTURE DEVELOPMENT


Sprint 3.0:


Institutional Risk Engine:


Planned:


- Advanced Position Sizing

- Portfolio Risk Manager

- Maximum Daily Loss

- Maximum Drawdown Protection

- Risk Dashboard

- Monte Carlo Risk Analysis



==================================================


# 13. DEVELOPMENT RULES


1. Risk Engine tidak boleh membuat signal.


2. Risk Engine tidak boleh mengubah strategi.


3. Risk Engine tidak boleh menghitung statistik performa.


4. Semua parameter risiko harus berasal dari config.


5. Perubahan function wajib update contract.


6. Backtest harus tetap kompatibel.



==================================================


# 14. CURRENT STATUS


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


# END OF RISK CONTRACT
==================================================