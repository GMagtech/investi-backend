from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime
import uvicorn

app = FastAPI(title="Investi Personnel Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB = "db.sqlite"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.on_event("startup")
def startup():
    conn = db(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS alerts(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      created_at TEXT, level TEXT, message TEXT, source TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS prices(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT, symbol TEXT, close REAL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS econ(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      date TEXT, series_id TEXT, value REAL
    )""")
    conn.commit(); conn.close()

@app.get("/alerts")
def get_alerts():
    conn = db()
    rows = [dict(x) for x in conn.execute("SELECT * FROM alerts ORDER BY id DESC LIMIT 200")]
    conn.close()
    return rows

@app.post("/alerts")
def add_alert(level: str, message: str, source: str):
    conn = db()
    conn.execute(
        "INSERT INTO alerts(created_at,level,message,source) VALUES (?,?,?,?)",
        (datetime.utcnow().isoformat(timespec="seconds"), level, message, source)
    )
    conn.commit(); conn.close()
    return {"ok": True}

@app.post("/ingest/prices")
def ingest_prices(symbol: str = "SPY"):
    conn = db()
    conn.execute("DELETE FROM prices WHERE symbol=?", (symbol,))
    base = 400.0
    for i in range(1, 11):
        conn.execute(
            "INSERT INTO prices(date,symbol,close) VALUES (?,?,?)",
            (f"2025-01-{i:02d}", symbol, base + i)
        )
    conn.commit(); conn.close()
    return {"ok": True}

@app.get("/prices")
def prices(symbol: str = "SPY"):
    conn = db()
    rows = [dict(x) for x in conn.execute(
        "SELECT date, close FROM prices WHERE symbol=? ORDER BY date", (symbol,)
    )]
    conn.close()
    return rows

@app.post("/ingest/econ")
def ingest_econ(series_id: str = "FEDFUNDS"):
    conn = db()
    conn.execute("DELETE FROM econ WHERE series_id=?", (series_id,))
    vals = [5.00, 5.00, 5.25, 5.25, 5.00, 4.75, 4.75, 4.50, 4.50, 4.25]
    for i, v in enumerate(vals, start=1):
        conn.execute("INSERT INTO econ(date,series_id,value) VALUES (?,?,?)",
                     (f"2025-01-{i:02d}", series_id, v))
    conn.commit(); conn.close()
    return {"ok": True}

@app.get("/econ")
def econ(series_id: str = "FEDFUNDS"):
    conn = db()
    rows = [dict(x) for x in conn.execute(
        "SELECT date, value FROM econ WHERE series_id=? ORDER BY date", (series_id,)
    )]
    conn.close()
    return rows

@app.get("/impact")
def impact(symbol: str = "SPY", text: str = "", days_after: int = 5):
    return {
        "avg_forward_return": 0.0132,
        "std": 0.0027,
        "n": 84,
        "similar": [
            {"type":"Fed", "when":"2024-11-05", "excerpt":"Powell signale un resserrement"},
            {"type":"Inflation", "when":"2023-03-12", "excerpt":"Indice au-dessus des attentes"}
        ]
    }

@app.get("/impact_sector")
def impact_sector(symbol: str = "SPY", days_after: int = 5):
    return {"sector": "Énergie", "avg_forward_return": 0.0144, "std": 0.0017, "n": 42}

@app.get("/impact_sector_matrix")
def impact_sector_matrix(days_after: int = 5):
    return {
        "technologie": -0.0011,
        "energie": 0.0144,
        "sante": 0.0023,
        "finance": 0.0052
    }

@app.post("/ingest/news")
def ingest_news(): return {"ok": True}

@app.get("/news")
def news(limit: int = 12):
    items = [
        {"title":"Fed hints restrictive stance", "summary":"Caution likely to remain."},
        {"title":"ECB considers hikes", "summary":"Inflation above target."},
        {"title":"OPEC mulls output cut", "summary":"Adjusting supply."}
    ]
    return items[:limit]

@app.post("/ingest/weather")
def ingest_weather(): return {"ok": True}

@app.get("/weather")
def get_weather(limit: int = 7): return [{"day": i, "risk":"low"} for i in range(limit)]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
