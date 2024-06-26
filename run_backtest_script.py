import json

import Backtester as backtester

# Define the file path and read the JSON file
file_path = "tradeable_assets.json"
with open(file_path, "r") as f:
    tradeable_assets = json.load(f)

# Create a Backtester instance and run the backtest
# Make sure to pass the asset details correctly from tradeable_assets if needed

backtester_instance = backtester.Backtester({"name": "NAS100_USD", "type": ""}, iterative=True, optimize_parameters=False, initial_balance=100000)

data = backtester_instance.run_backtest()