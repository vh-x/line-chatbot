import requests
from urllib.parse import urlencode

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from cities import CITIES
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from weather import get_weather

app = FastAPI()

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.get("/")
async def root():
    return "ok"


@app.post("/callback")
async def callback(request: Request):
    # Get X-Line-Signature header value
    signature = request.headers.get("X-Line-Signature")

    if not signature:
        raise HTTPException(status_code=400, detail="Missing X-Line-Signature header")

    # Get request body as text
    body = await request.body()
    body_text = body.decode("utf-8")

    # Handle webhook body
    try:
        handler.handle(body_text, signature)
    except InvalidSignatureError:
        raise HTTPException(
            status_code=400,
            detail="Invalid signature. Please check your channel access token/channel secret.",
        )

    return JSONResponse(content={"status": "OK"})


memory = {}


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    message = event.message.text
    userId = event.source.user_id if event.source.user_id else None
    reply_message = ""
    if message in CITIES:
        reply_message = f"{message} 是個好地方"
        weather = get_weather(message)
        if weather:
            startTime = weather.get("startTime", "")
            endTime = weather.get("endTime", "")
            status = weather.get("status", "")
            reply_message = f"{message} 在 {startTime} 至 {endTime} 的天氣為 {status}"

    if userId in memory:
        memory[userId] += 1
    else:
        memory[userId] = 1

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                notificationDisabled=True,
                replyToken=event.reply_token,
                messages=[
                    TextMessage(text=reply_message if reply_message else message)
                ],
            )
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
