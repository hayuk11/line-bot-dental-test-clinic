import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv() 

# Criar a aplicação Flask
app = Flask(__name__)

# Configuração da API do LINE
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

@app.route("/webhook", methods=['POST'])
def callback():
    # Obter a assinatura do cabeçalho X-Line-Signature
    signature = request.headers['X-Line-Signature']

    # Obter o corpo da requisição
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # Verificar a assinatura
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        # Não propagar o erro para garantir que o webhook retorne 200 OK
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        # Resposta simples para teste
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Olá! Recebi sua mensagem. Estamos em fase de teste.")
        )
    except Exception as e:
        app.logger.error(f"Error sending response: {str(e)}")

@app.route("/", methods=['GET'])
def health_check():
    return 'Chatbot LINE para Clínica Tanaka está funcionando!'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
