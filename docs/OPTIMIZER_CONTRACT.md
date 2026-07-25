# ==================================================
# SULTAN QUANT OS
# OPTIMIZER CONTRACT
# Version : 2.5.0
# ==================================================


# 1. DOCUMENT PURPOSE

Dokumen ini menjelaskan kontrak resmi untuk modul Optimizer Engine pada Sultan Quant OS.

Optimizer Engine digunakan untuk:

- melakukan pengujian parameter strategi
- membandingkan performa berbagai konfigurasi
- mencari kombinasi parameter terbaik
- menyimpan hasil eksperimen secara terstruktur
- mendukung penelitian strategi kuantitatif


Optimizer adalah modul penelitian.


Optimizer BUKAN:

- Strategy Engine
- Backtest Engine
- Statistics Engine
- Risk Engine
- Execution Engine


Optimizer hanya mengorkestrasi proses pengujian.


==================================================


# 2. DESIGN PRINCIPLE


Optimizer harus mengikuti prinsip:


1. Tidak memiliki logika entry trading.

2. Tidak membuat signal BUY / SELL.

3. Tidak menghitung profit sendiri.

4. Tidak menghitung statistik sendiri.

5. Tidak mengubah data market.


Optimizer hanya melakukan:

Parameter
    |
    v
Strategy
    |
    v
Backtest
    |
    v
Statistics
    |
    v
Ranking



==================================================


# 3. MODULE LOCATION


File utama:


engine/optimizer_engine.py


Runner:


optimizer/optimizer_runner.py



==================================================


# 4. DEPENDENCY FLOW


Optimizer Engine menggunakan:


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



Optimizer tidak boleh memanggil:

- report engine
- visual engine
- trade logger



==================================================


# 5. FUNCTION CONTRACT


## 5.1 run_single_test()


Function:


run_single_test(
    data_file: str,
    rsi_oversold: int,
    rsi_overbought: int
)


Input:


data_file

Path file market CSV


rsi_oversold

Parameter RSI bawah


rsi_overbought

Parameter RSI atas



Process:


1. Load data

2. Calculate indicators

3. Run strategy

4. Run backtest

5. Calculate statistics



Output:


dict statistics


Contoh:


{
total_trade,
winner,
loser,
win_rate,
net_profit,
profit_factor,
max_drawdown,
sharpe_ratio,

RSI_OVERSOLD,
RSI_OVERBOUGHT
}



==================================================


# 6. OPTIMIZE FUNCTION


Function:


optimize(
    data_file,
    parameter_grid
)


Input:


parameter_grid:


{
    "RSI_OVERSOLD":[5,10,15],

    "RSI_OVERBOUGHT":[85,90,95]
}



Process:


Membuat kombinasi:


RSI 5
+
RSI 85


RSI 5
+
RSI 90


RSI 5
+
RSI 95


dan seterusnya.



Output:


list[dict]


Contoh:


[
 {
  "RSI_OVERSOLD":5,
  "RSI_OVERBOUGHT":90,
  "profit_factor":2.08,
  "net_profit":90.74
 }
]



==================================================


# 7. RANKING CONTRACT


Function:


rank_results(
    results
)



Tujuan:


Mengurutkan hasil eksperimen.



Prioritas ranking:


1. Profit Factor

2. Net Profit



Formula:


Higher Profit Factor
        |
        v
Higher Net Profit
        |
        v
Best Result



==================================================


# 8. BEST RESULT


Function:


get_best_result(
    results
)



Input:


list hasil optimizer



Output:


dict hasil terbaik



Jika kosong:


return {}



==================================================


# 9. CURRENT PARAMETERS


Version 2.5.0 mendukung:


## RSI Optimization


RSI_OVERSOLD:

[
5,
10,
15
]


RSI_OVERBOUGHT:

[
85,
90,
95
]



==================================================


# 10. CURRENT OPTIMIZATION RESULT


Benchmark terakhir:


Best Parameter:


RSI_OVERSOLD:

5


RSI_OVERBOUGHT:

90



Performance:


Total Trade:

56


Win Rate:

44.64%


Net Profit:

90.74


Profit Factor:

2.08


Maximum Drawdown:

13.92


Drawdown Percentage:

15.34


Recovery Factor:

6.52


Sharpe Ratio:

0.28



==================================================


# 11. OPTIMIZER LIMITATION


Version 2.5.0 BELUM mendukung:


- EMA optimization

- ATR optimization

- ADX optimization

- Multi parameter grid

- Walk Forward Optimization

- Monte Carlo Simulation

- Genetic Algorithm



==================================================


# 12. FUTURE DEVELOPMENT


Sprint 2.5


Optimizer Pro:


Planned:


- Multi parameter optimization

- Grid Search engine improvement

- Result CSV export

- Top 10 ranking

- Parameter heatmap



Sprint 3.0:


Institutional Research:


- Walk Forward Optimization

- Monte Carlo Analysis

- Robustness Testing

- Multi Symbol Testing



==================================================


# 13. DEVELOPMENT RULES


1. Jangan mengubah nama function tanpa update semua caller.


2. Jangan mengubah parameter function tanpa update contract.


3. Jangan memasukkan logic strategy ke optimizer.


4. Jangan memasukkan logic backtest ke optimizer.


5. Semua hasil optimizer harus berasal dari Statistics Engine.


6. Optimizer hanya mengatur eksperimen.



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



Current:

Version 2.5.0 Stable



Git Tag:


v2.5.0-stable



==================================================


# END OF OPTIMIZER CONTRACT
==================================================