# This is where I will handle my login checks and maybe some other stuff, like helper, but not just like it...
from functools import wraps
import psycopg2
import psycopg2.extras
import requests
from flask import redirect, session


def get_db():
    db = psycopg2.connect(database="stocktrader", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
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
    api_key = "pk_8660e47a2c9f4e248e52d17122c75714"
    url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={api_key}"
    response = requests.get(url, timeout=1)
    quote = response.json()

    # Return quote information
    return {
        "name": quote["companyName"],
        "price": float(quote["latestPrice"]),
        "symbol": quote["symbol"]
    }


def usd(value):
    return f"${value:,.2f}"