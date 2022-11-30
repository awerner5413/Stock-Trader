# -- TD List
# hide API token
# Hide secret key? see flask docs
# list suggestions for stocks to buy on buy page
# Make nav bar frozen
# find new timestamp format for history insert_tms
# ..
# Test API usage start of Dec and see if using the page twice adds up too much
# Use PythonAnywhere when it's time to release to production, they will host the server
# -- Features to add
# also under quoted, a chat section for people to discuss investments and more stock information or for people to leave notes to self? TWT CHAT APP, REPLICATE, SIDE BAR???

import datetime
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from authentication import get_cursor, get_db, lookup, require_login, usd, stock_news

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Custom filter
app.jinja_env.filters["usd"] = usd

@app.route("/", methods=["GET", "POST"])
@require_login
def launch_homepage():
    """Display logged-in user's stock portfolio"""
    # Update cash amount if user makes a deposit
    deposit_sql = "SELECT cash_total FROM users WHERE id = %s"
    if request.method == "POST":
        deposit_dollars = float(request.form.get("cash"))
        if deposit_dollars < 0:
            error = "You must enter a valid dollar amount."
            flash(error)
            return redirect("/")

        cursor = get_cursor()
        cursor.execute(deposit_sql, (session["user_id"],))
        user_info = cursor.fetchall()
        cash = user_info[0]["cash_total"]

        update_cash_sql = "UPDATE users SET cash_total = %s WHERE id = %s"
        cursor.execute(update_cash_sql, (cash + deposit_dollars, session["user_id"],))
        flash("Your funds have been successfully deposited!")
        return redirect("/")

    # Get the holdings table into a list
    else:
        cursor = get_cursor()
        portfolio_sql = "SELECT * FROM holdings WHERE id = %s"
        cursor.execute(portfolio_sql, (session["user_id"],))
        portfolio = cursor.fetchall()
        tickers = []
        ticker_totals = []
        print("LOOK HERE")
        print(portfolio)

        if not portfolio:
            flash("Please purchase your first stock.")
            return redirect("/buy")
        else:

        # Loop through each holding and get the price and total through lookup
            for i in portfolio:
                final = 0
                symbol = i["stock_symbol"]
                shares = i["shares_amt"]
                quote = lookup(symbol)
                amount = quote.get("price")

                # Calculate the value of the stock holding and update the current total value
                value = round(amount * shares, 2)
                final = final + value

                # Update the dictionary with the price and total amounts to be displayed
                i.append(amount)
                i.append(value)

                # Update lists to create pie chart
                tickers.append(symbol)
                ticker_totals.append(value)
            
            # Get the users current cash value and create a new variable to calculate total value
            cursor.execute(deposit_sql, (session["user_id"],))
            user_info = cursor.fetchall()
            cash = user_info[0]["cash_total"]
            final = final + cash
            
            # Create dataset to send to chart
            data = list(zip(tickers, ticker_totals))
            labels = [row[0] for row in data]
            values = [row[1] for row in data]

            return render_template("index.html", portfolio=portfolio, cash=cash, final=final, labels=labels, values=values)


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

        # Confirm variables meet criteria
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            error = "You must enter a username and a password."
        elif password != confirmation:
            error = "Your password and confirmation must match."

        # Confirm no duplicate usernames
        cursor = get_cursor()
        duplicate_user_sql = "SELECT * FROM users WHERE name = %s"
        cursor.execute(duplicate_user_sql, (username,))
        dup_check = cursor.fetchall()
        if len(dup_check) == 1:
            error = "That username already exists. Please try again with a different username."
            flash(error)
            return redirect("/register")

        # Setup SQL for db addition
        sql = "INSERT INTO users (secret, name, cash_total) VALUES (%s, %s, %s)"
        val = (hashed, username, 10000.00)
        
        # If registration successful, add to login table and send to login page
        if error is None:
            try:
                cursor.execute(sql, val)
            except db.IntegrityError:
                error = "Invalid username or password."
            flash(f"Welcome to StockTrader, {username}! As a thank you, we have given you $10,000 - please log in and start trading!")
            return render_template("login.html")

        flash(error)
        return redirect("/register")

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


# THIS IS TEMPORARY DUMMY DATA TO POPULATE QUOTED PAGE WHILE API DOWN
temp_dict = [{"image":"https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8bmV3c3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60", 
            "timestamp": "2022-11-26", "headline": "This is the headline for my news article", "source": "Benzinga", "url": "https://giphy.com/gifs/donald-trump-if-he-wins-the-white-house-will-become-pixilated-p0YA9SBLKo2ac",
            "summary": "lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah"},
            {"image":"https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8bmV3c3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60", 
            "timestamp": "2022-11-26", "headline": "This is the headline for my news article", "source": "Benzinga", "url": "https://giphy.com/gifs/donald-trump-if-he-wins-the-white-house-will-become-pixilated-p0YA9SBLKo2ac",
            "summary": "lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah"},
            {"image":"https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8bmV3c3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60", 
            "timestamp": "2022-11-26", "headline": "This is the headline for my news article", "source": "Benzinga", "url": "https://giphy.com/gifs/donald-trump-if-he-wins-the-white-house-will-become-pixilated-p0YA9SBLKo2ac",
            "summary": "lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah"},
            {"image":"https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8M3x8bmV3c3xlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60", 
            "timestamp": "2022-11-26", "headline": "This is the headline for my news article", "source": "Benzinga", "url": "https://giphy.com/gifs/donald-trump-if-he-wins-the-white-house-will-become-pixilated-p0YA9SBLKo2ac",
            "summary": "lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah lorem ipsum blah blah blah blah blah"}]

