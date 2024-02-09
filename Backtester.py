from tkinter import scrolledtext
import pandas as pd
import numpy as np
import pandas as pd
from TechnicalIndicators import *
from Strategies import *
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # For custom x-axis labels
import matplotlib.dates as mdates # For formatting dates on x-axis
import tkinter as tk # For file dialog
from plot.Plotter import Plotter

plt.style.use("seaborn-v0_8")
pd.set_option('display.float_format', lambda x: '%.5f' % x)

class Backtester:
    def __init__(self, asset):
        self.asset_name = asset["name"]
        self.asset_type = asset["type"]
    
    def run_backtest(self):
        self.loop_granularities()
    
    def loop_granularities(self):
        granularities = ["H1"]
        for granularity in granularities:
            self.get_data_by_granularity(granularity)
    
    def get_data_by_granularity(self, granularity):
        file_path = f"data/{self.asset_name}_{granularity}_{self.asset_type}.csv"
        self.original_df = pd.read_csv(file_path)
        self.original_df['time'] = pd.to_datetime(self.original_df['time']) 
        self.original_df.set_index('time', inplace=True)

        self.data = self.original_df.loc["2023-03-08T13:00:00.000000000Z": "2023-09-07T09:00:00.000000000Z"].copy()
        self.add_spread()

    def add_spread(self):
        # Use the new 'Mid' column instead of calculating 'Mid_close'
        self.data["Spread"] = self.data["ask_c"].astype(float) - self.data["bid_c"].astype(float)
        self.apply_strategies()

    def apply_strategies(self):
        self.technical_indicators = TechnicalIndicators(self.data)
        self.strategies = Strategies(self.data)

        self.data, self.strategy_name = self.strategies.SMA_Crossover(50, 150)
        self.data.dropna(inplace=True)

        self.calculate_returns()


    def calculate_returns(self):
        # Calculate cumulative returns
        self.data["Cumulative_Hold"] = self.data["Returns"].cumsum().apply(np.exp)
        self.data["Cumulative_Strategy"] = self.data["Strategy"].cumsum().apply(np.exp)

        # Convert to percentage change
        self.data["Hold_Returns"] = (self.data["Cumulative_Hold"] / self.data["Cumulative_Hold"].iloc[0] - 1) * 100
        self.data["Strategy_Returns"] = (self.data["Cumulative_Strategy"] / self.data["Cumulative_Strategy"].iloc[0] - 1) * 100

        self.print_strategy_returns()
    
    def print_strategy_returns(self):
        self.calcualte_factors()
    
    def calcualte_factors(self):
        # Calculate Sharpe Ratio
        strategy_std = self.data["Strategy"].std()
        strategy_annualized_std = strategy_std * np.sqrt(252)
        strategy_sharpe = (self.data["Strategy"].mean() - 0.01) / strategy_annualized_std

        # Calculate Maximum Drawdown
        strategy_cummax = self.data["Cumulative_Strategy"].cummax()
        strategy_drawdown = (self.data["Cumulative_Strategy"] - strategy_cummax) / strategy_cummax
        strategy_max_drawdown = strategy_drawdown.min()

        #Calculate Win Rate

        print(f"Sharpe Ratio: {strategy_sharpe:.2f}")
        print(f"Maximum Drawdown: {strategy_max_drawdown:.2%}")

        # Calculate the change in position to identify trades
        self.data['Position_Change'] = self.data['Position'].diff()

        # Identify trade entry points
        trade_entries = self.data['Position_Change'].abs() > 0

        # Calculate the number of trades
        num_trades = trade_entries.sum()

        # Initialize variables to track the best and worst trade, and win/loss counts
        best_trade = None
        worst_trade = None
        wins = 0
        losses = 0
        current_trade_return = 0

        for i in range(len(self.data)):
            if trade_entries.iloc[i]:
                # At the start of a new trade, check if the previous trade was a win or loss
                if current_trade_return > 0:
                    wins += 1
                elif current_trade_return < 0:
                    losses += 1
                # Reset current trade return at the start of a new trade
                current_trade_return = 0
            current_trade_return += self.data['Returns'].iloc[i]
            # At the end of a trade or at the last available data point, evaluate the trade
            if trade_entries.iloc[i] or i == len(self.data) - 1:
                if best_trade is None or current_trade_return > best_trade:
                    best_trade = current_trade_return
                if worst_trade is None or current_trade_return < worst_trade:
                    worst_trade = current_trade_return
                # Evaluate the last trade in the dataset
                if i == len(self.data) - 1:
                    if current_trade_return > 0:
                        wins += 1
                    elif current_trade_return < 0:
                        losses += 1

        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0

        print(f"Number of Trades: {num_trades}")
        print(f"Best Trade: {best_trade}")
        print(f"Worst Trade: {worst_trade}")
        print(f"Win Rate: {win_rate:.2%}")

        summary = f"""
        Sharpe Ratio: {strategy_sharpe:.2f} 
        Maximum Drawdown: {strategy_max_drawdown:.2%} 
        Number of Trades: {num_trades} 
        Best Trade: {best_trade} 
        Worst Trade: {worst_trade} 
        Win Rate: {win_rate:.2%}
        """

        self.plot(summary)

    def plot(self, summary):
        Plotter.plot_candle(self.data, self.asset_name, self.strategy_name, summary)