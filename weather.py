from typing import TypedDict
import requests
from urllib.parse import urlencode
from config import CWA_AUTH_KEY
from today import getToday

BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

cache = {}
last_updated = None


def get_weather(city: str) -> str:
    global cache, last_updated

    today = getToday()

    if last_updated != today:
        cache.clear()
        last_updated = today

    if city not in cache:
        encoeded_params = urlencode(
            {
                "Authorization": CWA_AUTH_KEY,
                "elementName": "Wx",
                "locationName": city,
            }
        )
        url = f"{ BASE_URL }?{ encoeded_params }"

        try:
            print(f"fetching weather data from { url }")
            response = requests.get(url).json()
            weather_records = response["records"]["location"][0]["weatherElement"][0][
                "time"
            ]
            summary = f"以下是{ city }的天氣預報:\n\n"
            for data in weather_records:
                startTime = data.get("startTime", "")
                endTime = data.get("endTime", "")
                status = data.get("parameter", {}).get("parameterName", "")
                summary += f"{ startTime }~\n{ endTime }:\n天氣: { status }\n\n"

            cache[city] = summary

        except Exception as e:
            print(e)
            return "無法取得天氣資料"

    return cache[city]
