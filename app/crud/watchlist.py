from sqlalchemy.orm import Session
from app.models import WatchlistItem


#create
def add_watchlist(db: Session, item: WatchlistItem):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

#get
def get_watchlist(db: Session):
    return db.query(WatchlistItem).all()


#delete
def remove_from_watchlist(db: Session, symbol: str):
    item = db.query(WatchlistItem).filter_by(symbol=symbol).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
