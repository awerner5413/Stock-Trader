# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# -- TD List
# Build registration page, connect to DB, build index/homepage, setup security measures and add standing login check
# Figure out how to authenticate and use the login with werkzungaifenf (see finance-site and helpers)
# Will need to use Flask request feature to bring in API - documentation has a section
# User PythonAnywhere when it's time to release to production, they will host the server
# -- Features to add
# A script that scrapes a stock ticker for news and displays first 3 articles below
# Graph user cash total over time or per transaction

import psycopg2
from flask import Flask, render_template, request
from auth import require_login

app = Flask(__name__)

db = psycopg2.connect(database="test", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
db.autocommit = True
cursor = db.cursor()

@app.route('/')
def launch_homepage():

    # TESTING SQL
    # sql = "INSERT INTO users2 (name, age, birthday, score) VALUES (%s, %s, %s, %s)"
    # val = ("Ben", 31, '1990-12-26', 42)
    # cursor.execute(sql, val)
    # db.commit()
    # print(cursor.rowcount, "record inserted.")    

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
@require_login
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