from tkinter import scrolledtext
import pandas as pd
import numpy as np
from plotly import graph_objs as go
import pandas as pd
import plotly
from TechnicalIndicators import *
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # For custom x-axis labels
import matplotlib.dates as mdates # For formatting dates on x-axis
import tkinter as tk # For file dialog
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

        self.data = self.original_df.copy()
        self.add_spread()

    def add_spread(self):
        # Use the new 'Mid' column instead of calculating 'Mid_close'
        self.data["Spread"] = self.data["ask_c"].astype(float) - self.data["bid_c"].astype(float)
        self.apply_strategies()

    def apply_strategies(self):
        self.technical_indicators = TechnicalIndicators(self.data)
        #rsi_buy = 30
        #rsi_sell = 70
        # Apply strategies here
        #self.data["RSI"] = self.technical_indicators.RSI(period=14, column="bid_c")
        self.data["sma_s"] = self.technical_indicators.SMA(period=15, column="mid_c")
        self.data["sma_l"] = self.technical_indicators.SMA(period=50, column="mid_c")
        self.data["Returns"] = np.log(self.data["mid_c"]/self.data["mid_c"].shift(1))
        self.data["Position"] = 0
        #self.data["Position"] = np.where(self.data['RSI'] < rsi_buy, 1, 
         #                           np.where(self.data['RSI'] > rsi_sell, -1, 0))
        self.data["Position"] = np.where(self.data['sma_s'] > self.data['sma_l'], 1, -1)
        self.data["Strategy"] = self.data["Position"].shift(1) * self.data["Returns"]
        
        self.data.dropna(inplace=True)
        print(self.data.head())

        self.calculate_returns()


    def calculate_returns(self):
        # Calculate cumulative returns
        self.data["Cumulative_Hold"] = self.data["Returns"].cumsum().apply(np.exp)
        self.data["Cumulative_Strategy"] = self.data["Strategy"].cumsum().apply(np.exp)

        # Convert to percentage change
        self.data["Hold_Returns"] = (self.data["Cumulative_Hold"] / self.data["Cumulative_Hold"].iloc[0] - 1) * 100
        self.data["Strategy_Returns"] = (self.data["Cumulative_Strategy"] / self.data["Cumulative_Strategy"].iloc[0] - 1) * 100

        # Initialize the Plotly figure for the candlestick chart
        fig = go.Figure(data=[go.Candlestick(x=self.data.index,
                        open=self.data['mid_o'],  # Make sure these columns exist or adjust accordingly
                        high=self.data['mid_h'],
                        low=self.data['mid_l'],
                        close=self.data['mid_c'])])

        # Initialize a variable to store the last position
        last_position = None

        # Loop through the DataFrame and plot arrows on position changes
        for i, row in self.data.iterrows():
            current_position = row['Position']  # Ensure this is the correct column for your strategy's positions
            
            # Check if the current position is different from the last position
            if current_position != last_position:
                # Plot an up arrow for a position change to 1
                if current_position == 1:
                    fig.add_trace(go.Scatter(x=[i], y=[row['mid_l']],  # Use 'i' for the x-axis value if your index is datetime
                                            marker=dict(color='green', size=20),
                                            mode='markers', marker_symbol='arrow-up'))
                # Plot a down arrow for a position change to -1
                elif current_position == -1:
                    fig.add_trace(go.Scatter(x=[i], y=[row['mid_h']],
                                            marker=dict(color='red', size=20),
                                            mode='markers', marker_symbol='arrow-down'))
            # Update the last_position for the next iteration
            last_position = current_position
        
        # Add SMA Short as a line chart
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['sma_s'],
                         mode='lines', name='SMA Short', line=dict(color='blue', width=2)))

        # Add SMA Long line
        fig.add_trace(go.Scatter(x=self.data.index, y=self.data['sma_l'],
                                mode='lines', name='SMA Long', line=dict(color='magenta', width=2)))


        # Updating layout to make it more informative
        fig.update_layout(title='Asset Price with Strategy Positions',
                        xaxis_title='Date',
                        yaxis_title='Price',
                        xaxis_rangeslider_visible=False)  # Hides the range slider

        fig.show()




            


