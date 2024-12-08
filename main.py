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

from cities import cities
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from horoscope import get_results
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
    message: str = event.message.text
    reply_message = ""

    if "/" in message:
        try:
            birth_month, birth_day = map(int, message.split("/"))
            reply_message = get_results(birth_month, birth_day)
        except ValueError:
            reply_message = "請輸入正確的生日格式 (MM/DD)，例如 08/15"

    city = message.replace("台", "臺")
    if city in cities:
        weather = get_weather(city)
        if weather:
            startTime = weather.get("startTime", "")
            endTime = weather.get("endTime", "")
            status = weather.get("status", "")
            reply_message = (
                f"{city} 在\n" f"從{startTime}\n" f"至 {endTime}\n" f"天氣為 {status}"
            )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                notificationDisabled=True,
                replyToken=f"{ event.reply_token }",
                messages=[
                    TextMessage(
                        text=reply_message if reply_message else f"{ message }?",
                        quickReply=None,
                        quoteToken=None,
                    )
                ],
            )
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
