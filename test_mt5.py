import MetaTrader5 as mt5
import pandas as pd

print("=== Sultan Quant Lab ===")

if not mt5.initialize():
    print("Gagal koneksi")
    quit()

symbol = "XAUUSDc"

rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M1, 0, 10)

if rates is None:
    print("Data tidak ditemukan.")
    print(mt5.last_error())
else:
    df = pd.DataFrame(rates)
    print(df)

mt5.shutdown()