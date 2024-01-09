from arcticdb import Arctic
from dash import callback, dash_table, dcc, html, no_update, Input, Output
from dash_iconify import DashIconify
import dash_mantine_components as dmc
import plotly.express as px

from .backend.data_fetching import fetch_or_download_data, get_nasdaq_ticker_names
from .backend.time_series_analysis import macd_analysis
from .common import DBLibraries, DBSymbols, TSAnalyses

_HEADER_HEIGHT = 60

_SPACER = dmc.Space(h=30)


def header_bar():
    """Returns the header bar for the dashboard."""
    return dmc.Header(
        children=dmc.Group(
            [
                DashIconify(
                    icon="mdi:chart-line",
                    color="blue",
                    height=_HEADER_HEIGHT,
                    width=_HEADER_HEIGHT,
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


def time_series_analysis_dropdown():
    return dmc.Select(
        label="Time series analysis method",
        placeholder="Select analysis method",
        data=[
            {"label": "Moving average convergence-divergence", "value": "MACD"},
        ],
        searchable=True,
        id="time-series-analysis-dropdown",
    )


def macd_parameter_inputs():
    return dmc.Group(
        [
            dmc.NumberInput(
                label="Fast period",
                min=1,
                max=100,
                step=1,
                value=12,
                id="macd-fast-period-input",
            ),
            dmc.NumberInput(
                label="Slow period",
                min=1,
                max=100,
                step=1,
                value=26,
                id="macd-slow-period-input",
            ),
            dmc.NumberInput(
                label="Signal period",
                min=1,
                max=100,
                step=1,
                value=9,
                id="macd-signal-period-input",
            ),
        ]
    )


@callback(
    inputs=[
        Input("ticker-multi-selection", "value"),
        Input("time-series-analysis-dropdown", "value"),
        Input("macd-fast-period-input", "value"),
        Input("macd-slow-period-input", "value"),
        Input("macd-signal-period-input", "value"),
    ],
    output=Output("time-series-analysis-charts", "children"),
    prevent_initial_call=True,
)
def time_series_analysis_chart(
    tickers, analysis_method, fast_period, slow_period, signal_period
):
    # We can only analyse one stock at a time.
    if not tickers or len(tickers) > 1:
        return no_update

    stock_ticker = tickers[0]

    # Fetch the market data from the database -- by now, it should be cached but
    # just in case, we use the helper function to download it if necessary.
    library = db[DBLibraries.Caches.value]
    dfs = fetch_or_download_data(tickers, library)

    # Sanity check that we only have one DataFrame to analyse.
    if len(dfs) > 1:
        return no_update
    else:
        df = dfs[0]

    # Perform the analysis.
    if analysis_method == TSAnalyses.MACD.value:
        fig_candlestick, fig_indicator = macd_analysis(
            df, stock_ticker, fast_period, slow_period, signal_period
        )
        return [dcc.Graph(figure=fig_candlestick), dcc.Graph(figure=fig_indicator)]

    # Fallback, don't update the charts.
    return no_update


@callback(
    inputs=[Input("time-series-analysis-dropdown", "value")],
    output=Output("time-series-analysis-parameters", "children"),
    prevent_initial_call=True,
)
def instantiate_time_series_analysis_parameters(analysis_method):
    if analysis_method == TSAnalyses.MACD.value:
        return macd_parameter_inputs()
    else:
        return no_update


def layout(database: Arctic):
    # Quickest way to get the database into the callbacks.
    # NOTE: This is not safe (especially) for ArcticDB since transactions are not atomic.
    # TODO: Find a thread-safe way to pass the database connection to the callbacks.
    global db
    db = database

    header = header_bar()

    exploration_heading = dmc.Title("Explore the market", order=2)
    analysis_heading = dmc.Title("Analyse one stock in detail", order=2)
    history_chart = dcc.Graph(id="stock-history-chart")

    body = dmc.Grid(
        children=[
            dmc.Col(
                dmc.Stack(
                    [
                        exploration_heading,
                        ticker_multi_selection(database),
                        history_chart,
                    ]
                ),
                span=5,
            ),
            dmc.Col(
                dmc.Stack(
                    [
                        analysis_heading,
                        time_series_analysis_dropdown(),
                        html.Div(id="time-series-analysis-parameters"),
                        html.Div(id="time-series-analysis-charts"),
                    ]
                ),
                span=7,
            ),
        ],
    )
    div = html.Div([header, _SPACER, body, _SPACER])
    return div
