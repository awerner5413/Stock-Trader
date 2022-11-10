# This is where I will handle my login checks and maybe some other stuff, like helper, but not just like it...
from functools import wraps
from flask import session, redirect


def require_login(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper_func