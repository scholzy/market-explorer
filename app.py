#!/usr/bin/env python3

import os

from arcticdb import Arctic
import dash
import dash_mantine_components as dmc
from dotenv import load_dotenv
from flask import Flask, render_template

from app.backend.data_fetching import import_nasdaq_tickers
from app.common import DBLibraries, DBSymbols
from app.layout import layout

# Initialise the Flask app
app = Flask(__name__)

# And the fast tabular database (locally, for now)
db = Arctic("lmdb://./db")

# Make sure we've got somewhere to store exchange data
if DBLibraries.Exchanges.value not in db.list_libraries():
    db.create_library(DBLibraries.Exchanges.value)

# For now, we just use the NASDAQ exchange data. We load in serialised
# data from a downladed JSON file for now.
exchange_lib = db[DBLibraries.Exchanges.value]
if DBSymbols.NasdaqTickers.value not in exchange_lib.list_symbols():
    import_nasdaq_tickers("data/nasdaq.json", exchange_lib)

# Normally, we'd use SQLAlchemy to wrap the database connection
# and use the Flask connector to manage passing the connection. However,
# ArcticDB doesn't support SQLAlchemy, so we have to do it manually.


# Define the base route
@app.route("/")
def index():
    name = "Michael"
    return render_template("index.html", title="Market Explorer", name=name)


# Initialise the Dash app -- reusing the Flask server to host it
dash_app = dash.Dash(server=app, url_base_pathname="/dashboard/")  # type: ignore

# Wrap the layout in MantineProvider to provide global theming capability
dash_app.layout = dmc.MantineProvider(children=layout(db))

if __name__ == "__main__":
    # Load the environment variables if present
    load_dotenv()

    DEBUG_MODE = os.environ.get("FLASK_ENV") == "development"
    app.run(debug=DEBUG_MODE)
