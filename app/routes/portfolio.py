from fastapi import APIRouter
from app.crud.portfolio import add_to_portfolio, get_portfolio
from app.database import get_db
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import yfinance as yf





from app.crud.watchlist import get_watchlist
from app.models import PortfolioItem
from app.routes.search import human_readable_number

router = APIRouter()

@router.get("/displayStocks")
def display_stocks(db: Session = Depends(get_db)):
    items = db.query(PortfolioItem).all()
    portfolio = []

    for item in items:
        data = yf.Ticker(item.symbol).info
        market_value = item.last_price * item.quantity
        total_gain_amount = (item.last_price - item.avg_purchase_price) * item.quantity
        total_gain_percent = ((item.last_price - item.avg_purchase_price) / item.avg_purchase_price) * 100 if item.avg_purchase_price else 0

        portfolio.append({
            "symbol": item.symbol,
            "name": item.name,
            "last_price": f"${item.last_price:.2f}",
            "quantity": item.quantity,
            "purchase_price": f"${item.avg_purchase_price:.2f}",
            "market_value": f"${market_value:.2f}",
            "total_gain_amount": f"${total_gain_amount:.2f}",
            "total_gain_percent": f"{total_gain_percent:.2f}%",
            "market_cap": human_readable_number(data.get("marketCap", "N/A")),
            "volume": human_readable_number(data.get("volume", "N/A")),
        })

    return portfolio

#buy stocks
@router.post("/buy")
def buy_stock(symbol: str, quantity: int, db: Session = Depends(get_db)):
    try:
        data = yf.Ticker(symbol).info
        name = data.get("shortName", symbol)
        current_price = data["regularMarketPrice"]
    except Exception:
        raise HTTPException(status_code=404, detail="Stock not found or API error.")

    existing = db.query(PortfolioItem).filter_by(symbol=symbol).first()

    if existing:
        total_quantity = existing.quantity + quantity
        total_cost = (existing.avg_purchase_price * existing.quantity) + (current_price * quantity)
        existing.avg_purchase_price = total_cost / total_quantity
        existing.quantity = total_quantity
        existing.last_price = current_price
        db.commit()
        db.refresh(existing)
        return existing
    else:
        new_item = PortfolioItem(
            symbol=symbol,
            name=name,
            last_price=current_price,
            quantity=quantity,
            avg_purchase_price=current_price
        )
        return add_to_portfolio(db, new_item)
    #return {"message": "Stock purchased", "symbol": symbol, "quantity": quantity_to_buy, "price": price}
#sell stocks
@router.post("/sell")
def sell_stock(symbol: str, quantity: int, db: Session = Depends(get_db)):
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than zero.")

    item = db.query(PortfolioItem).filter_by(symbol=symbol).first()

    if not item:
        raise HTTPException(status_code=404, detail="Stock not found in portfolio.")

    if quantity > item.quantity:
        raise HTTPException(status_code=400, detail="Not enough quantity to sell.")

    item.quantity -= quantity

    if item.quantity == 0:
        db.delete(item)
        db.commit()
        return {"message": f"Sold all shares of {symbol}. Stock removed from portfolio."}
    else:
        # Optionally update last_price from market
        try:
            current_price = yf.Ticker(symbol).info["regularMarketPrice"]
            item.last_price = current_price
        except:
            pass  # Keep existing last_price if API fails

        db.commit()
        db.refresh(item)
        return item
