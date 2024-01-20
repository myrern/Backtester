import Backtester as backtester
import json

# Define the file path
file_path = "tradeable_assets.json"

# Read the JSON file
with open(file_path, 'r') as f:
    tradeable_assets = json.load(f)

test_asset = tradeable_assets[0]

backtester = backtester.Backtester(test_asset)
backtester.run_backtest()