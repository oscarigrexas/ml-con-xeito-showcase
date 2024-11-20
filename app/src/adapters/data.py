import os
from datetime import date, datetime, timedelta

import openmeteo_requests
import pandas as pd
import pytz
import requests


def log_current_data(current_data: pd.DataFrame):
    print(current_data.head().to_json(orient="table"))
    r = requests.post(
        f"{os.environ['DATA_COLLECTOR_URI']}/current_data",
        data=current_data.to_json(orient="table"),
    )
    if r.status_code == 500:
        raise Exception("Data collection error!")


def get_recent_data():
    # Setup the Open-Meteo API client with cache and retry on error
    openmeteo = openmeteo_requests.Client(session=None)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "hourly": [
            "carbon_monoxide",
            "nitrogen_dioxide",
            "sulphur_dioxide",
            "ozone",
            "dust",
            "european_aqi",
        ],
        "start_date": (date.today() - timedelta(days=1)).isoformat(),
        "end_date": date.today().isoformat(),
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_carbon_monoxide = hourly.Variables(0).ValuesAsNumpy()
    hourly_nitrogen_dioxide = hourly.Variables(1).ValuesAsNumpy()
    hourly_sulphur_dioxide = hourly.Variables(2).ValuesAsNumpy()
    hourly_ozone = hourly.Variables(3).ValuesAsNumpy()
    hourly_dust = hourly.Variables(4).ValuesAsNumpy()
    hourly_european_aqi = hourly.Variables(5).ValuesAsNumpy()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        )
    }
    hourly_data["carbon_monoxide"] = hourly_carbon_monoxide
    hourly_data["nitrogen_dioxide"] = hourly_nitrogen_dioxide
    hourly_data["sulphur_dioxide"] = hourly_sulphur_dioxide
    hourly_data["ozone"] = hourly_ozone
    hourly_data["dust"] = hourly_dust
    hourly_data["european_aqi"] = hourly_european_aqi

    hourly_dataframe = pd.DataFrame(data=hourly_data)

    hourly_dataframe = hourly_dataframe.set_index("date", drop=True)

    return hourly_dataframe[
        hourly_dataframe.index <= datetime.now(tz=pytz.timezone("CET"))
    ]


def get_current_data(recent_hourly_dataframe):
    return recent_hourly_dataframe.iloc[-1]
