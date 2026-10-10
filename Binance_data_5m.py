import requests
import pandas as pd
import datetime
import pytz
from urllib.parse import urljoin


def get_binance_data(symbol="BTCTUSD", interval="5m", start_date=datetime.datetime(2023, 6, 25),
                     end_date=datetime.datetime(2023, 6, 28)):
    base_url = "https://api.binance.com"
    endpoint = "/api/v3/klines"
    time_zone = pytz.timezone("Asia/Kolkata")

    number, unit = interval[:-1], interval[-1]
    number = int(number) if number.isdigit() else float(number)
    unit = {"m": "minutes", "h": "hours", "s": "seconds"}[unit]
    interval_delta = datetime.timedelta(**{unit: number})
    limit = 1000

    btc_ohlcv = pd.DataFrame()
    current_start_time = start_date

    while current_start_time < end_date:
        startTime = int(time_zone.localize(current_start_time).timestamp() * 1000)
        minutes_to_add = interval_delta.total_seconds() / 60 * limit
        current_end_time = current_start_time + datetime.timedelta(minutes=minutes_to_add) - datetime.timedelta(
            milliseconds=1)
        current_end_time = min(current_end_time, end_date)
        endTime = int(time_zone.localize(current_end_time).timestamp() * 1000)

        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
            "startTime": startTime,
            "endTime": endTime
        }

        response = requests.get(urljoin(base_url, endpoint), params=params)
        if response.status_code == 200:
            data = response.json()
            if not data:
                break
            df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                                             "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                                             "Taker buy quote asset volume", "Ignore"])
            df = df.drop(["Close time", "Quote asset volume", "Number of trades", "Taker buy base asset volume",
                          "Taker buy quote asset volume", "Ignore"], axis=1)
            df["Open time"] = pd.to_datetime(df["Open time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(time_zone)
            df = df.set_index("Open time")
            btc_ohlcv = pd.concat([btc_ohlcv, df]) if not btc_ohlcv.empty else df
        else:
            print(f"Request failed with status code {response.status_code}")
            break

        current_start_time = current_end_time + datetime.timedelta(milliseconds=1)

    return btc_ohlcv
