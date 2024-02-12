import numpy as np

from TechnicalIndicators import *


class Strategies:
    def __init__(self, data):
        self.data = data
        self.technical_indicators = TechnicalIndicators(self.data)

    def SMA_Crossover(self, short_window, long_window, test_data):
        strategy_name = "SMA_Crossover_" + str(short_window) + "_" + str(long_window)

        test_data["sma_s"] = self.technical_indicators.SMA(period=50, column="mid_c")
        test_data["sma_l"] = self.technical_indicators.SMA(period=150, column="mid_c")

        test_data["Position" + strategy_name] = 0
        test_data["Position" + strategy_name] = np.where(
            test_data["sma_s"] > test_data["sma_l"], 1, -1
        )
        test_data["Strategy" + strategy_name] = (
            test_data["Position" + strategy_name].shift(1) * test_data["Returns"]
        )
        test_data.dropna(inplace=True)

        cum_returns = test_data["Strategy" + strategy_name].cumsum().apply(np.exp)
        # get last value of cum_returns

        try:
            x = cum_returns.iloc[-1]
        except:
            return 0, test_data, strategy_name

        return cum_returns.iloc[-1], test_data, strategy_name

    def optimize_SMA_Crossover(self):
        start_sma_s = 1
        start_sma_l = 1

        test_data = self.data.copy()
        best_result = {"sma_s": 0, "sma_l": 0, "result": 0}

        for i in range(start_sma_l, 400, 10):
            for x in range(start_sma_s, 400, 10):
                result, df, strategy_name = self.SMA_Crossover(i, x, test_data)
                if result > best_result["result"]:
                    best_result["sma_s"] = x
                    best_result["sma_l"] = i
                    best_result["result"] = result

        best_return, df, strategy_name = self.SMA_Crossover(
            best_result["sma_l"], best_result["sma_s"], test_data
        )

        return df, strategy_name

    # momentum strategy rate of change
    def ROC(self, period):
        strategy_name = "ROC " + str(period)

        self.data["roc"] = self.technical_indicators.ROC(period=period, column="mid_c")

        self.data["Position" + strategy_name] = 0
        self.data["Position" + strategy_name] = np.where(self.data["roc"] > 0, 1, -1)
        self.data["Strategy" + strategy_name] = (
            self.data["Position" + strategy_name].shift(1) * self.data["Returns"]
        )
        self.data.dropna(inplace=True)

        return self.data, strategy_name
