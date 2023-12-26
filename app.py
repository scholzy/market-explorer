#!/usr/bin/env python3

from arcticdb import Arctic
from flask import Flask

app = Flask(__name__)

db = Arctic("lmdb://./db")

@app.route('/')
def index():
    db.create_library('stonks')
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
