import pandas as pd
import numpy as np
import tabulate
import matplotlib.pyplot as plt


class StrategyAnalysis():
     
    def __init__(self, amount, data):
        self.data = data
        
    def calculate_max_drawdown(self):
        # Calculate the cumulative returns
        self.data['cumulative_returns'] = np.exp(self.data['Returns'].cumsum())
        
        # Calculate the running maximum
        self.data['running_max'] = self.data['cumulative_returns'].cummax()
        
        # Calculate the drawdown
        self.data['drawdown'] = (self.data['running_max'] - self.data['cumulative_returns']) / self.data['running_max']
        
        # Calculate the maximum drawdown
        max_drawdown = self.data['drawdown'].max()
        
        return max_drawdown
    


   