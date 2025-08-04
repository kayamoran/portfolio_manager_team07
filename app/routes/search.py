# app/routes/search.py
import yfinance as yf
from fastapi import APIRouter, HTTPException

router = APIRouter()

def human_readable_number(num):
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(num) < 1000:
            return f"{num:.2f}{unit}"
        num /= 1000
    return f"{num:.2f}T"

@router.get("/{symbol}")
def search_stock(symbol: str):
    stock = yf.Ticker(symbol)
    info = stock.info

    if not info or "regularMarketPrice" not in info:
        raise HTTPException(status_code=404, detail="Stock not found")

    return {
        "symbol": symbol.upper(),
        "name": info.get("shortName", "N/A"),
        "price": f"${(info.get("regularMarketPrice"))}",
        "change_percent": f"{info.get("regularMarketChangePercent"):.2f}%",
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
        "market_cap": human_readable_number(info.get("marketCap")),
        "trading_volume": human_readable_number(info.get("volume")),
    }
