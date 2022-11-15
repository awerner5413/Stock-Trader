# This is where I will handle my login checks and maybe some other stuff, like helper, but not just like it...
from functools import wraps

import psycopg2
import psycopg2.extras
from flask import redirect, session


def get_db():
    db = psycopg2.connect(database="test", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
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