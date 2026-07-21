from engine.loader import load_data
from engine.indicator_engine import calculate_indicators

df = load_data("data/XAUUSDc_M1.csv")
df = calculate_indicators(df)

print(df[["ADX"]].tail(20))