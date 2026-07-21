import MetaTrader5 as mt5
import pandas as pd

SYMBOL = "XAUUSDc"
TIMEFRAME = mt5.TIMEFRAME_M1
BARS = 50000

print("Menghubungkan ke MT5...")

if not mt5.initialize():
    print("Gagal:", mt5.last_error())
    quit()

rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, BARS)

if rates is None:
    print("Tidak ada data.")
    mt5.shutdown()
    quit()

df = pd.DataFrame(rates)

df["time"] = pd.to_datetime(df["time"], unit="s")

filename = "data/XAUUSDc_M1.csv"

df.to_csv(filename, index=False)

print("--------------------------------")
print("Export berhasil")
print("Jumlah candle :", len(df))
print("File :", filename)
print("--------------------------------")

mt5.shutdown()