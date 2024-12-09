from datetime import datetime
from zoneinfo import ZoneInfo

timezone = ZoneInfo("Asia/Taipei")


def getToday():
    today = datetime.now(timezone).strftime("%Y-%m-%d")
    return today
