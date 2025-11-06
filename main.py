from fastapi import FastAPI
import yfinance as yf
from datetime import datetime

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}

@app.post("/ingest/prices")
def ingest_prices(symbol: str = "SPY", period: str = "1mo"):
    data = yf.download(symbol, period=period)
    prices = []
    for idx, row in data.iterrows():
        prices.append({
            "date": idx.strftime("%Y-%m-%d"),
            "close": float(row["Close"])
        })
    return {"count": len(prices), "data": prices}

@app.get("/prices")
def get_prices(symbol: str = "SPY", period: str = "1mo"):
    data = yf.download(symbol, period=period)
    prices = []
    for idx, row in data.iterrows():
        prices.append({
            "date": idx.strftime("%Y-%m-%d"),
            "close": float(row["Close"])
        })
    return prices

