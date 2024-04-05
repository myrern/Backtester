from iterativeBacktesting import IterativeBase as IB
from TechnicalIndicators import TechnicalIndicators
import numpy as np

class IterativeBactest(IB.IterativeBase):

    # helper method
    def go_long(self, bar, units = None, amount = None):
        if self.position == -1:
            self.buy_asset(bar, units = -self.units) # if short position, go neutral first
        if units:
            self.buy_asset(bar, units = units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.buy_asset(bar, amount = amount) # go long

    # helper method
    def go_short(self, bar, units = None, amount = None):
        if self.position == 1:
            self.sell_asset(bar, units = self.units) # if long position, go neutral first
        if units:
            self.sell_asset(bar, units = units)
        elif amount:
            if amount == "all":
                amount = self.current_balance
            self.sell_asset(bar, amount = amount) # go short
    
    def go_neutral(self, bar, position):
        self.close_position(bar, position)

    def test_IBS_strategy(self, ibs_low_threshold, ibs_high_threshold):
        strategy_name = "IBS_" + str(ibs_low_threshold) + "_" + str(ibs_high_threshold) + "_Iterative"

        technical_indicators = TechnicalIndicators(self.data)
        self.data["IBS"] = technical_indicators.IBS()

        # Printout for clarity
        stm = "Testing IBS strategy | IBS_Low = {} & IBS_High = {}".format(ibs_low_threshold, ibs_high_threshold)
        print("-" * 75)
        print(stm)
        print("-" * 75)

        self.position = 0  # Initial neutral position
        self.trades = 0  # No trades yet
        self.current_balance = self.initial_balance  # Reset initial capital

        self.data["Position" + strategy_name] = 0  # Start with no position
        self.data.dropna(inplace=True)  # Drop NA values

        # Initialize the position to neutral for all rows
        self.data["Position" + strategy_name] = 0  

        for candle in range(1, len(self.data) - 1):
            if self.data["IBS"].iloc[candle - 1] < ibs_low_threshold:
                if self.position in [0, -1]:
                    self.go_long(candle, amount="all")  # Go long
                    self.position = 1  # Update to long position
            elif self.data["IBS"].iloc[candle - 1] > ibs_high_threshold:
                if self.position in [1]:
                    self.go_neutral(candle, 1)
                    self.position = 0  # Update to neutral position

            # Update the position for each candle
            self.data.loc[self.data.index[candle -1 ], "Position" + strategy_name] = self.position

        self.close_final_position(candle + 1)  # Close position at the last bar

        # Calculate strategy returns based on positions
        self.data["Strategy" + strategy_name] = self.data["Position" + strategy_name].shift(1) * self.data["Returns"]

        return self.data, strategy_name

    
    def test_sma_strategy(self, SMA_S, SMA_L, data):
        strategy_name = "SMA_Crossover_" + str(SMA_S) + "_" + str(SMA_L) + "_Iterative"
        
        technical_indicators = TechnicalIndicators(data)
        
        # nice printout
        stm = "Testing SMA strategy | SMA_S = {} & SMA_L = {}".format(SMA_S, SMA_L)
        print("-" * 75)
        print(stm)
        print("-" * 75)
        
        # reset 
        self.position = 0  # initial neutral position
        self.trades = 0  # no trades yet
        self.current_balance = self.initial_balance  # reset initial capital
        self.data = data.copy()
        
        # prepare data
        self.data["sma_s"] = technical_indicators.SMA(period = SMA_S, column = "mid_c")
        self.data["sma_l"] = technical_indicators.SMA(period = SMA_L, column = "mid_c")
        self.data.dropna(inplace = True)

        self.data["Position" + strategy_name] = 0  # start with no position

        positions = [0]  # start with a default position

        for candle in range(1, len(self.data)-1): # all bars (except the last bar)
            if self.data["sma_s"].iloc[candle -1 ] > self.data["sma_l"].iloc[candle -1]: # signal to go long
                if self.position in [0, -1]:
                    self.go_long(candle, amount = 1000) # go long with full amount
                    self.position = 1  # long position
            elif self.data["sma_s"].iloc[candle-1] < self.data["sma_l"].iloc[candle-1]: # signal to go short
                if self.position in [0, 1]:
                    self.go_short(candle, amount = 1000) # go short with full amount
                    self.position = -1 # short position

            # Save the current position for this candle
            positions.append(self.position)

        positions.append(0)  # end with a default position

        self.data["Position" + strategy_name] = positions  # assign positions list to new column after the loop
        self.data["Strategy" + strategy_name] = self.data["Position" + strategy_name].shift(1) * self.data["Returns"]
        self.close_position(candle+1) # close position at the last bar
        self.data["position"] = self.data["Position" + strategy_name]

        return self.data, strategy_name


        