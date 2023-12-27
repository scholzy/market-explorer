#!/usr/bin/env python3

import os

from arcticdb import Arctic
import dash
from dotenv import load_dotenv
from flask import Flask

from app.layout import layout

# Initialise the Flask app
app = Flask(__name__)

# And the fast tabular database (locally, for now)
db = Arctic("lmdb://./db")

# Load the environment variables if present
load_dotenv()


# Define the base route
@app.route("/")
def index():
    db.create_library("stonks")
    return "Hello World!"


# Initialise the Dash app -- reusing the Flask server to host it
dash_app = dash.Dash(server=app, url_base_pathname="/dashboard/")  # type: ignore
dash_app.layout = layout()

if __name__ == "__main__":
    DEBUG_MODE = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=DEBUG_MODE)
