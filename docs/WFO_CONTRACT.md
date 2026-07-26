# ==================================================
# SULTAN QUANT OS
# WALK FORWARD OPTIMIZATION CONTRACT
# Version : 3.1.0
# ==================================================


# 1. DOCUMENT PURPOSE

Dokumen ini menjelaskan kontrak resmi untuk modul
Walk Forward Optimization Engine pada Sultan Quant OS.

Walk Forward Optimization digunakan untuk:

- menguji kestabilan strategi terhadap data baru
- mengurangi risiko overfitting
- melakukan validasi parameter strategi
- mensimulasikan proses pengembangan strategi profesional


Walk Forward Optimization adalah modul penelitian.


WFO BUKAN:

- Strategy Engine
- Backtest Engine
- Statistics Engine
- Risk Engine
- Report Engine


Optimizer Engine bertugas mencari parameter terbaik.

Walk Forward Optimization bertugas menguji apakah
parameter tersebut tetap bekerja pada data yang belum
pernah dilihat.



# 2. DESIGN PRINCIPLE


Walk Forward Optimization harus mengikuti prinsip:


- tidak boleh terjadi data leakage

- data masa depan tidak boleh digunakan saat training

- parameter hanya berasal dari training window

- testing window harus menggunakan data baru

- setiap eksperimen harus tercatat

- hasil harus dapat direproduksi



# 3. MODULE RESPONSIBILITY


Module utama:

optimizer/walk_forward.py


Tanggung jawab:

- membagi dataset menjadi training window dan testing window

- menjalankan optimizer pada training window

- mengambil parameter terbaik

- menjalankan validasi pada testing window

- mengumpulkan hasil setiap periode

- menghasilkan evaluasi WFO


WFO hanya melakukan orkestrasi.


WFO TIDAK BOLEH:

- menghitung indikator sendiri

- membuat signal strategy sendiri

- menjalankan backtest sendiri

- menghitung statistik sendiri

# 4. SYSTEM ARCHITECTURE


Flow:


Market Data

      |
      v

Loader Engine

      |
      v

Walk Forward Engine

      |
      +----------------+
      |                |
      v                v

Training Window    Testing Window

      |
      v

Optimizer Engine

      |
      v

Best Parameters

      |
      v

Strategy Engine

      |
      v

Backtest Engine

      |
      v

Statistics Engine

      |
      v

WFO Result

# 5. INPUT CONTRACT

Input minimal:


{
    "data_file":
        "data/XAUUSDc_M1.csv",


    "train_size":
        5000,


    "test_size":
        1000,


    "parameters":

    {

        "RSI_OVERSOLD":
            [5,10,15],


        "RSI_OVERBOUGHT":
            [85,90,95]

    },


    "step_size":
        1000,


    "rolling":
        True
}