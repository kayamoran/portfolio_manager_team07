import yfinance as yf
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import WatchlistItem
from app.crud.watchlist import add_watchlist, get_watchlist, remove_from_watchlist
from app.database import get_db

router = APIRouter()

@router.post("/add/{symbol}")
def add_to_watchlist(symbol: str, db: Session = Depends(get_db)):
    data = yf.Ticker(symbol).info
    if not data.get("regularMarketPrice"):
        raise HTTPException(status_code=404, detail="Stock not found")
    if symbol.upper() in [item.symbol for item in get_watchlist(db)]:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")
    item = WatchlistItem(
        symbol=symbol.upper(),
        name=data.get("shortName", "N/A"),
        price=data.get("regularMarketPrice"),
        change_percent=data.get("regularMarketChangePercent", 0),
    )
    return add_watchlist(db, item)

@router.get("/display")
def get_watchlist_list(db: Session = Depends(get_db)):
    return get_watchlist(db)

@router.delete("/delete/{symbol}")
def delete_stock(symbol: str, db: Session = Depends(get_db)):
    if remove_from_watchlist(db, symbol.upper()):
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Stock not in watchlist")
