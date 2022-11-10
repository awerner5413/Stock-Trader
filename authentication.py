# This is where I will handle my login checks and maybe some other stuff, like helper, but not just like it...
import psycopg2
from functools import wraps
from flask import session, redirect #, request, render_template, flash
# from werkzeug.security import check_password_hash, generate_password_hash


def get_db():
    db = psycopg2.connect(database="test", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
    db.autocommit = True
    return db

def get_cursor():    
    db = get_db()
    cursor = db.cursor()
    return cursor

def require_login(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper_func


# @app.route("/register", methods=["GET", "POST"])
# def register():

#     # Get all variables from registration
#     if request.method == "POST":
#         # Get variables from registration form
#         username = request.form.get("username")
#         password = request.form.get("password")
#         hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=len(password))
#         confirmation = request.form.get("confirmation")
#         error = None

#         # Setup SQL for db addition
#         db = get_db()
#         cursor = get_cursor()
#         sql = "INSERT INTO login (secret, name) VALUES (%s, %s)"
#         val = (hash, username)
        
#         # Confirm variables meet criteria
#         if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
#             error = "You must enter a username and a password."
#         elif password != confirmation:
#             error = "Your password and confirmation must match."

#         # Hash the password and add user to users - FIGURE OUT HOW TO HASH
#         if error is None:            
#             try:
#                 cursor.execute(sql, val)
#                 db.commit()
#             except db.IntegrityError:
#                 error = "Invalid username or password."
#             return render_template("login.html")
        
#         flash(error)

#     else:
#         return render_template("register.html")


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     # Forget any user_id
#     session.clear()
    
#     if request.method == "POST":
#         error = None
#         cursor = get_cursor()        
#         sql = "SELECT * FROM users WHERE username = %s"
#         un = request.form.get("username")

#         # Ensure username was submitted
#         if not request.form.get("username"):
#             error = "You must provider username."

#         # Ensure password was submitted
#         elif not request.form.get("password"):
#             error = "You must provider password."

#         # Query database for username
#         rows = cursor.execute(sql, un)

#         # Ensure username exists and password is correct
#         if len(rows) != 1 or not check_password_hash(rows[0]["secret"], request.form.get("password")):
#             error = "Invalid password."
#         elif rows[0]["name"] != request.form.get("username"):
#             error = "Invalid username."

#         # Remember which user has logged in
#         else:
#             session["user_id"] = rows[0]["id"]

#         # Redirect user to home page
#             return redirect("/")

#         flash(error)

#     # User reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("login.html")