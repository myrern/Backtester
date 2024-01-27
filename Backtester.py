import pandas as pd
import numpy as np
from TechnicalIndicators import *
import matplotlib.pyplot as plt
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
        self.original_df.set_index('Time', inplace=True)

        self.data = self.original_df.copy()
        self.add_spread()
    
    def add_spread(self):
        self.data["Mid_close"] = (self.data["Bid_c"].astype(float) + self.data["Ask_c"].astype(float)) / 2
        self.data["Spread"] = self.data["Ask_c"].astype(float) - self.data["Bid_c"].astype(float)
        self.apply_strategies()
    
    def apply_strategies(self):
        self.technical_indicators = TechnicalIndicators(self.data)
        rsi_buy = 30
        rsi_sell = 70
        # Apply strategies here
        self.data["RSI"] = self.technical_indicators.RSI(period=14, column="Bid_c")
        self.data["Returns"] = np.log(self.data["Mid_close"]/self.data["Mid_close"].shift(1))
        self.data["Position"] = 0
        self.data["Position"] = np.where(self.data['RSI'] < rsi_buy, 1, 
                                       np.where(self.data['RSI'] > rsi_sell, -1, 0))
        self.data["Strategy"] = self.data["Position"].shift(1) * self.data["Returns"]
        
        self.data.dropna(inplace=True)
        print(self.data.head())

        #plot data
        self.data["Hold_Returns"] = self.data["Returns"].cumsum().apply(np.exp)
        self.data["Strategy_Returns"] = self.data["Strategy"].cumsum().apply(np.exp)
        #self.data[].plot(figsize=(12,8), title=f"{self.asset_name} {self.asset_type}")