from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://investi-frontend-ayew.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"ok": True}

@app.post("/ingest/prices")
def ingest_prices(symbol: str = "SPY"):
    data = yf.download(symbol, period="6mo", interval="1d")
    if data.empty:
        return {"error": "No data"}
    output = [
        {"date": str(idx.date()), "close": float(row["Close"])}
        for idx, row in data.iterrows()
    ]
    return output

@app.get("/prices")
def get_prices(symbol: str = "SPY"):
    data = yf.download(symbol, period="6mo", interval="1d")
    output = [
        {"date": str(idx.date()), "close": float(row["Close"])}
        for idx, row in data.iterrows()
    ]
    return output
