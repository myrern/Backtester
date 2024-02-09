import numpy as np
from TechnicalIndicators import *

class Strategies:
    def __init__(self, data):
        self.data = data
        self.technical_indicators = TechnicalIndicators(self.data)

    def SMA_Crossover(self, short_window, long_window):
        strategy_name = "SMA_Crossover " + str(short_window) + "_" + str(long_window)

        self.data["sma_s"] = self.technical_indicators.SMA(period=50, column="mid_c")
        self.data["sma_l"] = self.technical_indicators.SMA(period=150, column="mid_c")

        self.data["Returns"] = np.log(self.data["mid_c"]/self.data["mid_c"].shift(1))

        self.data["Position"] = 0
        self.data["Position"] = np.where(self.data['sma_s'] > self.data['sma_l'], 1, -1)
        self.data["Strategy"] = self.data["Position"].shift(1) * self.data["Returns"]
        self.data.dropna(inplace=True)

        return self.data, strategy_name