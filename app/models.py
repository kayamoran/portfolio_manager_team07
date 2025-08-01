import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float
from app.database import Base
from datetime import datetime

class WatchlistItem(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    price = Column(Float)
    change_percent = Column(Float)
    
class PortfolioItem(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    last_price = Column(Float)          # Latest market price
    quantity = Column(Integer)
    avg_purchase_price = Column(Float)  # Cost basis for the stock
    
class PortfolioStatus(Base):
    __tablename__ = "portfolio_status"

    id = Column(Integer, primary_key=True, index=True)
    cash_balance = Column(Float, default=1_000_000.0)
    
    
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    type = Column(String)  # 'buy' or 'sell'
    timestamp = Column(DateTime, default=datetime.now)    
    
   
