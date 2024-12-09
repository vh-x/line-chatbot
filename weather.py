from typing import TypedDict
import requests
from urllib.parse import urlencode
from config import CWA_AUTH_KEY
from today import getToday

BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

cache = {}
last_updated = None


class WeatherResult(TypedDict):
    startTime: str
    endTime: str
    status: str


def get_weather(city: str) -> WeatherResult | None:
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
            weather = response["records"]["location"][0]["weatherElement"][0]["time"][0]
            if weather:
                startTime = weather.get("startTime", "")
                endTime = weather.get("endTime", "")
                status = weather.get("parameter", {}).get("parameterName", "")
                cache[city] = {
                    "startTime": startTime,
                    "endTime": endTime,
                    "status": status,
                }

        except Exception as e:
            print(e)
            return None

    return cache[city]
