import pandas as pd
import numpy as np
from scipy.stats import norm

class IterativeBase():

    def __init__(self, amount, data):
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trader = 0
        self.position = 0
        self.data = data
        self.process_data()
        self.last_buy_units = 0
        self.last_sell_units = 0
        self.trade_returns = []
        self.trade_dates = []
    
    
    def process_data(self):
        self.data["Returns"] = np.log(self.data["mid_c"] / self.data["mid_c"].shift(1))
        #self.data["Spread"] = self.data["ask_c"].astype(float) - self.data["bid_c"].astype(float)
        self.data.dropna(inplace = True)
    
    def get_current_candle(self, candle):
        date = str(self.data.index[candle].date())
        price = self.data["mid_o"].iloc[candle]
        #spread = self.data["Spread"].iloc[candle]
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


    def close_position(self, candle):
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

    
    def sell_asset(self, candle, units = None, amount = None):
        date, open_price = self.get_current_candle(candle)
        if amount is not None:
            units = int(amount / open_price)
        self.current_balance += units * open_price
        self.units -= units
        self.trades += 1
        print("{} |  Selling {} for {}".format(date, units, open_price))
    
    def print_current_balance(self, bar):
        date, price = self.get_current_candle(bar)
        print("{} | Current Balance: {}".format(date, round(self.current_balance, 2)))
    
    def close_final_position(self, candle):
        date, close_price = self.get_current_candle(candle)
        print(75 * "-")
        print("{} | +++ CLOSING FINAL POSITION +++".format(date))
        self.current_balance += self.units * close_price
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

            yearly_returns = df['Returns'].resample('YE').sum()
            monthly_returns = df['Returns'].resample('ME').sum()

            # Convert log returns to simple returns for yearly and monthly aggregates
            avg_yearly_return = yearly_returns.mean()
            avg_monthly_return = monthly_returns.mean()


            # Calculate additional metrics like the Sharpe Ratio and Standard Deviation of returns
            risk_free_rate = 0.0425  
            excess_returns = df['Returns'] - risk_free_rate/252  # Assuming 252 trading days in a year
            sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
            std_dev = df['Returns'].std() * np.sqrt(252)  # Annualized Standard Deviation

            print(75 * "-")
            # Print the summary statistics
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"Standard Deviation (Annualized): {std_dev:.2%}")
            print("Total Return: {:.2%}".format(np.exp(df['Returns'].sum()) - 1))
            print(f"Average Yearly Return: {avg_yearly_return:.2%}")
            print(f"Average Monthly Return: {avg_monthly_return:.2%}")
            print(75 * "-")
        else:
            print("No trades executed.")
