from fastapi import FastAPI
from app.database import engine
from app.models import Base
from app.routes import portfolio, search, watchlist
from app.models import WatchlistItem, PortfolioItem


#uvicorn app.main:app --reload

app = FastAPI(
    title="Portfolio Management API",
    version="1.0.0",
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["Watchlist"])
app.include_router(search.router, prefix="/api/search", tags=["Search"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])

