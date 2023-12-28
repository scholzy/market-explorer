from arcticdb import Arctic
from dash import callback, dash_table, dcc, html, no_update, Input, Output, State
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import yfinance as yf

from .backend.data_fetching import fetch_or_download_data, get_nasdaq_ticker_names
from .common import DBLibraries, DBSymbols

_HEADER_HEIGHT = 60

_SPACER = dmc.Space(h=30)


def header_bar():
    """Returns the header bar for the dashboard."""
    return dmc.Header(
        children=dmc.Group(
            [
                DashIconify(
                    icon="mdi:chart-line", height=_HEADER_HEIGHT, width=_HEADER_HEIGHT
                ),
                dmc.Title("Market Explorer Dashboard", order=1),
            ]
        ),
        height=_HEADER_HEIGHT,
    )


def ticker_multi_selection(database: Arctic):
    """Returns the multi-selection for the tickers.

    Args:
        database (Arctic): The Arctic database to read the data from.
    """
    ticker_data = get_nasdaq_ticker_names(database[DBLibraries.Exchanges.value])
    selections = [
        {"label": f"{ticker['name']} ({ticker['symbol']})", "value": ticker["symbol"]}
        for _, ticker in ticker_data.iterrows()
    ]
    return dmc.MultiSelect(
        label="Tickers",
        placeholder="Select tickers",
        data=selections,
        searchable=True,
        id="ticker-multi-selection",
    )


def ticker_data_table(database: Arctic):
    """Returns the table of ticker data.

    Used for debugging and visualisation purposes.

    Args:
        database (Arctic): The Arctic database to read the data from.
    """
    exchanges_library = database[DBLibraries.Exchanges.value]
    nasdaq_tickers = exchanges_library.read(DBSymbols.NasdaqTickers.value).data
    return dash_table.DataTable(
        data=nasdaq_tickers.to_dict("records"),
    )


@callback(
    inputs=[Input("ticker-multi-selection", "value")],
    output=Output("stock-history-chart", "figure"),
    prevent_initial_call=True,
)
def stock_history_chart(tickers):
    fig = px.scatter()

    if not tickers:
        return fig

    library = db[DBLibraries.Caches.value]
    dfs = fetch_or_download_data(tickers, library)

    for df, ticker in zip(dfs, tickers):
        fig.add_scatter(x=df.index, y=df["Close"], name=ticker)

    return fig


def layout(database: Arctic):
    global db
    db = database

    header = header_bar()
    table = ticker_data_table(database)
    chart = dcc.Graph(id="stock-history-chart")
    body = dmc.Grid(
        children=[dmc.Col(ticker_multi_selection(database), span=4), dmc.Col(chart, span=8)],
        style={"height": 400},
    )
    div = html.Div([header, _SPACER, body, _SPACER, table])
    return div
