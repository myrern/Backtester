##
# API to run the backtester
# Run the API at localhost with the following command: uvicorn main:app --reload
##
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import Backtester as backtester
import pandas as pd
import json

app = FastAPI()

@app.get("/run_smaCrossover")
def backtestSmaCrossover(sma_s: int = 50, sma_l: int = 150, optimize: bool = False, iterative: bool = False, initial_balance: int = 100000):
    backtester_instance = backtester.Backtester({"name": "EUR_USD", "type": "CURRENCY"}, iterative=iterative, optimize_parameters=optimize, initial_balance=initial_balance)
    data = backtester_instance.run_backtest()

    # Reset index to include it in the DataFrame as a column, you can give it a meaningful name
    data.reset_index(inplace=True, drop=False)

    # Now convert to JSON including the index (which is now a regular column)
    json_data = data.to_json(orient="records")
    
    # Convert the JSON string to a Python dict
    response_data = json.loads(json_data)

    # Return the data as a JSON response
    return JSONResponse(content=response_data)