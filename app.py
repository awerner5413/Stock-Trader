# I need to figure out how to handle all of the things that cs50 built in for me withi helpers
# I believe that included the login validations, something to do with formatting USD, etc.
# TD List
# Add in the styles sheet from finance and adjust
# Get the layout html file the way I want so I can build off it
# see if we were using JS for anything in the finance project

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def launch_homepage():    
    return render_template("index.html")
