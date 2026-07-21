def generate_signal(df):

    df["BUY"] = (
        (df["EMA20"] > df["EMA50"]) &
        (df["RSI"] > 50)
    )

    df["SELL"] = (
        (df["EMA20"] < df["EMA50"]) &
        (df["RSI"] < 50)
    )

    return df