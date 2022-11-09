# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# TD List
# Figure out how to authenticate and use the login with werkzungaifenf (see finance-site and helpers)
# Figure out how to use Postgresql and add a database for the login (finish backend section on ZtM)
# Will need to use Flask request feature to bring in API - documentation has a section
# User PythonAnywhere when it's time to release to production, they will host the server
# Features to add
# A script that scrapes a stock ticker for news and displays first 3 articles below
# Graph user cash total over time or per transaction

import psycopg2
from flask import Flask, render_template

app = Flask(__name__)

db = psycopg2.connect( database="test", user='postgres', password='Atg112523!', host='127.0.0.1', port='5432')
db.autocommit = True
cursor = db.cursor()

@app.route('/')
def launch_homepage():

    # TESTING SQL
    sql = "INSERT INTO users2 (name, age, birthday, score) VALUES (%s, %s, %s, %s)"
    val = ("Ben", 31, '1990-12-26', 42)
    cursor.execute(sql, val)
    db.commit()
    print(cursor.rowcount, "record inserted.")    

    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():    
    return render_template("login.html")