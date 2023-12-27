from arcticdb import Arctic
from dash import dash_table, html
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .common import DBLibraries, DBSymbols

_HEADER_HEIGHT = 60


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


def layout(database: Arctic):
    header = header_bar()
    table = ticker_data_table(database)
    body = dmc.Grid(children=dmc.Stack(dmc.MultiSelect()))
    div = html.Div([header, body, table])
    return div
