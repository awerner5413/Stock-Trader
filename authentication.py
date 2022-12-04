import os
from functools import wraps
import psycopg2
import psycopg2.extras
import requests
from flask import redirect, session


def get_db():
    """Connect to the database and return the connection"""
    db_url = os.environ['DATABASE_URL']
    db = psycopg2.connect(db_url, sslmode='require')
    db.autocommit = True
    return db


def get_cursor():
    """Use the database connection to create a cursor to perform queries"""
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor


def require_login(func):
    """decorator to confirm the current user is logged in before accessing features of certain pages. Redirect to login if not"""
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if session.get("user_id") is None:            
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper_func


def lookup(symbol):
    """Contact the API to get stock price information of the ticker symbol submitted"""
    # Contact API
    token = os.environ['API_KEY']
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={token}"
    response = requests.get(url, timeout=1)
    quote = response.json()

    # Return quote information
    return {
        "name": quote["companyName"],
        "price": float(quote["latestPrice"]),
        "symbol": quote["symbol"]
    }


def stock_news(symbol):
    """Contact the API to get the most recent news article for the company of the ticker symbol submitted"""
    # Contact API
    token = os.environ['API_KEY']
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/1?token={token}"
    response = requests.get(url, timeout=1)
    news = response.json()
    print(news)

    # Return news information
    if not news:
        print("NOT IS WORKING")
        return {"summary": "No news available for this stock",
                "image": "https://static9.depositphotos.com/1431107/1135/i/600/depositphotos_11359051-stock-photo-sorry-emoticon.jpg"}
    else:
        return {
            "headline": news[0]["headline"],
            "source": news[0]["source"],
            "url": news[0]["url"],
            "summary": news[0]["summary"],
            "image": news[0]["image"]
        }

def usd(value):
    """Format values to a dollar amount using a Jinja filter"""
    return f"${value:,.2f}"