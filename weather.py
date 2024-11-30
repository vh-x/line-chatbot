from typing import TypedDict
import requests
from urllib.parse import urlencode
from config import CWA_AUTH_KEY

BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"


class WeatherResult(TypedDict):
    startTime: str
    endTime: str
    status: str


def get_weather(city: str) -> WeatherResult | None:
    encoeded_params = urlencode(
        {
            "Authorization": CWA_AUTH_KEY,
            "elementName": "Wx",
            "locationName": city,
        }
    )
    url = f"{ BASE_URL }?{ encoeded_params }"

    try:
        response = requests.get(url).json()
        weather = response["records"]["location"][0]["weatherElement"][0]["time"][0]
        if weather:
            startTime = weather.get("startTime", "")
            endTime = weather.get("endTime", "")
            status = weather.get("parameter", {}).get("parameterName", "")
            return {"startTime": startTime, "endTime": endTime, "status": status}
    except Exception as e:
        print(e)
        return None
