import numpy as np


class SimpleBacktester:
    def __init__(self, df):
        self.df = df
        self.df['Mid_Close'] = (self.df['Bid_c'].astype(float) + self.df['Ask_c'].astype(float)) / 2
        self.df['Spread'] = self.df['Ask_c'].astype(float) - self.df['Bid_c'].astype(float)
        self.df['RSI'] = self.calculate_RSI()

    def calculate_RSI(self, period=14):
        delta = self.df['Mid_Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def backtest(self, rsi_buy=30, rsi_sell=70):
        self.df['Position'] = 0
        self.df['Position'] = np.where(self.df['RSI'] < rsi_buy, 1, 
                                       np.where(self.df['RSI'] > rsi_sell, -1, 0))

        self.df['Returns'] = self.df['Mid_Close'].pct_change()
        self.df['Strategy'] = self.df['Position'].shift(1) * self.df['Returns']
        self.df['Strategy'] -= np.where(self.df['Position'] != 0, self.df['Spread'], 0)

        total_return = self.df['Strategy'].cumsum().iloc[-1]
        print("Total Return: ", total_return)


backtester = SimpleBacktester(df)
backtester.backtest()