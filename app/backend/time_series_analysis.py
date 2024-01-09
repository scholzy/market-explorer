import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def macd_analysis(
    df: pd.DataFrame, name: str, fast_span: int, slow_span: int, signal_span: int
) -> tuple[go.Figure, go.Figure]:
    """Returns a MACD analysis of the given DataFrame.

    Args:
        dataframe (pd.DataFrame): The DataFrame to analyse.
        name (str): The name to insert into plot titles.
        fast_span (int): The fast period for MACD analysis.
        slow_span (int): The slow period.
        signal_span (int): The signal period.
    """
    data = go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
    )
    fig_candlestick = go.Figure(data=[data])

    # Calculate the fast and slow signals, exponential moving averages over the
    # given periods.
    fast_signal = df["Close"].ewm(span=fast_span).mean()
    slow_signal = df["Close"].ewm(span=slow_span).mean()

    # Draw line plots visualising these signals, overlaid over the candlestick plot.
    fig_candlestick.add_scatter(x=df.index, y=fast_signal, name="Fast signal")
    fig_candlestick.add_scatter(x=df.index, y=slow_signal, name="Slow signal")
    fig_candlestick.update_layout({"title": {"text": f"Candlestick plot for {name}"}})

    # The Moving Average Convergence Divergence (MACD) is the difference between
    # the fast and slow signals. Then, the signal is the exponential moving average
    # of the MACD. Finally, the divergence is the difference between the MACD and
    # the signal.
    macd = fast_signal - slow_signal
    macd_signal = macd.ewm(span=signal_span).mean()
    macd_histogram = macd - macd_signal

    # Draw line plots visualising all three signals.
    # TODO: Figure out how to plot the MACD as a histogram which seems to be convention.
    fig_indicator = px.scatter()
    fig_indicator.add_scatter(x=df.index, y=macd, name="MACD")
    fig_indicator.add_scatter(x=df.index, y=macd_signal, name="Signal")
    fig_indicator.add_scatter(x=df.index, y=macd_histogram, name="Divergence")
    fig_indicator.update_layout({"title": {"text": f"MACD analysis plot for {name}"}})

    return fig_candlestick, fig_indicator
