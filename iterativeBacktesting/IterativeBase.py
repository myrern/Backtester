import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import tabulate
from scipy.stats import norm

import matplotlib.dates as mdates
import matplotlib.ticker as ticker


class IterativeBase():

    def __init__(self, amount, data):
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.data = data
        self.process_data()
        self.last_buy_units = 0
        self.last_sell_units = 0
        self.trade_returns = []
        self.trade_dates = []
    

        self.balance_history = [amount]  # Initial balance
        self.date_history = [data.index[0]]  # Assuming trades start from the beginning of the dataset
        self.trades = 0

    def process_data(self):
        self.data["Returns"] = np.log(self.data["mid_c"] / self.data["mid_c"].shift(1))
        self.data.dropna(inplace=True)
    
    def get_current_candle(self, candle):
        date = self.data.index[candle]
        price = self.data["mid_o"].iloc[candle]
        return date, price
    
    def buy_asset(self, candle, units=None, amount=None):
        date, open_price = self.get_current_candle(candle)
        if amount is not None:
            units = int(amount / open_price)
        self.current_balance -= units * open_price
        self.last_buy_units = units
        self.last_buy_price = open_price  # Store the purchase price
        self.units += units
        self.trades += 1

        print("{} | Buying {} for {}".format(date, units, open_price))


    def close_position1(self, candle):
        date, close_price = self.get_current_candle(candle)
        if self.last_buy_units != 0:
            # Calculate profit: (close_price - last_buy_price) * units sold
            profit = (close_price - self.last_buy_price) * self.last_buy_units
            # Calculate return: profit / initial investment
            initial_investment = self.last_buy_price * self.last_buy_units
            trade_return = profit / initial_investment
            self.trade_returns.append(trade_return)  # Append the calculated return
            self.trade_dates.append(date)  # Record the date of the trade
            # Update current balance based on the sale
            self.current_balance += self.last_buy_units * close_price
            self.units -= self.last_buy_units
            self.trades += 1
            print(f"{date} | Closing position for {close_price}, Return: {trade_return:.2%}")


        self.balance_history.append(self.current_balance)
        self.date_history.append(date)  # Save the date of the trade
        print("{} |  Buying {} for {}".format(date, units, open_price))
    
    def close_position(self, candle, position=None):
        date, open_price = self.get_current_candle(candle)
        if position == 1:
            if self.last_buy_units != 0:
                self.current_balance += self.last_buy_units * open_price
                self.units -= self.last_buy_units
                self.trades += 1
                self.balance_history.append(self.current_balance)
                self.date_history.append(date)  # Save the date of the trade
                print("{} |  Closing position for {}".format(date, open_price))

    
    def sell_asset(self, candle, units=None, amount=None):
        date, open_price = self.get_current_candle(candle)
        if amount is not None:
            units = int(amount / open_price)
        self.current_balance += units * open_price
        self.units -= units
        self.trades += 1
        self.balance_history.append(self.current_balance)
        self.date_history.append(date)  # Save the date of the trade
        print("{} |  Selling {} for {}".format(date, units, open_price))
    
    def print_current_balance(self, bar):
        date, price = self.get_current_candle(bar)
        print("{} | Current Balance: {}".format(date, round(self.current_balance, 2)))


    def calculate_max_drawdown(self):
        # Calculate the max drawdown
        self.data['peak'] = self.data['mid_c'].cummax()
        self.data['drawdown'] = (self.data['mid_c'] - self.data['peak']) / self.data['peak']
        max_dd = self.data['drawdown'].min()
        print("Max Drawdown: {:.2%}".format(max_dd))


        # Plot the drawdowns 
        plt.figure(figsize=(10, 6))
        plt.fill_between(self.data.index, self.data['drawdown'], color='red', alpha=0.3)
        plt.title('Drawdown over time')
        plt.show()

        
        return max_dd
   
   

    
    def close_final_position(self, candle):
        date, close_price = self.get_current_candle(candle)
        if self.units > 0:
            self.current_balance += self.units * close_price
            self.balance_history.append(self.current_balance)
            self.date_history.append(date)  # Save the date of closing final position
        print(75 * "-")
        print("{} | +++ CLOSING FINAL POSITION +++".format(date))
        self.units = 0
        self.trades += 1
        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100

        #self.print_current_balance(candle)
        #print("{} | net performance (%) = {}".format(date, round(perf, 2)  ))
        #print("{} | number of trades executed = {}".format(date, self.trades))
        #print(75 * "-")

    def summary(self):
        if hasattr(self, 'trade_returns') and hasattr(self, 'trade_dates') and len(self.trade_returns) > 0:
            # Create a DataFrame with trade returns and dates
            df = pd.DataFrame({'Returns': self.trade_returns}, index=pd.to_datetime(self.trade_dates))
                
            # Ensure the index is a DatetimeIndex
            df.index = pd.to_datetime(df.index)

            starting_equity = self.initial_balance
            total_return = np.exp(df['Returns'].sum()) - 1
            monthly_return = df['Returns'].mean() * 21  # Assuming 21 trading days in a month
            annualized_return = df['Returns'].mean() * 252  # Assuming 252 trading days in a year
            standard_deviation = df['Returns'].std() * np.sqrt(252)  # Annualized Volatility
            exposure_time = len(df) / len(self.data) * 100  # Percentage of time exposed to the market
            equity_peak = self.current_balance.max()
            hold_return = (self.data['mid_c'].iloc[-1] - self.data['mid_c'].iloc[0]) / self.data['mid_c'].iloc[0]


            # Calculate additional metrics like the Sharpe Ratio and Standard Deviation of returns
            risk_free_rate = 0.0425  
            excess_returns = df['Returns'] - risk_free_rate/252  # Assuming 252 trading days in a year
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
                

            summary_metrics = {
                    'Start': df.index.min(),
                    'End': df.index.max(),
                    'Duration [Days]': (df.index.max() - df.index.min()).days,
                    'Exposure Time [%]': exposure_time,
                    'Equity Start [$]': starting_equity,
                    'Equity Final [$]': self.current_balance,
                    'Equity Peak [$]': equity_peak,
                    'Strategy Return [%]': total_return * 100,
                    'Hold Return [%]': hold_return * 100,
                    'Average Yearly Return [%]': annualized_return * 100,
                    'Average Monthly Return [%]':  monthly_return * 100,
                    'Standard deviation (Ann.) [%]': standard_deviation * 100,
                    'Sharpe Ratio': sharpe_ratio
                    
                        
                    }
                
            # round the values to 2 decimal places if they are floats
            for key, value in summary_metrics.items():
                if isinstance(value, float):
                    summary_metrics[key] = round(value, 2)

            print(tabulate.tabulate(summary_metrics.items(), tablefmt="plain", headers=["Metric", "Value"]))
            
        else:
            print("No trades executed")

        self.print_current_balance(candle)
        print("{} | net performance (%) = {}".format(date, round(perf, 2)))
        print("{} | number of trades executed = {}".format(date, self.trades))
        print(75 * "-")
        

        # Convert the saved trade dates into matplotlib's date format
        dates = mdates.date2num(self.date_history)

        # Plot the balance history
        plt.figure(figsize=(10, 6))

        # Create an area plot (filled plot)
        plt.fill_between(dates, self.balance_history, color="skyblue", alpha=0.4)
        plt.plot(dates, self.balance_history, color="Slateblue", alpha=0.6)

        # Format the y-axis to show full numbers without scientific notation
        plt.gca().get_yaxis().set_major_formatter(
            ticker.FuncFormatter(lambda x, p: format(int(x), ','))
        )

        # Set the x-axis to only display the year
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        # Rotate date labels for better readability
        plt.gcf().autofmt_xdate()

        # Add text for the last balance
        last_balance = self.balance_history[-1]
        last_date = dates[-1]
        plt.text(last_date, last_balance, f'Last Balance: ${format(last_balance, ",.2f")}',
                horizontalalignment='right', verticalalignment='bottom', fontsize=10, color='darkgreen')

        plt.title("Balance Over Time")
        plt.xlabel("Date")
        plt.ylabel("Balance")
        plt.grid(True)
        plt.show()