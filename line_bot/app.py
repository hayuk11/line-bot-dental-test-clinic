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

# Simulação de banco de dados de usuários (em produção, use Supabase ou outro banco)
user_data = {}

# Simulação de horários disponíveis (em produção, use calendar_manager)
available_slots = {
    "27/04/2025": ["09:00", "10:00", "11:00", "14:00", "15:00"],
    "28/04/2025": ["09:30", "10:30", "14:30", "15:30", "16:30"],
    "29/04/2025": ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00"],
    "30/04/2025": ["10:00", "11:00", "15:00", "16:00", "17:00"]
}

# Funções simplificadas dos módulos
def detect_language(text):
    # Simulação simples de detecção de idioma
    if any(word in text.lower() for word in ['olá', 'ola', 'bom dia', 'boa tarde', 'brasil']):
        return 'pt'
    elif any(word in text.lower() for word in ['こんにちは', 'おはよう', '予約', '日本']):
        return 'ja'
    else:
        return 'en'  # Default para inglês

def set_user_language(user_id, language):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['language'] = language

def get_user_language(user_id):
    if user_id in user_data and 'language' in user_data[user_id]:
        return user_data[user_id]['language']
    return 'en'  # Default para inglês

def get_available_slots():
    return available_slots

def create_appointment(user_id, date, time):
    # Simulação de criação de agendamento
    appointment_id = f"APT-{user_id[:6]}-{date.replace('/', '')}-{time.replace(':', '')}"
    if user_id not in user_data:
        user_data[user_id] = {}
    if 'appointments' not in user_data[user_id]:
        user_data[user_id]['appointments'] = []
    
    user_data[user_id]['appointments'].append({
        'id': appointment_id,
        'date': date,
        'time': time
    })
    
    return appointment_id

