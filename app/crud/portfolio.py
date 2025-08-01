from sqlalchemy.orm import Session
from app.models import PortfolioItem

def add_to_portfolio(db: Session, item: PortfolioItem):
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def get_portfolio_data(db: Session, table_name):
    return db.query(table_name).all()

def delete_from_portfolio(db: Session, id: int):
    item = db.query(PortfolioItem).filter_by(id=id).first()
    if item:
        db.delete(item)
        db.commit()
        return True
    return False
