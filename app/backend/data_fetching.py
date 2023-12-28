import datetime
import json
from typing import Union

from arcticdb.version_store.library import Library
import pandas as pd
import yfinance as yf

from app import DBLibraries, DBSymbols

_START_DATE = "2000-01-01"


def import_nasdaq_tickers(filepath: str, library: Library) -> None:
    """Imports the NASDAQ tickers from the given file path into the given Arctic library.

    Args:
        filepath (str): The file path to the NASDAQ tickers JSON file.
        library (Library): The Arctic library to import the tickers into.

    Returns:
        dict[str, str]: A dictionary of the tickers and their names.
    """
    with open(filepath, "r") as f:
        nasdaq_data = json.load(f)

    # The JSON schema is something like:
    # {
    #    "data": {
    #       "headers": {
    #           "symbol": "Symbol",
    #           "name": "Name",
    #           ...
    #       },
    #       "rows": [
    #           {
    #               "symbol": "A",
    #               "name": "Agilent Technologies Inc.",
    #               ...
    #           },
    #           ...
    #       ]
    #    }
    # }

    headers = nasdaq_data["data"]["headers"]
    indices = nasdaq_data["data"]["rows"]
    data = {header: [index[header] for index in indices] for header in headers}

    df = pd.DataFrame(data)
    library.write(DBSymbols.NasdaqTickers.value, df)


def get_nasdaq_ticker_names(library: Library) -> pd.DataFrame:
    """Returns a DataFrame of the NASDAQ ticker names.

    Args:
        library (Library): The Arctic library to read the data from.
    """
    return library.read(DBSymbols.NasdaqTickers.value).data[["symbol", "name"]]


def fetch_or_download_data(tickers: list[str], library: Library) -> list[pd.DataFrame]:
    if not tickers:
        return []

    for ticker in tickers:
        if not library.has_symbol(ticker):
            data = download_data([ticker])
            library.write(ticker, data)

    return [library.read(ticker).data for ticker in tickers]

def download_data(
    tickers: list[str], start_date: Union[str, datetime.datetime] = _START_DATE
):
    """Downloads the historical data for the given list of ticker symbols.

    Args:
        tickers (list[str]): List of ticker symbols for the stocks.
        period (str, optional): The period of time to download the data for. Defaults to "1mo".
    """
    request_string = tickers[0] if len(tickers) == 1 else " ".join(tickers)
    return yf.download(request_string, start=start_date)
