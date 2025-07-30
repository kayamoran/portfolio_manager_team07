from sqlalchemy import Column, Integer, String, Float
from app.database import Base

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
    value = Column(Float)               # last_price * quantity
    total_gain = Column(Float)
    todays_gain = Column(Float)
    total_gain_percent = Column(Float)
    todays_gain_percent = Column(Float)
