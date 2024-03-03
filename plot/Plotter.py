import tkinter as tk  # For file dialog
from tkinter import scrolledtext

import matplotlib.dates as mdates  # For formatting dates on x-axis
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  # For custom x-axis labels
import numpy as np
import pandas as pd
import plotly
from plotly import graph_objs as go
from plotly.subplots import make_subplots

plt.style.use("seaborn-v0_8")
pd.set_option("display.float_format", lambda x: "%.5f" % x)


class Plotter:
    def plot_returns(data):
        # Determine the range of the data
        date_range = data.index.max() - data.index.min()
        fig, ax = plt.subplots(figsize=(12, 8))

        # Plot the 'Strategy_Returns'
        ax.plot(data.index, data["Strategy_Returns"], label="Strategy Returns")

        # Fill the area under the 'Strategy_Returns' curve
        ax.fill_between(
            data.index,
            0,
            data["Strategy_Returns"],
            where=(data["Strategy_Returns"] >= 0),
            facecolor="green",
            alpha=0.3,
            interpolate=True,
        )
        ax.fill_between(
            data.index,
            0,
            data["Strategy_Returns"],
            where=(data["Strategy_Returns"] < 0),
            facecolor="red",
            alpha=0.3,
            interpolate=True,
        )

        # Set x-axis major locator and formatter dynamically
        if (
            date_range.days > 365 * 5
        ):  # Data spans over multiple years, show ticks per year
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        elif date_range.days > 365:  # Data spans over a year, show ticks per month
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        else:  # Data is less than a year, show ticks per week
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # Set y-axis formatter
        ax.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda y, _: "{:.0f}%".format(y))
        )
        plt.ylabel("Percentage Change (%)")
        plt.title("Strategy Returns Over Time")
        plt.legend()

    def plot_candle(data, asset_name, strategy_name):
        # Create a subplot figure with 2 rows for the candlestick and volume, sharing the x-axis
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.4, 0.2, 0.3],
        )

        # Add the candlestick chart in the first row
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["mid_o"],
                high=data["mid_h"],
                low=data["mid_l"],
                close=data["mid_c"],
                increasing=dict(line=dict(color="green", width=1), fillcolor="green"),
                decreasing=dict(line=dict(color="red", width=1), fillcolor="red"),
                name="Candlestick",
            ),
            row=1,
            col=1,
        )

        volume_colors = [
            "green" if close >= open else "red"
            for close, open in zip(data["mid_c"], data["mid_o"])
        ]

        # Add volume bars in the second row with colors based on the associated candlestick
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["volume"],
                name="Volume",
                marker_color=volume_colors,
            ),
            row=2,
            col=1,
        )

        # Add the Strategy line on the third row
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Cumulative_Strategy"],
                mode="lines",
                name="Strategy Line",
                line=dict(color="yellow", width=2),
            ),
            row=3,
            col=1,
        )

        # Add the Returns line on the third row
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Cumulative_Hold"],
                mode="lines",
                name="Returns Line",
                line=dict(color="blue", width=2),
            ),
            row=3,
            col=1,
        )

        # Initialize a variable to store the last position
        last_position = None

        # Loop through the DataFrame to plot arrows for position changes
        for i, row in data.iterrows():
            current_position = row[
                "Position" + strategy_name
            ]  # Adjust for your position column name

            if current_position != last_position:
                if current_position == 1:
                    fig.add_trace(
                        go.Scatter(
                            x=[i],
                            y=[row["mid_l"]],
                            marker=dict(color="green", size=20),
                            mode="markers",
                            marker_symbol="arrow-up",
                        ),
                        row=1,
                        col=1,
                    )
                elif current_position == -1:
                    fig.add_trace(
                        go.Scatter(
                            x=[i],
                            y=[row["mid_h"]],
                            marker=dict(color="red", size=20),
                            mode="markers",
                            marker_symbol="arrow-down",
                        ),
                        row=1,
                        col=1,
                    )
                last_position = current_position

        # Add SMA lines on the candlestick chart
        if "sma_s" and "sma_l" in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["sma_s"],
                    mode="lines",
                    name="SMA Short",
                    line=dict(color="blue", width=2),
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data["sma_l"],
                    mode="lines",
                    name="SMA Long",
                    line=dict(color="magenta", width=2),
                ),
                row=1,
                col=1,
            )

        # Customize the layout for a dark theme
        fig.update_layout(
            template="plotly_dark",
            title="Asset Price with Strategy Positions for "
            + asset_name
            + " Strategy: "
            + strategy_name,
            title_x=0.5,
            title_font_size=20,
            xaxis_title="Date",
            yaxis_title="Price",
            plot_bgcolor="#08101D",
            paper_bgcolor="#08101D",
            xaxis=dict(color="white", type="date"),
            yaxis=dict(color="white"),
            xaxis2=dict(title="Date", color="white"),
            yaxis2=dict(title="Volume", color="white"),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
            ),
        )

        # Hide the range slider and adjust layout for the candlestick chart
        fig.update_xaxes(rangeslider_visible=False, row=1, col=1)
        fig.update_layout(showlegend=False)

        # Display the figure
        fig.show()