@app.route('/quote', methods=["GET", "POST"])
@require_login
def launch_quotes():
    if request.method == "POST":
        symbol = request.form.get("symbol")

        # try:
        #     quote = lookup(symbol)
        # except:
        #     error = "Please provide a valid ticker symbol."
        #     flash(error)
        #     return render_template("quote.html")
        
        # try:            
        #     news = stock_news(symbol)
        # except:
        #     error = "STOCK NEWS ISN'T WORKING"
        #     flash(error)
        #     return render_template("quote.html")
        # else:
            # Quote variables  - POSTPONED UNTIL MY API RESETS
            # symbol = quote.get("symbol")
            # name = quote.get("name")
            # price = quote.get("price")
        #ONCE READY TO PUBLISH I NEED TO FIX INDENTS TO GO UNDER THE ELSE OF TRY BLOCK
        name = "Random Company"
        price = 150.00

            # News variables - POSTPONED UNTIL MY API RESETS
            # ms = news.get("datetime") / 1000.0
            # timestamp = datetime.datetime.fromtimestamp(ms).strftime('%Y-%m-%d %H:%M:%S')
            # headline = news.get("headline")
            # source = news.get("source")
            # url = news.get("url")
            # summary = news.get("summary")
            # image = news.get("image")
        return render_template("quoted.html", symbol=symbol.upper(), name=name, price=price, temp_dict = temp_dict)
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
            return redirect("/buy")
        company_name = quote.get("name")
        stock_symbol = quote.get("symbol")

        # Validate the amount of shares is a useable number
        try:
            shares = int(request.form.get("shares"))
        except:
            error = "Enter a valid amount of shares."
            flash(error)
            return redirect("/buy")
        
        if shares < 0:
            error = "Enter a valid amount of shares."
            flash(error)
            return redirect("/buy")
        
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
            return redirect("/buy")
        
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
            flash("Your purchase was successful!")
            return redirect("/buy")

    else:
        buy_cash_sql = "SELECT cash_total FROM users WHERE id = %s"
        cursor = get_cursor()
        cursor.execute(buy_cash_sql, (session["user_id"],))
        user_info = cursor.fetchall()
        cash = user_info[0]["cash_total"]
        return render_template("buy.html", cash=cash)


@app.route("/sell", methods=["GET", "POST"])
@require_login
def sell():
    """Sell shares of owned stock and update holdings, transactions, and user cash totals."""
    cursor = get_cursor()

    # if sale attempted, get variables and perform validation
    if request.method == "POST":
        # Validate the amount of shares is a useable number
        try:
            shares = int(request.form.get("shares"))
        except:
            error = "Enter a valid amount of shares."
            flash(error)
            return render_template("sell.html")
        if shares < 0:
            error = "Enter a valid amount of shares."
            flash(error)
            return render_template("sell.html")        
        
        # Validate user has enough shares to cover sale and update holdings
        symbol = request.form.get("symbol")
        current_holdings_sql = "SELECT * FROM holdings WHERE id = %s AND stock_symbol = %s"
        cursor.execute(current_holdings_sql, (session["user_id"], symbol,))
        current_holdings = cursor.fetchall()
        username = current_holdings[0]["name"]
        current_shares = current_holdings[0]["shares_amt"]
        if shares > current_holdings[0]["shares_amt"]:
            error = f"You do not own enough shares to complete this transaction. You currently have {current_shares} share(s). Please update the amount and try again."
            flash(error)
            return redirect("/sell")

        # Delete stock from holdings if user sells all shares, else update shares amount
        if shares == current_holdings[0]["shares_amt"]:
            remove_holdings_sql = "DELETE FROM holdings WHERE stock_symbol = %s AND id = %s"
            cursor.execute(remove_holdings_sql, (symbol, session["user_id"],))
        else:
            update_holdings_sql = "UPDATE holdings SET shares_amt = %s WHERE stock_symbol = %s AND id = %s"
            cursor.execute(update_holdings_sql, (current_shares - shares, symbol, session["user_id"],))

        # Update users cash amount
        quote = lookup(symbol)
        price = quote.get("price")
        earnings = price * shares
        cash_pull_sql = "SELECT cash_total FROM users WHERE id = %s"
        cursor.execute(cash_pull_sql, (session["user_id"],))
        current_cash = cursor.fetchall()
        cash = current_cash[0]["cash_total"]

        cash_update_sql = "UPDATE users SET cash_total = %s WHERE id = %s"
        cursor.execute(cash_update_sql, (cash + earnings, session["user_id"],))

        # Update transactions
        sale_transaction_sql = "INSERT INTO transactions (id, name, transaction_type, transaction_amount, stock_symbol, shares_amt, insert_tms) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sale_transaction_sql, (session["user_id"], username, "Sell", earnings, symbol, shares, datetime.datetime.now(),))

        flash("Your transaction was successful!")
        return redirect("/sell")

    # Render sell template with stock options in dropdown
    else:        
        current_holdings_sql = "SELECT * FROM holdings WHERE id = %s"
        cursor.execute(current_holdings_sql, (session["user_id"],))
        current_holdings = cursor.fetchall() 
        stocks = []
        for row in current_holdings:
            x = row.get("stock_symbol")
            stocks.append(x)
        return render_template("sell.html", stocks=stocks)


@app.route("/history")
@require_login
def history():
    """Show history of all transactions"""
    cursor = get_cursor()
    transaction_sql = "SELECT transaction_id, id, name, transaction_type, transaction_amount, stock_symbol, shares_amt, insert_tms FROM transactions WHERE id = %s ORDER BY insert_tms DESC"
    cursor.execute(transaction_sql, (session["user_id"],))
    transactions = cursor.fetchall()
    return render_template("history.html", transactions=transactions)