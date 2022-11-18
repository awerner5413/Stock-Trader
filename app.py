# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# -- TD List
# Build buy page
# Build homepage to show holdings
# Build sell page and functions
# Build hisotry page and functions
# Test to see if database session ends without a close() call
# ..
# User PythonAnywhere when it's time to release to production, they will host the server
# -- Features to add
# Have the quote information show up on the quote page that still has the search bar so you don't need to go back to search for a new quote
# A script that scrapes a stock ticker for news and displays first 3 articles below
# Graph user cash total over time or per transaction

import datetime
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from authentication import get_cursor, get_db, lookup, require_login, usd

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
        # Get variables from registration form and hash password
        username = request.form.get("username")
        password = request.form.get("password")
        hashed = generate_password_hash(password, method='pbkdf2:sha256', salt_length=len(password))
        confirmation = request.form.get("confirmation")
        error = None

        # Setup SQL for db addition
        db = get_db()
        cursor = get_cursor()
        sql = "INSERT INTO users (secret, name) VALUES (%s, %s)"
        val = (hashed, username)

        # Confirm variables meet criteria
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            error = "You must enter a username and a password."
        elif password != confirmation:
            error = "Your password and confirmation must match."

        # If registration successful, add to login table and send to login page
        if error is None:            
            try:
                cursor.execute(sql, val)
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
        sql = "SELECT * FROM users WHERE name = %s"
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
            error = "Invalid username."
        elif not check_password_hash(rows[0]["secret"], password):
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

        try:
            quote = lookup(symbol)
        except:
            error = "Please provide a valid ticker symbol."
            flash(error)
            return render_template("quote.html")
        else:
            symbol = quote.get("symbol")
            name = quote.get("name")
            price = quote.get("price")
            return render_template("quoted.html", symbol=symbol, name=name, price=price)
    
    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@require_login
def buy():
    if request.method == "POST":
        error = None
        symbol = request.form.get("symbol")

        # Get quote information and validate the symbol is useable
        try:
            quote = lookup(symbol)
        except:
            error = "Please provide a valid ticker symbol."
            flash(error)
            return render_template("buy.html")        
        company_name = quote.get("name")
        stock_symbol = quote.get("symbol")

        # MAKE SURE THIS ERROR IS HANDLED - TRY WITHOUT THIS AND SEE IF TRY/EXCEPT HANDLES BLANK, IF SO UPDATE QUOTE
        # if quote is None:
        #     error = "Invalid ticker symbol"


        # Validate the amount of shares is a useable number
        try:
            shares = int(request.form.get("shares"))
        except:
            error = "Enter a valid amount of shares."
            flash(error)
            return render_template("buy.html")
        
        if shares < 0:
            error = "Enter a valid amount of shares."
            flash(error)
            return render_template("buy.html")
        
        # Prepare database connection to save transaction
        cursor = get_cursor()
        cash_sql = "SELECT * FROM users WHERE id = %s"
        cursor.execute(cash_sql, (session["user_id"],))
        user = cursor.fetchall()             
        
        # Get user info and confirm user has enough cash for purchase
        cash = user[0]["cash_total"]
        username = user[0]["name"]
        price = quote.get("price") * shares
        if price > cash:
            error = "You do not have enough funds to make this purchase."
            flash(error)
            return render_template("buy.html")
        
        else:
            # Add purchase to transactions table
            transaction_sql = "INSERT INTO transactions (id, name, transaction_type, transaction_amount, stock_symbol, shares_amt, insert_tms) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(transaction_sql, (session["user_id"], username, "Buy", price, stock_symbol, shares, datetime.datetime.now(),))
            
            # Update user cash amount
            update_sql = "UPDATE users SET cash_total = %s WHERE id = %s"
            cursor.execute(update_sql, (cash - price, session["user_id"],))

            # Check if stock already owned, either add or update to holdings table
            holdings_check_sql = "SELECT stock_symbol FROM holdings WHERE id = %s AND stock_symbol = %s"
            cursor.execute(holdings_check_sql, (session["user_id"], stock_symbol,))
            holdings = cursor.fetchall()
            if len(holdings) != 1:
                add_holdings_sql = "INSERT INTO holdings (id, name, stock_symbol, company, shares_amt) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(add_holdings_sql, (session["user_id"], username, stock_symbol, company_name, shares,))
            else:
                amount_check_sql = "SELECT shares_amt FROM holdings WHERE id = %s AND stock_symbol = %s"
                cursor.execute(amount_check_sql, (session["user_id"], stock_symbol,))
                amount_check = cursor.fetchall()                
                amount = int(amount_check[0]["shares_amt"])
                shares_update_sql = "UPDATE holdings SET shares_amt = %s WHERE id = %s AND stock_symbol = %s"
                cursor.execute(shares_update_sql, (shares + amount, session["user_id"], stock_symbol,))
            return redirect("/")

    else:
        return render_template("buy.html")