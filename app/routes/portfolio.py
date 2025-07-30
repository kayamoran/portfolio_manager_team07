from fastapi import APIRouter
from app.crud.portfolio import get_portfolio
from app.database import get_db
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import yfinance as yf





from app.crud.watchlist import get_watchlist
from app.models import PortfolioItem

router = APIRouter()

@router.get("/displayStocks")
def read_portfolio(db: Session = Depends(get_db)):
    portfolio = get_portfolio(db)
    return portfolio

#buy stocks
@router.post("/buy")
def buy_stock(symbol: str, amount: float, db: Session = Depends(get_db)):
    symbol = symbol.upper()
    stock = yf.Ticker(symbol)
    info = stock.info

    price = info.get("regularMarketPrice")
    name = info.get("shortName", "N/A")

    if not price:
        raise HTTPException(status_code=404, detail="Stock not found")

    quantity_to_buy = amount / price

    # Check if already in portfolio
    existing = db.query(PortfolioItem).filter_by(symbol=symbol).first()

    if existing:
        existing.quantity += quantity_to_buy
        existing.last_price = price
        existing.value = existing.quantity * price
        
    else:
        new_item = PortfolioItem(
            symbol=symbol,
            name=name,
            last_price=price,
            quantity=quantity_to_buy,
            value=quantity_to_buy * price,
            total_gain=0,
            todays_gain=0,
            total_gain_percent=0,
            todays_gain_percent=0,
        )
        db.add(new_item)

    db.commit()
    return {"message": "Stock purchased", "symbol": symbol, "quantity": quantity_to_buy, "price": price}
#sell stocks
