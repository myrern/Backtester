 def calcualte_factors(self):
        # Calculate Sharpe Ratio
        strategy_std = self.data["Strategy"].std()
        strategy_annualized_std = strategy_std * np.sqrt(252)
        strategy_sharpe = (
            self.data["Strategy"].mean() - 0.01
        ) / strategy_annualized_std

        # Calculate Maximum Drawdown
        strategy_cummax = self.data["Cumulative_Strategy"].cummax()
        strategy_drawdown = (
            self.data["Cumulative_Strategy"] - strategy_cummax
        ) / strategy_cummax
        strategy_max_drawdown = strategy_drawdown.min()

        # Calculate Win Rate

        print(f"Sharpe Ratio: {strategy_sharpe:.2f}")
        print(f"Maximum Drawdown: {strategy_max_drawdown:.2%}")

        # Calculate the change in position to identify trades
        self.data["Position_Change"] = self.data["Position"].diff()

        # Identify trade entry points
        trade_entries = self.data["Position_Change"].abs() > 0

        # Calculate the number of trades
        num_trades = trade_entries.sum()

        # Initialize variables to track the best and worst trade, and win/loss counts
        best_trade = None
        worst_trade = None
        wins = 0
        losses = 0
        current_trade_return = 0

        for i in range(len(self.data)):
            if trade_entries.iloc[i]:
                # At the start of a new trade, check if the previous trade was a win or loss
                if current_trade_return > 0:
                    wins += 1
                elif current_trade_return < 0:
                    losses += 1
                # Reset current trade return at the start of a new trade
                current_trade_return = 0
            current_trade_return += self.data["Returns"].iloc[i]
            # At the end of a trade or at the last available data point, evaluate the trade
            if trade_entries.iloc[i] or i == len(self.data) - 1:
                if best_trade is None or current_trade_return > best_trade:
                    best_trade = current_trade_return
                if worst_trade is None or current_trade_return < worst_trade:
                    worst_trade = current_trade_return
                # Evaluate the last trade in the dataset
                if i == len(self.data) - 1:
                    if current_trade_return > 0:
                        wins += 1
                    elif current_trade_return < 0:
                        losses += 1

        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0

        print(f"Number of Trades: {num_trades}")
        print(f"Best Trade: {best_trade}")
        print(f"Worst Trade: {worst_trade}")
        print(f"Win Rate: {win_rate:.2%}")

        summary = f"""
        Sharpe Ratio: {strategy_sharpe:.2f} 
        Maximum Drawdown: {strategy_max_drawdown:.2%} 
        Number of Trades: {num_trades} 
        Best Trade: {best_trade} 
        Worst Trade: {worst_trade} 
        Win Rate: {win_rate:.2%}
        """
