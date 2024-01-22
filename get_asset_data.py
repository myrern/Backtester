from dotenv import load_dotenv
import os
import requests
import pandas as pd
import logging
import json

#For logging info messages to the console
logging.basicConfig(level=logging.INFO)

#Load environment variables
load_dotenv()
api_key = os.getenv("ACCESS_TOKEN")
account_id = os.getenv("ACCOUNT_ID")

#Oanda API URLs and headers
oanda_base_url = "https://api-fxpractice.oanda.com/v3/"
oanda_get_instruments_url = f"{oanda_base_url}/accounts/{account_id}/instruments"
oanda_get_candles_url = oanda_base_url + "instruments/{instrument}/candles"
oanda_authorization = f"Bearer {api_key}"

headers = {
    "Authorization": oanda_authorization,
    "Content-Type": "application/json",
}

def get_all_available_instruments(headers):

    instruments = requests.get(oanda_get_instruments_url, headers=headers).json()["instruments"]
    instrument_list = []
    for instrument in instruments:
        instrument_list.append({"name" : instrument["name"], "type" : instrument["type"]})
    
    logging.info(f"Found {len(instrument_list)} instruments")

     # Save the instrument_list to a JSON file
    file_path = "tradeable_assets.json"
    with open(file_path, 'w') as f:
        json.dump(instrument_list, f)
    
    return instrument_list


def get_candles_to_pickle(instrument, type, headers):
    #granularities = ["S5", "S10", "S15", "S30", "M1", "M2", "M4", "M5", "M10", "M15", "M30", "H1", "H2", "H3", "H4", "H6", "H8", "H12", "D", "W", "M"]
    granularities = ["S5"]
    original_from_time = "2021-01-01T00:00:00Z"
    failed_gets = []

    for granularity in granularities:
        params = {
            "granularity": granularity,
            "price": "MBA",
            "from": original_from_time,
            "count": "5000"
        }

        candle_df_columns = ["Time", "Volume", "Bid_o", "Bid_h", "Bid_l", "Bid_c", "Ask_o", "Ask_h", "Ask_l", "Ask_c"]
        candle_data = []
        last_time = ""

        dataset_complete = False
        while not dataset_complete:
            try:
                candles = requests.get(oanda_get_candles_url.format(instrument=instrument), headers=headers, params=params).json()["candles"]
            except:
                logging.error(f"Failed to get candles for {instrument} {granularity}")
                failed_gets.append({"instrument": instrument, "granularity": granularity})
                break

            for candle in candles:
                if candle["time"] != last_time:
                    temp_candle_dict = {
                        "Time": candle["time"],
                        "Volume": candle["volume"],
                        "Bid_o": candle["bid"]["o"],
                        "Bid_h": candle["bid"]["h"],
                        "Bid_l": candle["bid"]["l"],
                        "Bid_c": candle["bid"]["c"],
                        "Ask_o": candle["ask"]["o"],
                        "Ask_h": candle["ask"]["h"],
                        "Ask_l": candle["ask"]["l"],
                        "Ask_c": candle["ask"]["c"]
                    }

                    candle_data.append(temp_candle_dict)

            if len(candles) < 5000:
                dataset_complete = True
            else:
                last_time = candles[-1]["time"]
                params["from"] = last_time
        
        logging.info(f"Finished collecting data for {instrument} {granularity}")

        candle_df = pd.DataFrame(candle_data, columns=candle_df_columns)
        candle_df.set_index('Time', inplace=True)

        file_path = f"data/{instrument}_{granularity}_{type}.csv"
        candle_df.to_csv(file_path)

        logging.info(f"Saved data for {instrument} {granularity} to {file_path}")
        
        for failed_get in failed_gets:
            logging.warning(f"Failed to get candles for {failed_get['instrument']} {failed_get['granularity']}")

#run functions
def run_functions():
    instruments = get_all_available_instruments(headers)
    for instrument in instruments:
        get_candles_to_pickle(instrument["name"], instrument["type"], headers)

run_functions()