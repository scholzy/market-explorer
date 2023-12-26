#!/usr/bin/env python3

import os

from arcticdb import Arctic
from dotenv import load_dotenv
from flask import Flask

# Initialise the Flask app
app = Flask(__name__)

# And the fast tabular database (locally, for now)
db = Arctic("lmdb://./db")

# Load the environment variables if present
load_dotenv()


@app.route("/")
def index():
    db.create_library("stonks")
    return "Hello World!"


if __name__ == "__main__":
    DEBUG_MODE = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=DEBUG_MODE)
