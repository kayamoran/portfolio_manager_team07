from fastapi import APIRouter
from app.crud.portfolio import add_to_portfolio, get_portfolio
from app.database import get_db
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import yfinance as yf





from app.crud.watchlist import get_watchlist
from app.models import PortfolioItem, PortfolioStatus, Transaction
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

    if current_price is None:
        raise HTTPException(status_code=400, detail="Price unavailable.")

    # Calculate total cost
    total_cost = current_price * quantity

    # Fetch current cash status
    status = db.query(PortfolioStatus).first()
    if not status:
        raise HTTPException(status_code=500, detail="Portfolio status not initialized.")

    if status.cash_balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient funds to complete purchase.")

    existing = db.query(PortfolioItem).filter_by(symbol=symbol).first()

    if existing:
        # Update average purchase price
        total_quantity = existing.quantity + quantity
        total_invested = (existing.avg_purchase_price * existing.quantity) + total_cost
        existing.avg_purchase_price = total_invested / total_quantity
        existing.quantity = total_quantity
        existing.last_price = current_price
    else:
        new_item = PortfolioItem(
            symbol=symbol,
            name=name,
            last_price=current_price,
            quantity=quantity,
            avg_purchase_price=current_price
        )
        db.add(new_item)

    # Deduct cash
    status.cash_balance -= total_cost
    transaction = Transaction(
    symbol=symbol,
    name=name,
    quantity=quantity,
    price=current_price,
    type="buy")
    db.add(transaction)


    db.commit()

    return existing if existing else new_item
   
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

    # Get the current market price
    try:
        data = yf.Ticker(symbol).info
        current_price = data.get("regularMarketPrice")
        if current_price is None:
            raise ValueError
        item.last_price = current_price  # update last_price if needed
    except:
        raise HTTPException(status_code=400, detail="Could not fetch current market price.")

    # Calculate revenue
    revenue = current_price * quantity

    # Update quantity
    item.quantity -= quantity

    # Update cash balance
    status = db.query(PortfolioStatus).first()
    if not status:
        raise HTTPException(status_code=500, detail="Portfolio status not initialized.")
    status.cash_balance += revenue

    if item.quantity == 0:
        db.delete(item)
        
    transaction = Transaction(
    symbol=symbol,
    name=item.name,
    quantity=quantity,
    price=current_price,
    type="sell")
    db.add(transaction)

    db.commit()

    return {
        "message": f"Sold {quantity} shares of {symbol} for ${revenue:.2f}",
        "cash_balance": status.cash_balance
    }


@router.get("/cash")
def get_cash_balance(db: Session = Depends(get_db)):
    status = db.query(PortfolioStatus).first()
    
    if not status:
        # Auto-initialize if missing
        status = PortfolioStatus(cash_balance=1_000_000.0)
        db.add(status)
        db.commit()
        db.refresh(status)
    return {"cash_balance": status.cash_balance}


@router.get("/transactions")
def get_transaction_history(db: Session = Depends(get_db)):
    history = db.query(Transaction).order_by(Transaction.timestamp.desc()).all()
    return [
        {
            "symbol": t.symbol,
            "name": t.name,
            "quantity": t.quantity,
            "price": t.price,
            "type": t.type,
            "timestamp": t.timestamp
        }
        for t in history
    ]