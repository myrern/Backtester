import pandas as pd
import numpy as np

class IterativeBase():

    def __init__(self, amount, data):
        self.initial_balance = amount
        self.current_balance = amount
        self.units = 0
        self.trader = 0
        self.position = 0
        self.data = data
        self.process_data()
    
    def process_data(self):
        self.data["Returns"] = np.log(self.data["mid_c"] / self.data["mid_c"].shift(1))
        #self.data["Spread"] = self.data["ask_c"].astype(float) - self.data["bid_c"].astype(float)
        self.data.dropna(inplace = True)
    
    def get_current_candle(self, candle):
        date = str(self.data.index[candle].date())
        price = self.data["mid_o"].iloc[candle]
        #spread = self.data["Spread"].iloc[candle]
        return date, price
    
    def buy_asset(self, candle, units = None, amount = None):
        date, open_price = self.get_current_candle(candle)
        if amount is not None:
            units = int(amount / open_price)
        self.current_balance -= units * open_price
        self.units += units
        self.trades += 1
        print("{} |  Buying {} for {}".format(date, units, open_price))
    
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
    
    def close_position(self, candle):
        date, close_price = self.get_current_candle(candle)
        print(75 * "-")
        print("{} | +++ CLOSING FINAL POSITION +++".format(date))
        self.current_balance += self.units * close_price
        self.units = 0
        self.trades += 1
        perf = (self.current_balance - self.initial_balance) / self.initial_balance * 100
        self.print_current_balance(candle)
        print("{} | net performance (%) = {}".format(date, round(perf, 2)  ))
        print("{} | number of trades executed = {}".format(date, self.trades))
        print(75 * "-")