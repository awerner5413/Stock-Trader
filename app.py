# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# TD List
# see if we were using JS for anything in the finance project
# Figure out how to authenticate and use the login with werkzungaifenf (see finance-site and helpers)
# Figure out how to use Postgresql and add a database for the login


from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def launch_homepage():    
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():    
    return render_template("login.html")