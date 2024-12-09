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
    city = message.replace("台", "臺")

    if "/" in message:
        try:
            birth_month, birth_day = map(int, message.split("/"))
            reply_message = get_results(birth_month, birth_day)
        except ValueError:
            reply_message = "請輸入正確的生日格式 (MM/DD)，例如 08/15"

    elif city in cities:
        reply_message = get_weather(city)

    elif any(
        keyword in message
        for keyword in ["運勢", "占卜", "天氣", "說明", "怎麼用", "什麼"]
    ):
        reply_message = "請輸入生日格式 (MM/DD，例如: 08/15) 來取得運勢占卜，或縣市名稱來查詢天氣，例如: 台北市"

    elif any(
        keyword in message for keyword in ["你好", "哈囉", "早安", "午安", "晚安"]
    ):
        reply_message = "嗨！你好，請問有什麼需要幫忙的嗎?"

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
