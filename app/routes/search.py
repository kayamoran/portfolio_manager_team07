# app/routes/search.py
import yfinance as yf
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/{symbol}")
def search_stock(symbol: str):
    stock = yf.Ticker(symbol)
    info = stock.info

    if not info or "regularMarketPrice" not in info:
        raise HTTPException(status_code=404, detail="Stock not found")

    return {
        "symbol": symbol.upper(),
        "name": info.get("shortName", "N/A"),
        "price": info.get("regularMarketPrice"),
        "change_percent": info.get("regularMarketChangePercent"),
        "currency": info.get("currency"),
        "exchange": info.get("exchange"),
    }
