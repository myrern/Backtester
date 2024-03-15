import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from plot.Plotter import Plotter
from Strategies import *
from TechnicalIndicators import *
from iterativeBacktesting import IterativeBacktest as IB

plt.style.use("seaborn-v0_8")
pd.set_option("display.float_format", lambda x: "%.5f" % x)


class Backtester:
    def __init__(self, asset, iterative = False, optimize_parameters = False, initial_balance = 100000):
        self.asset_name = asset["name"]
        self.asset_type = asset["type"]
        self.iterative = iterative
        self.optimize_parameters = optimize_parameters
        self.initial_balance = initial_balance

    def run_backtest(self):
        self.loop_granularities()
        self.add_spread()
        self.apply_strategies()
        self.calculate_returns()
        return self.data

    def loop_granularities(self):
        granularities = ["D"]
        for granularity in granularities:
            self.get_data_by_granularity(granularity)

    def get_data_by_granularity(self, granularity):
        file_path = f"data/{self.asset_name}_{granularity}_{self.asset_type}.csv"
        self.original_df = pd.read_csv(file_path)
        self.original_df["time"] = pd.to_datetime(self.original_df["time"])
        self.original_df.set_index("time", inplace=True)

        #set data to 30% og the original data
        #self.data = self.original_df.copy().iloc[: int(len(self.original_df) * 0.3)]
        self.data = self.original_df.copy()

    def add_spread(self):
        # Use the new 'Mid' column instead of calculating 'Mid_close'
        self.data["Spread"] = self.data["ask_c"].astype(float) - self.data[
            "bid_c"
        ].astype(float)

    def apply_strategies(self):
        self.data["Returns"] = np.log(self.data["mid_c"] / self.data["mid_c"].shift(1))
        self.strategies = Strategies(self.data)

        if self.iterative:
            self.iterative_backtest()
        else:
            self.vectorized_backtest()
    
    def vectorized_backtest(self):
        if self.optimize_parameters:
            self.data, self.strategy_name = self.strategies.IBS_Strategy(0.1, 0.9)
        else:
           self.data, self.strategy_name = self.strategies.IBS_Strategy(0.1, 0.9)
        
        self.data.dropna(inplace=True)
    
    def iterative_backtest(self):
        iterative_backtest = IB.IterativeBactest(self.initial_balance, self.data)
        self.data, self.strategy_name = iterative_backtest.test_IBS_strategy(0.6, 0.8)
        #self.data, self.strategy_name = iterative_backtest.test_IBS_strategy_enhanced(20, 12, 26, 14)
        #self.data, self.strategy_name = iterative_backtest.test_sma_strategy(150, 50, self.data)
        self.data.dropna(inplace=True)

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
        #Plotter.plot_candle(self.data, self.asset_name, self.strategy_name)
        pass