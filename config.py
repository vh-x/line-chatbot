import os
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
CWA_AUTH_KEY = os.environ.get("CWA_AUTH_KEY")
