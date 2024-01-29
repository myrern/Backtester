import Backtester as backtester
import json

# Define the file path and read the JSON file
file_path = "tradeable_assets.json"
with open(file_path, 'r') as f:
    tradeable_assets = json.load(f)

# Create a Backtester instance and run the backtest
backtester_instance = backtester.Backtester({"name": "EUR_USD", "type": "CURRENCY"})
backtester_instance.run_backtest()  