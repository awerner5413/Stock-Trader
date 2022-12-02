import psycopg2
import psycopg2.extras
import requests
import os
from dotenv import load_dotenv
from flask import redirect, session
from functools import wraps


def configure():
    load_dotenv()

def get_db():
    db_url = os.environ['DATABASE_URL']
    db = psycopg2.connect(db_url, sslmode='require')
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
    token = os.environ['API_KEY']
    print(token)
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
    # Contact API
    token = os.environ['API_KEY']
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/news/last/1?token={token}"
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