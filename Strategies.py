import numpy as np

from TechnicalIndicators import *


class Strategies:
    def __init__(self, data):
        self.data = data
        self.technical_indicators = TechnicalIndicators(self.data)

    def SMA_Crossover(self, short_window, long_window, test_data):
        strategy_name = "SMA_Crossover_" + str(short_window) + "_" + str(long_window) + "_Vectorized"

        test_data["sma_s"] = self.technical_indicators.SMA(period=short_window, column="mid_c")
        test_data["sma_l"] = self.technical_indicators.SMA(period=long_window, column="mid_c")

        test_data["Position" + strategy_name] = 0
        test_data["Position" + strategy_name] = np.where(
            test_data["sma_s"] > test_data["sma_l"], 1, -1
        )
        test_data["Strategy" + strategy_name] = (
            test_data["Position" + strategy_name].shift(1) * test_data["Returns"]
        )
        test_data.dropna(inplace=True)
        test_data["position"] = test_data["Position" + strategy_name]

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

        for i in range(start_sma_l, 300, 30):
            for x in range(start_sma_s, 300, 30):
                result, df, strategy_name = self.SMA_Crossover(i, x, test_data)
                if result > best_result["result"]:
                    best_result["sma_s"] = x
                    best_result["sma_l"] = i
                    best_result["result"] = result

        best_return, df, strategy_name = self.SMA_Crossover(
            best_result["sma_l"], best_result["sma_s"], test_data
        )

        return df, strategy_name
    
    def IBS_Strategy(self, ibs_low_threshold, ibs_high_threshold):
        strategy_name = "IBS" + "_Vectorized"
        # Calculate IBS
        self.data['IBS'] = (self.data['mid_c'] - self.data['mid_l']) / (self.data['mid_h'] - self.data['mid_l'])
        # Define Positions based on IBS thresholds
        self.data['Position' + strategy_name] = 0
        self.data['Position' + strategy_name] = np.where(self.data['IBS'] < ibs_low_threshold, 1,
                                                          np.where(self.data['IBS'] > ibs_high_threshold, -0.9, 0))
        # Calculate Strategy Returns
        self.data['Strategy' + strategy_name] = self.data['Position' + strategy_name].shift(1) * self.data['Returns']
        self.data.dropna(inplace=True)

        return self.data, strategy_name

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
