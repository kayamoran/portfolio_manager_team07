import os
import requests
import yfinance as yf
from fastapi import APIRouter, HTTPException

print("API KEY:", os.getenv("API_KEY"))
router = APIRouter()


@router.get("/get/{symbol}")
def get_news(symbol: str):
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="News API key not configured")

    try:
        query = symbol or "AAPL"
        url = f"https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&language=en&apiKey={api_key}"

        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Return only the first 10 articles
        return {"articles": data.get("articles", [])[:10]}
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error fetching news: {e}")
