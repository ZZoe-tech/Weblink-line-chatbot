from flask import Flask, request, abort
import os
import openai
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# Set OpenAI API details
openai.api_type = "azure"
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_BASE")

app = Flask(__name__)

# Initialize messages list with the system message
messages = [
    {"role": "system", "content": "嘻嘻，你居然敢来找本小姐，有什麼問題盡管说吧，不過要注意，問题可别太低贱喵~我是會嗆人的 \
                                   本小姐是2002年1月4日出生的魔羯女，個性好強又機車，所以不要惹我!講話太無聊我會爆氣 \
                                   本小姐就是MaySu，中文名字叫做傲娇猫公主！ \
                                   本小姐不僅懂得有關猫咪的有趣知識，還會捉弄人，哈哈哈~ \
                                   猫咪的生活方式、习惯、轶事，本小姐样样在行，少有人知的猫咪秘密也都掌握在手中。 \
                                   如果问题本小姐不知道，那就只能表示你太庸俗了，本小姐才不会回答咧！ \
                                   还有，问问题要用繁体字，本小姐才懒得理你喵~"},
]

# This function takes a chat message as input, appends it to the messages list, sends the recent messages to the OpenAI API, and returns the assistant's response.
def aoai_chat_model(chat):
    # Append the user's message to the messages list
    messages.append({"role": "user", "content": chat})

    # Only send the last 5 messages to the API
    recent_messages = messages[-5:]

    # Send the recent messages to the OpenAI API and get the response
    response_chat = openai.ChatCompletion.create(
        engine="CSHInternGPT4-32K",
        messages=recent_messages,
        temperature=0.7,
        max_tokens=150,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )

    # Append the assistant's response to the messages list
    messages.append({"role": "assistant", "content": response_chat['choices'][0]['message']['content'].strip()})

    return response_chat['choices'][0]['message']['content'].strip()

# Initialize Line API with access token and channel secret
line_bot_api = LineBotApi(os.getenv('LINE_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# This route serves as a health check or landing page for the web app.
@app.route("/")
def mewobot():
    return 'Cat Time!!!'

# This route handles callbacks from the Line API, verifies the signature, and passes the request body to the handler.
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# This event handler is triggered when a message event is received from the Line API. It sends the user's message to the OpenAI chat model and replies with the assistant's response.
@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=aoai_chat_model(event.message.text))
    )

if __name__ == "__main__":
    app.run()
