# This is where I will handle my login checks and maybe some other stuff, like helper, but not just like it...
import psycopg2
from functools import wraps
from flask import session, redirect, request


def get_cursor():
    db = psycopg2.connect(database="test", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
    db.autocommit = True
    cursor = db.cursor()
    return cursor

def require_login(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper_func


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Get all variables from registration
    if request.method == "POST":
        # Get variables from registration form
        username = request.form.get("username")
        password = request.form.get("password")
        # confirmation = request.form.get("confirmation")

        # Setup SQL for db addition
        sql = "INSERT INTO login (secret, name) VALUES (%s, %s)"
        val = (username, password)

        # NEED TO FIGURE OUT HOW TO HANDLE ERRORS DIFFERENT THAN WHAT THEY DID - POP UP ON SCREEN?
        # Confirm variables meet criteria
        # if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
        #     return apology("must enter a username or password", 400)
        # elif password != confirmation:
        #     return apology("password and confirmation must match", 400)

        # Hash the password and add user to users - FIGURE OUT HOW TO HASH
        # else:
        #     # hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=len(password))
        #     try:
        #         db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        #     except ValueError as err: # FIGURE OUT HOW TO HANDLE ERROR HERE RATHER THAN RE-LOAD PAGE
        #         return render_template("register.html")
        #         # return apology("invalid username and/or password", 400)
        #     return render_template("login.html")
        
        try:
            print(username, password)
            cursor.execute(sql, val)
            db.commit()
        except ValueError as err: # FIGURE OUT HOW TO HANDLE ERROR HERE RATHER THAN RE-LOAD PAGE, or do but with flash message
            return render_template("register.html")            
        return render_template("login.html")


    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            error = "You must provider username."

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "You must provider password."

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")