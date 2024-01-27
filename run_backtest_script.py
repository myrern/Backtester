import Backtester as backtester
import json

# Define the file path
file_path = "tradeable_assets.json"

# Read the JSON file
with open(file_path, 'r') as f:
    tradeable_assets = json.load(f)



backtester = backtester.Backtester({"name": "EUR_USD", "type": "CURRENCY"})
backtester.run_backtest()