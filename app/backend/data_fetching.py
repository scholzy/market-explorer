import json

from arcticdb.version_store.library import Library
import pandas as pd
import yfinance as yf


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
    library.write("nasdaq_tickers", df)


def get_tickers(tickers: list[str]):
    """Returns a yfinance Ticker object for the given list of ticker symbols.

    Args:
        tickers (list[str]): List of ticker symbols for the stocks.
    """
    return yf.Ticker(" ".join(tickers))


def download_data(tickers: list[str], period: str = "1y"):
    """Downloads the historical data for the given list of ticker symbols.

    Args:
        tickers (list[str]): List of ticker symbols for the stocks.
        period (str, optional): The period of time to download the data for. Defaults to "1mo".
    """
    request_string = " ".join(tickers)
    return yf.download(request_string, period=period)
