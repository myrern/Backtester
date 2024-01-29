from tkinter import scrolledtext
import pandas as pd
import numpy as np
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
        rsi_buy = 30
        rsi_sell = 70
        # Apply strategies here
        self.data["RSI"] = self.technical_indicators.RSI(period=14, column="bid_c")
        self.data["Returns"] = np.log(self.data["mid_c"]/self.data["mid_c"].shift(1))
        self.data["Position"] = 0
        self.data["Position"] = np.where(self.data['RSI'] < rsi_buy, 1, 
                                    np.where(self.data['RSI'] > rsi_sell, -1, 0))
        self.data["Strategy"] = self.data["Position"].shift(1) * self.data["Returns"]
        
        self.data.dropna(inplace=True)
        print(self.data.head())

        self.calculate_returns()
        self.plot_returns()
        self.calculate_summary()
        self.display_summary_popup()

    def calculate_returns(self):
        # Calculate cumulative returns
        self.data["Cumulative_Hold"] = self.data["Returns"].cumsum().apply(np.exp)
        self.data["Cumulative_Strategy"] = self.data["Strategy"].cumsum().apply(np.exp)

        # Convert to percentage change
        self.data["Hold_Returns"] = (self.data["Cumulative_Hold"] / self.data["Cumulative_Hold"].iloc[0] - 1) * 100
        self.data["Strategy_Returns"] = (self.data["Cumulative_Strategy"] / self.data["Cumulative_Strategy"].iloc[0] - 1) * 100


    def plot_returns(self):
        # Determine the range of the data
        date_range = self.data.index.max() - self.data.index.min()

        # Plotting
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot the 'Strategy_Returns'
        ax.plot(self.data.index, self.data["Strategy_Returns"], label='Strategy Returns')

        # Fill the area under the 'Strategy_Returns' curve
        ax.fill_between(self.data.index, 0, self.data["Strategy_Returns"],
                        where=(self.data["Strategy_Returns"] >= 0), facecolor='green', alpha=0.3, interpolate=True)
        ax.fill_between(self.data.index, 0, self.data["Strategy_Returns"],
                        where=(self.data["Strategy_Returns"] < 0), facecolor='red', alpha=0.3, interpolate=True)

        # Set x-axis major locator and formatter dynamically
        if date_range.days > 365 * 5:
            # Data spans over multiple years, show ticks per year
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif date_range.days > 365:
            # Data spans over a year, show ticks per month
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        else:
            # Data is less than a year, show ticks per week
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

        # Rotate date labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

        # Set y-axis formatter
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: '{:.0f}%'.format(y)))
        plt.ylabel('Percentage Change (%)')
        plt.title('Strategy Returns Over Time')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def calculate_summary(self):
        # Calculate various statistics
        start_date = self.data.index.min()
        end_date = self.data.index.max()
        duration = (end_date - start_date).days

        initial_equity = 100000  # Example initial equity
        final_equity = initial_equity * (1 + self.data["Hold_Returns"].iloc[-1] / 100)
        equity_peak = initial_equity * (1 + self.data["Hold_Returns"].cummax().iloc[-1] / 100)
            
        total_return_percent = self.data["Hold_Returns"].iloc[-1]
        annual_return_percent = (1 + total_return_percent / 100) ** (365 / duration) - 1
            
        # Calculate other metrics like volatility, Sharpe ratio, etc.
        # These calculations would depend on the details of your strategy and the data available.
        # ...

        # Compile the summary data into a dictionary
        summary_data = {
            "Start":             start_date,
            "End":               end_date,
            "Duration":          f"{duration} days",
            "Equity Final [$]":  final_equity,
            "Equity Peak [$]":   equity_peak,
            "Return [%]":        total_return_percent,
            "Annual Return [%]": annual_return_percent,
            # ... [add other calculated metrics here] ...
            "_strategy": self.__class__.__name__
            }

        return summary_data

    def display_summary_popup(self):
        # Get the summary data
        summary_data = self.calculate_summary()

        # Create a new Tkinter window
        window = tk.Tk()
        window.title("Backtest Summary")

        # Define the window size
        window.geometry('600x400')  # Width x Height

        # Create a scrolled text area widget
        text_area = scrolledtext.ScrolledText(window, wrap=tk.WORD)
        text_area.pack(expand=True, fill='both')

        # Format and insert the summary data into the text area
        formatted_summary = "\n".join(f"{key}: {value}" for key, value in summary_data.items())
        text_area.insert(tk.INSERT, formatted_summary)

        # Start the Tkinter event loop
        window.mainloop()