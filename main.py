@app.post("/ingest/prices")
def ingest_prices(symbol: str = Body(...)):
    import yfinance as yf

    data = yf.download(symbol, period="2mo")["Close"]

    # Remove old records for this symbol
    cur.execute("DELETE FROM prices WHERE symbol=?", (symbol,))

    RESULT = []
    for date, close in data.items():
        day = date.strftime("%Y-%m-%d")
        cur.execute(
            "INSERT INTO prices(symbol, date, close) VALUES (?,?,?)",
            (symbol, day, float(close))
        )
        RESULT.append({"date": day, "close": float(close)})

    conn.commit()
    return {"ok": True, "rows": len(RESULT)}
