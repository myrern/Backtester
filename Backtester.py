import tkinter as tk  # For file dialog
from tkinter import scrolledtext

import matplotlib.dates as mdates  # For formatting dates on x-axis
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker  # For custom x-axis labels
import numpy as np
import pandas as pd

from plot.Plotter import Plotter
from Strategies import *
from TechnicalIndicators import *

plt.style.use("seaborn-v0_8")
pd.set_option("display.float_format", lambda x: "%.5f" % x)


class Backtester:
    def __init__(self, asset):
        self.asset_name = asset["name"]
        self.asset_type = asset["type"]

    def run_backtest(self):
        self.loop_granularities()

    def loop_granularities(self):
        granularities = ["D"]
        for granularity in granularities:
            self.get_data_by_granularity(granularity)

    def get_data_by_granularity(self, granularity):
        file_path = f"data/{self.asset_name}_{granularity}_{self.asset_type}.csv"
        self.original_df = pd.read_csv(file_path)
        self.original_df["time"] = pd.to_datetime(self.original_df["time"])
        self.original_df.set_index("time", inplace=True)

        self.data = self.original_df.copy()

        self.add_spread()

    def add_spread(self):
        # Use the new 'Mid' column instead of calculating 'Mid_close'
        self.data["Spread"] = self.data["ask_c"].astype(float) - self.data[
            "bid_c"
        ].astype(float)
        self.apply_strategies()

    def apply_strategies(self):
        self.technical_indicators = TechnicalIndicators(self.data)
        self.strategies = Strategies(self.data)

        # self.data, self.strategy_name = self.strategies.SMA_Crossover(50, 150)
        self.data["Returns"] = np.log(self.data["mid_c"] / self.data["mid_c"].shift(1))
        self.data, self.strategy_name = self.strategies.optimize_SMA_Crossover()

        self.data.dropna(inplace=True)
        self.calculate_returns()

        # self.calculate_returns()
        # self.plot()

    def calculate_returns(self):
        # Calculate cumulative returns
        self.data["Cumulative_Hold"] = self.data["Returns"].cumsum().apply(np.exp)
        self.data["Cumulative_Strategy"] = (
            self.data["Strategy" + self.strategy_name].cumsum().apply(np.exp)
        )

        # Convert to percentage change
        self.data["Hold_Returns"] = (
            self.data["Cumulative_Hold"] / self.data["Cumulative_Hold"].iloc[0] - 1
        ) * 100
        self.data["Strategy_Returns"] = (
            self.data["Cumulative_Strategy"] / self.data["Cumulative_Strategy"].iloc[0]
            - 1
        ) * 100

        self.plot()

    def plot(self):
        Plotter.plot_candle(self.data, self.asset_name, self.strategy_name)
