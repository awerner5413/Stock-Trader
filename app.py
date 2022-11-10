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

from flask import Flask, render_template
from authentication import require_login, get_cursor

app = Flask(__name__)


@app.route('/')
@require_login
def launch_homepage():

    # TESTING SQL
    # sql = "INSERT INTO users2 (name, age, birthday, score) VALUES (%s, %s, %s, %s)"
    # val = ("Ben", 31, '1990-12-26', 42)
    # cursor.execute(sql, val)
    # db.commit()
    # print(cursor.rowcount, "record inserted.")    

    return render_template("index.html")