def process_message(user_id, message, language):
    # Processamento simples de mensagem baseado no idioma
    if language == 'pt':
        return f"Olá! Como posso ajudar você hoje na {CLINIC_NAME}?"
    elif language == 'ja':
        return f"こんにちは！{CLINIC_NAME}でどのようにお手伝いできますか？"
    elif language == 'en':
        return f"Hello! How can I help you today at {CLINIC_NAME}?"
    else:
        # Para outros idiomas, tentamos responder em inglês
        return f"Hello! How can I help you today at {CLINIC_NAME}?"

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
                    QuickReplyButton(action=MessageAction(label="🇧🇷 Português", text="Português")),
                    QuickReplyButton(action=MessageAction(label="🇯🇵 日本語", text="日本語")),
                    QuickReplyButton(action=MessageAction(label="🇺🇸 English", text="English")),
                    QuickReplyButton(action=MessageAction(label="🌐 Others", text="Other Language"))
                ]
            )
            
            # Enviar mensagem com botões de resposta rápida
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="Por favor, selecione seu idioma / 言語を選択してください / Please select your language / 🌐 Select your language",
                    quick_reply=language_quick_reply
                )
            )
            return
        
        # Verificar se o usuário está solicitando outro idioma
        if user_message == "Other Language":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Please type the name of your language (e.g., Español, Français, Deutsch, etc.)")
            )
            return
        
        # Verificar se o usuário está informando um idioma personalizado
        if user_id in user_data and user_data.get(user_id, {}).get('awaiting_language', False):
            # Armazenar o idioma personalizado
            set_user_language(user_id, 'other')
            user_data[user_id]['custom_language'] = user_message
            user_data[user_id]['awaiting_language'] = False
            
            # Enviar mensagem de boas-vindas em inglês (padrão para idiomas não suportados)
            welcome_message = f"Welcome to {CLINIC_NAME}! We'll try to assist you in English. How can we help you today?"
            
            # Criar botões de resposta rápida para opções iniciais
            options_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="📅 Book appointment", text="Book appointment")),
                    QuickReplyButton(action=MessageAction(label="ℹ️ Clinic information", text="Clinic information")),
                    QuickReplyButton(action=MessageAction(label="👨‍⚕️ Talk to staff", text="Talk to staff"))
                ]
            )
            
            # Enviar mensagem de boas-vindas com opções
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=welcome_message,
                    quick_reply=options_quick_reply
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
            set_user_language(user_id, selected_language)
            
            # Obter a mensagem de boas-vindas no idioma selecionado
            welcome_messages = {
                'pt': f"Bem-vindo à {CLINIC_NAME}! Como posso ajudar você hoje?",
                'ja': f"{CLINIC_NAME}へようこそ！今日はどのようにお手伝いできますか？",
                'en': f"Welcome to {CLINIC_NAME}! How can I help you today?"
            }
            
            # Criar botões de resposta rápida para opções iniciais
            options_labels = {
                'pt': ["📅 Agendar consulta", "ℹ️ Informações da clínica", "👨‍⚕️ Falar com atendente"],
                'ja': ["📅 予約を取る", "ℹ️ クリニック情報", "👨‍⚕️ スタッフと話す"],
                'en': ["📅 Book appointment", "ℹ️ Clinic information", "👨‍⚕️ Talk to staff"]
            }
            
            options_values = {
                'pt': ["Agendar consulta", "Informações da clínica", "Falar com atendente"],
                'ja': ["予約を取る", "クリニック情報", "スタッフと話す"],
                'en': ["Book appointment", "Clinic information", "Talk to staff"]
            }
            
            options_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label=options_labels[selected_language][0], text=options_values[selected_language][0])),
                    QuickReplyButton(action=MessageAction(label=options_labels[selected_language][1], text=options_values[selected_language][1])),
                    QuickReplyButton(action=MessageAction(label=options_labels[selected_language][2], text=options_values[selected_language][2]))
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
        
        # Para outras mensagens, detectar idioma
        detected_language = get_user_language(user_id)
        if not detected_language:
            detected_language = detect_language(user_message)
            set_user_language(user_id, detected_language)
        
        # Verificar se o usuário quer agendar uma consulta
        appointment_keywords = {
            'pt': ['agendar', 'marcar', 'consulta', 'horário', 'disponível'],
            'ja': ['予約', '診察', '時間', '利用可能'],
            'en': ['book', 'appointment', 'schedule', 'available', 'time']
        }
        
        # Verificar se a mensagem contém palavras-chave de agendamento
        is_appointment_request = False
        for lang, keywords in appointment_keywords.items():
            if any(keyword in user_message.lower() for keyword in keywords):
                is_appointment_request = True
                break
        
        appointment_messages = {
            'pt': ["Agendar consulta", "agendar consulta"],
            'ja': ["予約を取る", "予約"],
            'en': ["Book appointment", "book appointment"]
        }
        
        if is_appointment_request or any(msg in user_message for msg in appointment_messages.get(detected_language, [])):
            # Obter horários disponíveis
            slots = get_available_slots()
            
            # Mensagens para diferentes idiomas
            date_selection_messages = {
                'pt': "Por favor, selecione uma data para sua consulta:",
                'ja': "診察の日付を選択してください：",
                'en': "Please select a date for your appointment:"
            }
            
            # Criar botões de resposta rápida para datas disponíveis
            date_buttons = []
            for date in slots.keys():
                date_buttons.append(
                    QuickReplyButton(action=MessageAction(label=f"📆 {date}", text=f"Data: {date}"))
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
            slots = get_available_slots()
            if selected_date in slots:
                available_times = slots[selected_date]
                
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
                        QuickReplyButton(action=MessageAction(label=f"🕒 {time}", text=f"Horário: {time} - {selected_date}"))
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
                appointment_id = create_appointment(user_id, selected_date, selected_time)
                
                # Mensagens de confirmação para diferentes idiomas
                confirmation_messages = {
                    'pt': f"✅ Sua consulta foi agendada com sucesso para {selected_date} às {selected_time}.\n\nID do agendamento: {appointment_id}\n\nDeseja fazer mais alguma coisa?",
                    'ja': f"✅ 予約は{selected_date}の{selected_time}に正常に予約されました。\n\n予約ID：{appointment_id}\n\n他に何かお手伝いできることはありますか？",
                    'en': f"✅ Your appointment has been successfully scheduled for {selected_date} at {selected_time}.\n\nAppointment ID: {appointment_id}\n\nIs there anything else you would like to do?"
                }
                
                # Opções após confirmação
                options_labels = {
                    'pt': ["📋 Ver minhas consultas", "📅 Agendar outra consulta", "❌ Cancelar consulta"],
                    'ja': ["📋 予約を見る", "📅 別の予約を取る", "❌ 予約をキャンセルする"],
                    'en': ["📋 View my appointments", "📅 Book another appointment", "❌ Cancel appointment"]
                }
                
                options_values = {
                    'pt': ["Ver minhas consultas", "Agendar outra consulta", "Cancelar consulta"],
                    'ja': ["予約を見る", "別の予約を取る", "予約をキャンセルする"],
                    'en': ["View my appointments", "Book another appointment", "Cancel appointment"]
                }
                
                options_quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label=options_labels[detected_language][0], text=options_values[detected_language][0])),
                        QuickReplyButton(action=MessageAction(label=options_labels[detected_language][1], text=options_values[detected_language][1])),
                        QuickReplyButton(action=MessageAction(label=options_labels[detected_language][2], text=options_values[detected_language][2]))
                    ]
                )
                
                # Enviar mensagem de confirmação com opções
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=confirmation_messages.get(detected_language, confirmation_messages['en']),
                        quick_reply=options_quick_reply
                    )
                )
                return
        
        # Verificar se o usuário quer informações da clínica
        info_keywords = {
            'pt': ['informações', 'informação', 'clínica', 'endereço', 'telefone', 'email'],
            'ja': ['情報', 'クリニック', '住所', '電話', 'メール'],
            'en': ['information', 'info', 'clinic', 'address', 'phone', 'email']
        }
        
        info_messages = {
            'pt': ["Informações da clínica", "informações"],
            'ja': ["クリニック情報", "情報"],
            'en': ["Clinic information", "information"]
        }
        
        is_info_request = False
        for lang, keywords in info_keywords.items():
            if any(keyword in user_message.lower() for keyword in keywords):
                is_info_request = True
                break
        
        if is_info_request or any(msg in user_message for msg in info_messages.get(detected_language, [])):
            # Mensagens de informação para diferentes idiomas
            info_messages = {
                'pt': f"📍 **{CLINIC_NAME}**\n\n📍 Endereço: {CLINIC_ADDRESS}\n📞 Telefone: {CLINIC_PHONE}\n📧 Email: {CLINIC_EMAIL}\n\n⏰ Horário de funcionamento:\nSegunda a Sexta: 9:00 - 18:00\nSábado: 9:00 - 13:00\nDomingo: Fechado",
                'ja': f"📍 **{CLINIC_NAME}**\n\n📍 住所: {CLINIC_ADDRESS}\n📞 電話: {CLINIC_PHONE}\n📧 メール: {CLINIC_EMAIL}\n\n⏰ 営業時間:\n月曜日～金曜日: 9:00 - 18:00\n土曜日: 9:00 - 13:00\n日曜日: 休診",
                'en': f"📍 **{CLINIC_NAME}**\n\n📍 Address: {CLINIC_ADDRESS}\n📞 Phone: {CLINIC_PHONE}\n📧 Email: {CLINIC_EMAIL}\n\n⏰ Opening Hours:\nMonday to Friday: 9:00 - 18:00\nSaturday: 9:00 - 13:00\nSunday: Closed"
            }
            
            # Opções após informações
            options_labels = {
                'pt': ["📅 Agendar consulta", "🗺️ Ver mapa", "📞 Ligar para clínica"],
                'ja': ["📅 予約を取る", "🗺️ 地図を見る", "📞 クリニックに電話する"],
                'en': ["📅 Book appointment", "🗺️ View map", "📞 Call clinic"]
            }
            
            options_values = {
                'pt': ["Agendar consulta", "Ver mapa", "Ligar para clínica"],
                'ja': ["予約を取る", "地図を見る", "クリニックに電話する"],
                'en': ["Book appointment", "View map", "Call clinic"]
            }
            
            options_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label=options_labels[detected_language][0], text=options_values[detected_language][0])),
                    QuickReplyButton(action=MessageAction(label=options_labels[detected_language][1], text=options_values[detected_language][1])),
                    QuickReplyButton(action=MessageAction(label=options_labels[detected_language][2], text=options_values[detected_language][2]))
                ]
            )
            
            # Enviar mensagem de informação com opções
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=info_messages.get(detected_language, info_messages['en']),
                    quick_reply=options_quick_reply
                )
            )
            return
        
        # Para outras mensagens, processar normalmente
        response = process_message(user_id, user_message, detected_language)
        
        # Criar botões de resposta rápida para opções gerais
        options_labels = {
            'pt': ["📅 Agendar consulta", "ℹ️ Informações da clínica", "👨‍⚕️ Falar com atendente"],
            'ja': ["📅 予約を取る", "ℹ️ クリニック情報", "👨‍⚕️ スタッフと話す"],
            'en': ["📅 Book appointment", "ℹ️ Clinic information", "👨‍⚕️ Talk to staff"]
        }
        
        options_values = {
            'pt': ["Agendar consulta", "Informações da clínica", "Falar com atendente"],
            'ja': ["予約を取る", "クリニック情報", "スタッフと話す"],
            'en': ["Book appointment", "Clinic information", "Talk to staff"]
        }
        
        options_quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label=options_labels.get(detected_language, options_labels['en'])[0], text=options_values.get(detected_language, options_values['en'])[0])),
                QuickReplyButton(action=MessageAction(label=options_labels.get(detected_language, options_labels['en'])[1], text=options_values.get(detected_language, options_values['en'])[1])),
                QuickReplyButton(action=MessageAction(label=options_labels.get(detected_language, options_labels['en'])[2], text=options_values.get(detected_language, options_values['en'])[2]))
            ]
        )
        
        # Enviar resposta ao usuário com opções
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=response,
                quick_reply=options_quick_reply
            )
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
