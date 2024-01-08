import pandas as pd
import plotly.graph_objects as go


def macd_analysis(
    df: pd.DataFrame, fast_span: int, slow_span: int, signal_span: int
) -> go.Figure:
    """Returns a MACD analysis of the given DataFrame.

    Args:
        dataframe (pd.DataFrame): The DataFrame to analyse.
    """
    data = go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
    )
    fig = go.Figure(data=[data])

    fast_signal = df["Close"].ewm(span=fast_span).mean()
    slow_signal = df["Close"].ewm(span=slow_span).mean()
    fig.add_scatter(x=df.index, y=fast_signal, name="Fast signal")
    fig.add_scatter(x=df.index, y=slow_signal, name="Slow signal")

    return fig
