import pandas as pd
import numpy as np
from DNNModel import *
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
        granularities = ["D"]
        for granularity in granularities:
            self.get_data_by_granularity(granularity)
    
    def get_data_by_granularity(self, granularity):
        file_path = f"data/{self.asset_name}_{granularity}_{self.asset_type}.csv"
        self.original_df = pd.read_csv(file_path)
        self.original_df.set_index('Time', inplace=True)

        self.data = self.original_df.copy()

        # FOR TESTING PURPOSES
        self.data["test_price"] = self.data["Bid_c"]
        
        self.apply_strategies()
    
    def apply_strategies(self):
        # Apply strategies here
        self.data["Returns"] = np.log(self.data["test_price"]/self.data["test_price"].shift(1))
        self.data["Direction"] = np.where(self.data["Returns"] > 0, 1, 0)
        self.data.dropna(inplace=True)

        self.columns = ["Volume", "Direction"]

        self.split_data()
    
    def split_data(self):
        split = int(len(self.data) * 0.66)
        self.train = self.data.iloc[:split].copy()
        self.test = self.data.iloc[split:].copy()

        self.standardize_train_data()
        
    def standardize_train_data(self):
        self.mu, self.std = self.train.mean(), self.train.std()
        self.train_standardized = (self.train - self.mu) / self.std

        self.create_and_fit_model()
    
    def create_and_fit_model(self):
        set_seeds(100)
        self.model = create_model(hl=2, hu=100, dropout=True, input_dim=len(self.columns))
        self.model.fit(x = self.train_standardized[self.columns], y = self.train["Direction"], epochs = 2, verbose = False,
          validation_split = 0.2, shuffle = False, class_weight = cw(self.train))
        self.model.evaluate(self.train_standardized[self.columns], self.train["Direction"])
        self.prediction = self.model.predict(self.train_standardized[self.columns])

        self.forward_test()
    
    def forward_test(self):
        self.test_standardized = (self.test - self.train.mean()) / self.train.std()
        self.model.evaluate(self.test_standardized[self.columns], self.test["Direction"])
        self.test["Probability"] = self.model.predict(self.test_standardized[self.columns])
        self.test["Position"] = np.where(self.test["Probability"] < 0.50, -1, np.nan)
        self.test["Position"] = np.where(self.test["Probability"] > 0.50, 1, self.test["Position"])

        self.test["Strategy"] = self.test["Position"] * self.test["Returns"]
        self.test["cReturns"] = self.test["Returns"].cumsum().apply(np.exp)
        self.test["cStrategy"] = self.test["Strategy"].cumsum().apply(np.exp)

        print(self.test.tail(30))

        self.plot_results()
    
    def plot_results(self):
        self.test[["cReturns", "cStrategy"]].plot()
        plt.show()