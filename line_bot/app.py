import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import conversation_manager
import translation_manager
import calendar_manager
import reporting_manager

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configuração da API do LINE
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
clinic_line_user_id = os.environ.get('CLINIC_LINE_USER_ID')

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

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # Obter a mensagem do usuário
    user_id = event.source.user_id
    user_message = event.message.text
    
    # Detectar idioma e traduzir se necessário
    detected_language = translation_manager.detect_language(user_message)
    
    # Processar a mensagem e obter resposta
    response = conversation_manager.process_message(user_id, user_message, detected_language)
    
    # Enviar resposta ao usuário
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )

@app.route("/", methods=['GET'])
def health_check():
    return 'Chatbot LINE para Clínica Tanaka está funcionando!'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000) )
    app.run(host="0.0.0.0", port=port)
