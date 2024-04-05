import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
        self.units += units
        self.trades += 1
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
