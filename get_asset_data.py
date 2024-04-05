# from dotenv import load_dotenv
import json
import logging
import os

import pandas as pd
import requests

api_key = "355e3f854bfe5cd14c1ae71e71cb723e-b1bdecc6d4a9ac5023b66104c9f48863"
account_id = "101-004-25172303-001"


# For logging info messages to the console
logging.basicConfig(level=logging.INFO)

# Load environment variables
# load_dotenv()
# api_key = os.getenv("ACCESS_TOKEN")
# account_id = os.getenv("ACCOUNT_ID")

# Oanda API URLs and headers
oanda_base_url = "https://api-fxpractice.oanda.com/v3/"
oanda_get_instruments_url = f"{oanda_base_url}/accounts/{account_id}/instruments"
oanda_get_candles_url = oanda_base_url + "instruments/{instrument}/candles"
oanda_authorization = f"Bearer {api_key}"

headers = {
    "Authorization": oanda_authorization,
    "Content-Type": "application/json",
}


def get_all_available_instruments(headers):

    instruments = requests.get(oanda_get_instruments_url, headers=headers).json()[
        "instruments"
    ]
    instrument_list = []
    for instrument in instruments:
        instrument_list.append({"name": instrument["name"],
                                "type": instrument["type"],
                                "pipLocation": instrument["pipLocation"], 
                                "PriceDesimals": instrument["displayPrecision"], # number of decimal places in the price
                                "tradeSizeDesimals": instrument["tradeUnitsPrecision"], # number of decimal places in the trade size
                                "minimumTradeSize": instrument["minimumTradeSize"],
                                "financing": instrument["financing"]["longRate"],
                                "marginRate": instrument["marginRate"],
                                "financing": {"longRate": instrument["financing"]["longRate"], 
                                              "shortRate": instrument["financing"]["shortRate"]}})

    logging.info(f"Found {len(instrument_list)} instruments")

    # Save the instrument_list to a JSON file
    file_path = "tradeable_assets.json"
    with open(file_path, "w") as f:
        json.dump(instrument_list, f, indent=4)

    return instrument_list


def get_candles_to_pickle(instrument, type, headers):
    # granularities = ["S5", "S10", "S15", "S30", "M1", "M2", "M4", "M5", "M10", "M15", "M30", "H1", "H2", "H3", "H4", "H6", "H8", "H12", "D", "W", "M"]
    granularities = ["D"]

    original_from_time = "2000-01-01T00:00:00Z"

    failed_gets = []

    for granularity in granularities:
        params = {
            "granularity": granularity,
            "price": "MBA",
            "from": original_from_time,
            "count": "5000",
        }

        candle_df_columns = [
            "time",
            "volume",
            "bid_o",
            "bid_h",
            "bid_l",
            "bid_c",
            "ask_o",
            "ask_h",
            "ask_l",
            "ask_c",
            "mid_o",
            "mid_h",
            "mid_l",
            "mid_c",
        ]
        candle_data = []
        last_time = ""

        dataset_complete = False
        while not dataset_complete:
            try:
                candles = requests.get(
                    oanda_get_candles_url.format(instrument=instrument),
                    headers=headers,
                    params=params,
                ).json()["candles"]
            except:
                logging.error(f"Failed to get candles for {instrument} {granularity}")
                failed_gets.append(
                    {"instrument": instrument, "granularity": granularity}
                )
                break

            for candle in candles:
                if candle["time"] != last_time:
                    temp_candle_dict = {
                        "time": candle["time"],
                        "volume": candle["volume"],
                        "bid_o": candle["bid"]["o"],
                        "bid_h": candle["bid"]["h"],
                        "bid_l": candle["bid"]["l"],
                        "bid_c": candle["bid"]["c"],
                        "ask_o": candle["ask"]["o"],
                        "ask_h": candle["ask"]["h"],
                        "ask_l": candle["ask"]["l"],
                        "ask_c": candle["ask"]["c"],
                        "mid_o": candle["mid"]["o"],
                        "mid_h": candle["mid"]["h"],
                        "mid_l": candle["mid"]["l"],
                        "mid_c": candle["mid"]["c"],
                    }

                    candle_data.append(temp_candle_dict)

            if len(candles) < 5000:
                dataset_complete = True
            else:
                last_time = candles[-1]["time"]
                params["from"] = last_time

        logging.info(f"Finished collecting data for {instrument} {granularity}")

        candle_df = pd.DataFrame(candle_data, columns=candle_df_columns)
        candle_df.set_index("time", inplace=True)

        file_path = f"data/{instrument}_{granularity}_{type}.csv"

        dir_name = os.path.dirname('data/') # have to create the directory if it doesn't exist
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        candle_df.to_csv(file_path)

        logging.info(f"Saved data for {instrument} {granularity} to {file_path}")

        for failed_get in failed_gets:
            logging.warning(
                f"Failed to get candles for {failed_get['instrument']} {failed_get['granularity']}"
            )


# run functions
def run_functions():
    instruments = get_all_available_instruments(headers)
    # for instrument in instruments:
    #   get_candles_to_pickle(instrument["name"], instrument["type"], headers)

    get_candles_to_pickle("NAS100_USD", "CFD", headers)


run_functions()
