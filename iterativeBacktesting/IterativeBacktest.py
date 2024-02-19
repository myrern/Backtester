from iterativeBacktesting import IterativeBase as IB
from TechnicalIndicators import TechnicalIndicators

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

        return self.data, strategy_name