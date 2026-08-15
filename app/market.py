import requests
import pandas as pd
import numpy as np
from .config import BINANCE_BASE_URL

def fetch_klines(symbol, interval, limit=300):
    r = requests.get(
        f"{BINANCE_BASE_URL}/api/v3/klines",
        params={"symbol": symbol, "interval": interval, "limit": limit},
        timeout=20,
    )
    r.raise_for_status()
    rows = r.json()
    cols = ["open_time","open","high","low","close","volume","close_time",
            "quote_volume","trades","taker_base","taker_quote","ignore"]
    df = pd.DataFrame(rows, columns=cols)
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    return df[["open_time","open","high","low","close","volume"]]

def add_indicators(df):
    x = df.copy()
    x["ema20"] = x["close"].ewm(span=20, adjust=False).mean()
    x["ema50"] = x["close"].ewm(span=50, adjust=False).mean()
    x["ema200"] = x["close"].ewm(span=200, adjust=False).mean()
    delta = x["close"].diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    x["rsi14"] = 100 - (100 / (1 + rs))
    tr = pd.concat([
        x["high"] - x["low"],
        (x["high"] - x["close"].shift()).abs(),
        (x["low"] - x["close"].shift()).abs()
    ], axis=1).max(axis=1)
    x["atr14"] = tr.rolling(14).mean()
    x["swing_high"] = x["high"].rolling(20).max()
    x["swing_low"] = x["low"].rolling(20).min()
    return x

def timeframe_snapshot(symbol, interval):
    df = add_indicators(fetch_klines(symbol, interval))
    row = df.iloc[-1]
    prev = df.iloc[-5]
    if row["close"] > row["ema50"] and row["ema20"] > row["ema50"]:
        trend = "bullish"
    elif row["close"] < row["ema50"] and row["ema20"] < row["ema50"]:
        trend = "bearish"
    else:
        trend = "neutral"
    return {
        "timeframe": interval,
        "close": float(row["close"]),
        "ema20": float(row["ema20"]),
        "ema50": float(row["ema50"]),
        "ema200": float(row["ema200"]),
        "rsi14": float(row["rsi14"]) if pd.notna(row["rsi14"]) else None,
        "atr14": float(row["atr14"]) if pd.notna(row["atr14"]) else None,
        "swing_high_20": float(row["swing_high"]),
        "swing_low_20": float(row["swing_low"]),
        "recent_change_pct": float((row["close"] / prev["close"] - 1) * 100),
        "trend": trend,
    }

def collect_market(symbol):
    return {tf: timeframe_snapshot(symbol, tf) for tf in ["4h","1h","15m","5m"]}
