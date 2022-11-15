# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# -- TD List
# Build quote page
# Will need to use Flask request feature to bring in API - documentation has a section
# See what else I can bring in with API that might be easy (hard stuff can wait for features)
# ..
# Clean up DB with better tables and new password and re-establish all code connections
# User PythonAnywhere when it's time to release to production, they will host the server
# -- Features to add
# A script that scrapes a stock ticker for news and displays first 3 articles below
# Graph user cash total over time or per transaction

from flask import Flask, render_template, request, flash, session, redirect
from authentication import get_db, get_cursor, require_login, lookup, usd
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Custom filter
app.jinja_env.filters["usd"] = usd

@app.route('/', methods=["GET", "POST"])
@require_login
def launch_homepage():
    return render_template("index.html")    


@app.route("/register", methods=["GET", "POST"])
def register():

    # Get all variables from registration
    if request.method == "POST":
        # Get variables from registration form
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=len(password))
        confirmation = request.form.get("confirmation")
        error = None

        # Setup SQL for db addition
        db = get_db()
        cursor = get_cursor()
        sql = "INSERT INTO login (secret, name) VALUES (%s, %s)"
        val = (hashed, username)
        
        # Confirm variables meet criteria
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            error = "You must enter a username and a password."
        elif password != confirmation:
            error = "Your password and confirmation must match."

        # Hash the password and add user to users - FIGURE OUT HOW TO HASH
        if error is None:            
            try:
                cursor.execute(sql, val)
                db.commit()
            except db.IntegrityError:
                error = "Invalid username or password."
            return render_template("login.html")
        
        flash(error)

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        error = None
        cursor = get_cursor()
        sql = "SELECT * FROM login WHERE name = %s"
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username and password was submitted
        if not username or not password:
            error = "You must provider a username and a password."
            flash(error)
            return render_template("login.html")
    
        # Query database for username
        cursor.execute(sql, (username,))
        rows = cursor.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1:
            print("NAME")
            error = "Invalid username."            
        elif not check_password_hash(rows[0]["secret"], password):
            print("PASS")
            error = "Invalid password."                   

        # Remember which user has logged in and re-direct to home page
        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/")

        # If unsuccessful login, reload login and flash error message
        flash(error)
        return render_template("login.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route('/quote', methods=["GET", "POST"])
@require_login
def launch_quotes():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quote = lookup(symbol)
        if quote == None:
            error = "Invalid ticker symbol" 
        else:
            symbol = quote.get("symbol")
            name = quote.get("name")
            price = quote.get("price")
            return render_template("quoted.html", symbol=symbol, name=name, price=price)
    
        # Re-load page with error message if search was incorrect - can I add more specific errors/messages?
        flash(error)
        return render_template("quote.html")    
    
    else:
        return render_template("quote.html")