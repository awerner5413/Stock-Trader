import psycopg2
import psycopg2.extras
import requests
import config
import datetime
from flask import redirect, session
from functools import wraps


def get_db():
    db_password = config.db_password
    db = psycopg2.connect(database="stocktrader", user='postgres', password=db_password, host='127.0.0.1', port='5432')
    db.autocommit = True
    return db


def get_cursor():
    db = get_db()
    cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor


def require_login(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper_func


def lookup(symbol):
    # Contact API
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={config.api_key}"
    response = requests.get(url, timeout=1)
    quote = response.json()

    # Return quote information
    return {
        "name": quote["companyName"],
        "price": float(quote["latestPrice"]),
        "symbol": quote["symbol"]
    }


def stock_news(symbol):
    # Contact API
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/1?token={config.api_key}"
    response = requests.get(url, timeout=1)
    news = response.json()

    # Return news information
    return {
        "headline": news[0]["headline"],
        "source": news[0]["source"],
        "url": news[0]["url"],
        "summary": news[0]["summary"],
        "image": news[0]["image"]
    }

def usd(value):
    return f"${value:,.2f}"