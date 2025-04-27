import os
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    QuickReply, QuickReplyButton, MessageAction,
    FlexSendMessage, BubbleContainer, BoxComponent,
    ButtonComponent, TextComponent, DatetimePickerAction
)
from dotenv import load_dotenv
import translation_manager
import conversation_manager
import calendar_manager
import reporting_manager

# Carregar variáveis de ambiente
load_dotenv()

# Criar a aplicação Flask
app = Flask(__name__)

# Configuração da API do LINE
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))
clinic_line_user_id = os.environ.get('CLINIC_LINE_USER_ID')

# Configurações da clínica
CLINIC_NAME = os.environ.get('CLINIC_NAME', 'Clínica Tanaka')
CLINIC_ADDRESS = os.environ.get('CLINIC_ADDRESS', 'Tóquio, Japão')
CLINIC_PHONE = os.environ.get('CLINIC_PHONE', '+81-XX-XXXX-XXXX')
CLINIC_EMAIL = os.environ.get('CLINIC_EMAIL', 'contato@clinicatanaka.com')

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
        # Obter a mensagem do usuário
        user_id = event.source.user_id
        user_message = event.message.text
        
        # Verificar se é a primeira mensagem do usuário
        if user_message.lower() in ['oi', 'olá', 'ola', 'hello', 'hi', 'こんにちは', 'konnichiwa']:
            # Criar botões de resposta rápida para seleção de idioma
            language_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="Português", text="Português")),
                    QuickReplyButton(action=MessageAction(label="日本語", text="日本語")),
                    QuickReplyButton(action=MessageAction(label="English", text="English"))
                ]
            )
            
            # Enviar mensagem com botões de resposta rápida
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Por favor, selecione seu idioma / 言語を選択してください / Please select your language",
                    quick_reply=language_quick_reply
                )
            )
            return
        
        # Verificar se o usuário está selecionando um idioma
        if user_message in ['Português', '日本語', 'English']:
            # Mapear a seleção para o código de idioma
            language_map = {
                'Português': 'pt',
                '日本語': 'ja',
                'English': 'en'
            }
            selected_language = language_map[user_message]
            
            # Salvar a preferência de idioma do usuário
            conversation_manager.set_user_language(user_id, selected_language)
            
            # Obter a mensagem de boas-vindas no idioma selecionado
            welcome_messages = {
                'pt': f"Bem-vindo à {CLINIC_NAME}! Como posso ajudar você hoje?",
                'ja': f"{CLINIC_NAME}へようこそ！今日はどのようにお手伝いできますか？",
                'en': f"Welcome to {CLINIC_NAME}! How can I help you today?"
            }
            
            # Criar botões de resposta rápida para opções iniciais
            options_messages = {
                'pt': ["Agendar consulta", "Informações da clínica", "Falar com atendente"],
                'ja': ["予約を取る", "クリニック情報", "スタッフと話す"],
                'en': ["Book appointment", "Clinic information", "Talk to staff"]
            }
            
            options_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label=options_messages[selected_language][0], text=options_messages[selected_language][0])),
                    QuickReplyButton(action=MessageAction(label=options_messages[selected_language][1], text=options_messages[selected_language][1])),
                    QuickReplyButton(action=MessageAction(label=options_messages[selected_language][2], text=options_messages[selected_language][2]))
                ]
            )
            
            # Enviar mensagem de boas-vindas com opções
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=welcome_messages[selected_language],
                    quick_reply=options_quick_reply
                )
            )
            return
        
        # Para outras mensagens, detectar idioma e processar normalmente
        detected_language = translation_manager.detect_language(user_message)
        
        # Verificar se o usuário quer agendar uma consulta
        appointment_keywords = {
            'pt': ['agendar', 'marcar', 'consulta', 'horário', 'disponível'],
            'ja': ['予約', '診察', '時間', '利用可能'],
            'en': ['book', 'appointment', 'schedule', 'available', 'time']
        }
        
        # Verificar se a mensagem contém palavras-chave de agendamento
        is_appointment_request = any(keyword in user_message.lower() for keyword in appointment_keywords.get(detected_language, []))
        
        if is_appointment_request or user_message in ["Agendar consulta", "予約を取る", "Book appointment"]:
            # Obter horários disponíveis
            available_slots = calendar_manager.get_available_slots()
            
            # Mensagens para diferentes idiomas
            date_selection_messages = {
                'pt': "Por favor, selecione uma data para sua consulta:",
                'ja': "診察の日付を選択してください：",
                'en': "Please select a date for your appointment:"
            }
            
            # Criar botões de resposta rápida para datas disponíveis
            date_buttons = []
            for date in available_slots.keys():
                date_buttons.append(
                    QuickReplyButton(action=MessageAction(label=date, text=f"Data: {date}"))
                )
            
            date_quick_reply = QuickReply(items=date_buttons[:13])  # Limite de 13 botões
            
            # Enviar mensagem com datas disponíveis
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=date_selection_messages.get(detected_language, date_selection_messages['en']),
                    quick_reply=date_quick_reply
                )
            )
            return
        
        # Verificar se o usuário está selecionando uma data
        if user_message.startswith("Data: "):
            selected_date = user_message.replace("Data: ", "")
            
            # Obter horários disponíveis para a data selecionada
            available_slots = calendar_manager.get_available_slots()
            if selected_date in available_slots:
                available_times = available_slots[selected_date]
                
                # Mensagens para diferentes idiomas
                time_selection_messages = {
                    'pt': f"Horários disponíveis para {selected_date}:",
                    'ja': f"{selected_date}の利用可能な時間：",
                    'en': f"Available times for {selected_date}:"
                }
                
                # Criar botões de resposta rápida para horários disponíveis
                time_buttons = []
                for time in available_times:
                    time_buttons.append(
                        QuickReplyButton(action=MessageAction(label=time, text=f"Horário: {time} - {selected_date}"))
                    )
                
                time_quick_reply = QuickReply(items=time_buttons[:13])  # Limite de 13 botões
                
                # Enviar mensagem com horários disponíveis
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=time_selection_messages.get(detected_language, time_selection_messages['en']),
                        quick_reply=time_quick_reply
                    )
                )
                return
        
        # Verificar se o usuário está selecionando um horário
        if user_message.startswith("Horário: "):
            # Extrair horário e data
            parts = user_message.replace("Horário: ", "").split(" - ")
            if len(parts) == 2:
                selected_time = parts[0]
                selected_date = parts[1]
                
                # Salvar o agendamento
                appointment_id = calendar_manager.create_appointment(user_id, selected_date, selected_time)
                
                # Mensagens de confirmação para diferentes idiomas
                confirmation_messages = {
                    'pt': f"Sua consulta foi agendada com sucesso para {selected_date} às {selected_time}. ID do agendamento: {appointment_id}",
                    'ja': f"予約は{selected_date}の{selected_time}に正常に予約されました。予約ID：{appointment_id}",
                    'en': f"Your appointment has been successfully scheduled for {selected_date} at {selected_time}. Appointment ID: {appointment_id}"
                }
                
                # Enviar mensagem de confirmação
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=confirmation_messages.get(detected_language, confirmation_messages['en']))
                )
                return
        
        # Para outras mensagens, processar normalmente
        response = conversation_manager.process_message(user_id, user_message, detected_language)
        
        # Enviar resposta ao usuário
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=response)
        )
    except Exception as e:
        app.logger.error(f"Error in handle_message: {str(e)}")
        # Enviar mensagem de erro genérica
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Desculpe, ocorreu um erro. Por favor, tente novamente mais tarde.")
            )
        except Exception as reply_error:
            app.logger.error(f"Error sending error message: {str(reply_error)}")

@app.route("/", methods=['GET'])
def health_check():
    return f'Chatbot LINE para {CLINIC_NAME} está funcionando!'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
