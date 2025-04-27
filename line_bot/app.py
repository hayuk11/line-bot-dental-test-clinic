import os
import json
import random
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

# Dicionário para armazenar dados temporários da sessão (não persistente)
session_data = {}

# Simulação de horários disponíveis (em produção, use calendar_manager)
available_slots = {
    "27/04/2025": ["09:00", "10:00", "11:00", "14:00", "15:00"],
    "28/04/2025": ["09:30", "10:30", "14:30", "15:30", "16:30"],
    "29/04/2025": ["08:00", "09:00", "10:00", "11:00", "13:00", "14:00"],
    "30/04/2025": ["10:00", "11:00", "15:00", "16:00", "17:00"]
}

# Função para gerar ID de agendamento
def create_appointment_id(user_id, date, time):
    # Gera um ID único para o agendamento
    random_part = ''.join(random.choices('0123456789ABCDEF', k=4))
    date_part = date.replace('/', '')
    time_part = time.replace(':', '')
    return f"APT-{random_part}-{date_part}-{time_part}"

# Função para obter horários disponíveis
def get_available_slots():
    return available_slots

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
        # Obter a mensagem do usuário e ID
        user_id = event.source.user_id
        user_message = event.message.text
        
        # Inicializar dados da sessão se necessário
        if user_id not in session_data:
            session_data[user_id] = {
                'current_language': None,
                'current_step': 'initial',
                'appointment_data': {}
            }
        
        # Verificar se é uma mensagem inicial ou de saudação
        greetings = ['oi', 'olá', 'ola', 'hello', 'hi', 'こんにちは', 'konnichiwa', 'bom dia', 'boa tarde', 'boa noite']
        if user_message.lower() in greetings or session_data[user_id]['current_step'] == 'initial':
            # Resetar o passo atual para inicial
            session_data[user_id]['current_step'] = 'language_selection'
            
            # Criar botões de resposta rápida para seleção de idioma (ordem: japonês, português, inglês)
            language_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="🇯🇵 日本語", text="日本語")),
                    QuickReplyButton(action=MessageAction(label="🇧🇷 Português", text="Português")),
                    QuickReplyButton(action=MessageAction(label="🇺🇸 English", text="English")),
                    QuickReplyButton(action=MessageAction(label="🌐 Others", text="Others"))
                ]
            )
            
            # Enviar mensagem com botões de resposta rápida (ordem: japonês, português, inglês)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="言語を選択 / Selecione idioma / Select language",
                    quick_reply=language_quick_reply
                )
            )
            return
        
        # Verificar se o usuário está solicitando outro idioma
        if user_message == "Others":
            session_data[user_id]['current_step'] = 'awaiting_custom_language'
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Type your language name")
            )
            return
        
        # Verificar se o usuário está informando um idioma personalizado
        if session_data[user_id]['current_step'] == 'awaiting_custom_language':
            # Verificar se o idioma digitado é um dos idiomas suportados
            language_map = {
                'português': 'pt',
                'portugues': 'pt',
                'portuguese': 'pt',
                'brazil': 'pt',
                'brasil': 'pt',
                '日本語': 'ja',
                'japonês': 'ja',
                'japones': 'ja',
                'japanese': 'ja',
                'japan': 'ja',
                'japão': 'ja',
                'japao': 'ja',
                'english': 'en',
                'inglês': 'en',
                'ingles': 'en',
                'england': 'en',
                'usa': 'en',
                'eua': 'en'
            }
            
            # Converter para minúsculas para comparação
            user_language = user_message.lower()
            
            # Verificar se o idioma digitado é um dos idiomas suportados
            if user_language in language_map:
                selected_language = language_map[user_language]
            else:
                # Para idiomas não suportados, usar inglês como padrão
                selected_language = 'en'
            
            # Armazenar o idioma selecionado na sessão atual
            session_data[user_id]['current_language'] = selected_language
            session_data[user_id]['current_step'] = 'main_menu'
            
            # Mostrar menu principal no idioma selecionado
            show_main_menu(event, user_id)
            return
        
        # Verificar se o usuário está selecionando um idioma padrão
        if user_message in ['Português', '日本語', 'English']:
            # Mapear a seleção para o código de idioma
            language_map = {
                'Português': 'pt',
                '日本語': 'ja',
                'English': 'en'
            }
            selected_language = language_map[user_message]
            
            # Armazenar o idioma selecionado na sessão atual
            session_data[user_id]['current_language'] = selected_language
            session_data[user_id]['current_step'] = 'main_menu'
            
            # Mostrar menu principal no idioma selecionado
            show_main_menu(event, user_id)
            return
        
        # Obter o idioma atual da sessão
        current_language = session_data[user_id]['current_language']
        if not current_language:
            # Se não houver idioma definido, voltar para a seleção de idioma
            session_data[user_id]['current_step'] = 'language_selection'
            
            # Criar botões de resposta rápida para seleção de idioma (ordem: japonês, português, inglês)
            language_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="🇯🇵 日本語", text="日本語")),
                    QuickReplyButton(action=MessageAction(label="🇧🇷 Português", text="Português")),
                    QuickReplyButton(action=MessageAction(label="🇺🇸 English", text="English")),
                    QuickReplyButton(action=MessageAction(label="🌐 Others", text="Others"))
                ]
            )
            
            # Enviar mensagem com botões de resposta rápida (ordem: japonês, português, inglês)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="言語を選択 / Selecione idioma / Select language",
                    quick_reply=language_quick_reply
                )
            )
            return
        
        # Verificar se o usuário quer agendar uma consulta
        appointment_messages = {
            'pt': ["Agendar consulta", "agendar", "marcar", "consulta", "horário"],
            'ja': ["予約を取る", "予約", "診察", "時間"],
            'en': ["Book appointment", "book", "appointment", "schedule", "time"]
        }
        
        # Verificar se a mensagem contém palavras-chave de agendamento
        is_appointment_request = False
        for keyword in appointment_messages.get(current_language, []):
            if keyword.lower() in user_message.lower():
                is_appointment_request = True
                break
        
        if is_appointment_request or session_data[user_id]['current_step'] == 'appointment_date':
            # Atualizar o passo atual
            session_data[user_id]['current_step'] = 'appointment_date'
            
            # Obter horários disponíveis
            slots = get_available_slots()
            
            # Mensagens para diferentes idiomas
            date_selection_messages = {
                'pt': "Selecione uma data:",
                'ja': "日付を選択:",
                'en': "Select a date:"
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
                    text=date_selection_messages.get(current_language, date_selection_messages['en']),
                    quick_reply=date_quick_reply
                )
            )
            return
        
        # Verificar se o usuário está selecionando uma data
        if user_message.startswith("Data: "):
            selected_date = user_message.replace("Data: ", "")
            
            # Armazenar a data selecionada
            session_data[user_id]['appointment_data']['date'] = selected_date
            session_data[user_id]['current_step'] = 'appointment_time'
            
            # Obter horários disponíveis para a data selecionada
            slots = get_available_slots()
            if selected_date in slots:
                available_times = slots[selected_date]
                
                # Mensagens para diferentes idiomas
                time_selection_messages = {
                    'pt': f"Horários para {selected_date}:",
                    'ja': f"{selected_date}の時間:",
                    'en': f"Times for {selected_date}:"
                }
                
                # Criar botões de resposta rápida para horários disponíveis
                time_buttons = []
                for time in available_times:
                    time_buttons.append(
                        QuickReplyButton(action=MessageAction(label=f"🕒 {time}", text=f"Hora: {time}"))
                    )
                
                time_quick_reply = QuickReply(items=time_buttons[:13])  # Limite de 13 botões
                
                # Enviar mensagem com horários disponíveis
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=time_selection_messages.get(current_language, time_selection_messages['en']),
                        quick_reply=time_quick_reply
                    )
                )
                return
        
        # Verificar se o usuário está selecionando um horário
        if user_message.startswith("Hora: "):
            selected_time = user_message.replace("Hora: ", "")
            
            # Verificar se temos a data selecionada na sessão
            if 'appointment_data' in session_data[user_id] and 'date' in session_data[user_id]['appointment_data']:
                selected_date = session_data[user_id]['appointment_data']['date']
                
                # Armazenar o horário selecionado
                session_data[user_id]['appointment_data']['time'] = selected_time
                session_data[user_id]['current_step'] = 'appointment_confirmation'
                
                # Gerar ID de agendamento
                appointment_id = create_appointment_id(user_id, selected_date, selected_time)
                session_data[user_id]['appointment_data']['id'] = appointment_id
                
                # Mensagens de confirmação para diferentes idiomas
                confirmation_messages = {
                    'pt': f"✅ Consulta agendada: {selected_date} às {selected_time}.\nID: {appointment_id}\nDeseja fazer mais algo?",
                    'ja': f"✅ 予約完了: {selected_date}の{selected_time}\nID: {appointment_id}\n他に何かありますか？",
                    'en': f"✅ Appointment set: {selected_date} at {selected_time}.\nID: {appointment_id}\nAnything else?"
                }
                
                # Opções após confirmação
                options_labels = {
                    'pt': ["📋 Minhas consultas", "📅 Nova consulta", "ℹ️ Informações"],
                    'ja': ["📋 予約を見る", "📅 新しい予約", "ℹ️ 情報"],
                    'en': ["📋 My appointments", "📅 New appointment", "ℹ️ Information"]
                }
                
                options_values = {
                    'pt': ["Minhas consultas", "Nova consulta", "Informações"],
                    'ja': ["予約を見る", "新しい予約", "情報"],
                    'en': ["My appointments", "New appointment", "Information"]
                }
                
                options_quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][0], text=options_values[current_language][0])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][1], text=options_values[current_language][1])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][2], text=options_values[current_language][2]))
                    ]
                )
                
                # Enviar mensagem de confirmação com opções
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=confirmation_messages.get(current_language, confirmation_messages['en']),
                        quick_reply=options_quick_reply
                    )
                )
            else:
                # Se não tiver a data, pedir para selecionar a data primeiro
                session_data[user_id]['current_step'] = 'appointment_date'
                
                # Obter horários disponíveis
                slots = get_available_slots()
                
                # Mensagens para diferentes idiomas
                date_selection_messages = {
                    'pt': "Selecione uma data primeiro:",
                    'ja': "まず日付を選択してください:",
                    'en': "Select a date first:"
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
                        text=date_selection_messages.get(current_language, date_selection_messages['en']),
                        quick_reply=date_quick_reply
                    )
                )
            return
        
        # Verificar se o usuário quer informações da clínica
        info_messages = {
            'pt': ["Informações", "informação", "clínica", "endereço", "telefone", "email"],
            'ja': ["情報", "クリニック", "住所", "電話", "メール"],
            'en': ["Information", "info", "clinic", "address", "phone", "email"]
        }
        
        # Verificar se a mensagem contém palavras-chave de informações
        is_info_request = False
        for keyword in info_messages.get(current_language, []):
            if keyword.lower() in user_message.lower():
                is_info_request = True
                break
        
        if is_info_request:
            # Mensagens de informação para diferentes idiomas
            info_messages = {
                'pt': f"📍 {CLINIC_NAME}\n\n📍 Endereço: {CLINIC_ADDRESS}\n📞 Tel: {CLINIC_PHONE}\n📧 Email: {CLINIC_EMAIL}\n\n⏰ Horários:\nSeg-Sex: 9:00-18:00\nSáb: 9:00-13:00\nDom: Fechado",
                'ja': f"📍 {CLINIC_NAME}\n\n📍 住所: {CLINIC_ADDRESS}\n📞 電話: {CLINIC_PHONE}\n📧 メール: {CLINIC_EMAIL}\n\n⏰ 営業時間:\n月～金: 9:00-18:00\n土: 9:00-13:00\n日: 休診",
                'en': f"📍 {CLINIC_NAME}\n\n📍 Address: {CLINIC_ADDRESS}\n📞 Phone: {CLINIC_PHONE}\n📧 Email: {CLINIC_EMAIL}\n\n⏰ Hours:\nMon-Fri: 9:00-18:00\nSat: 9:00-13:00\nSun: Closed"
            }
            
            # Opções após informações
            options_labels = {
                'pt': ["📅 Agendar", "🗺️ Ver mapa", "📞 Ligar"],
                'ja': ["📅 予約する", "🗺️ 地図", "📞 電話する"],
                'en': ["📅 Book", "🗺️ Map", "📞 Call"]
            }
            
            options_values = {
                'pt': ["Agendar consulta", "Ver mapa", "Ligar"],
                'ja': ["予約する", "地図", "電話する"],
                'en': ["Book appointment", "Map", "Call"]
            }
            
            options_quick_reply = QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label=options_labels[current_language][0], text=options_values[current_language][0])),
                    QuickReplyButton(action=MessageAction(label=options_labels[current_language][1], text=options_values[current_language][1])),
                    QuickReplyButton(action=MessageAction(label=options_labels[current_language][2], text=options_values[current_language][2]))
                ]
            )
            
            # Enviar mensagem de informação com opções
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=info_messages.get(current_language, info_messages['en']),
                    quick_reply=options_quick_reply
                )
            )
            return
        
        # Verificar se o usuário quer ver suas consultas
        view_appointments_keywords = {
            'pt': ["Minhas consultas", "consultas"],
            'ja': ["予約を見る", "私の予約"],
            'en': ["My appointments", "appointments"]
        }
        
        # Verificar se a mensagem contém palavras-chave de visualização de consultas
        is_view_appointments_request = False
        for keyword in view_appointments_keywords.get(current_language, []):
            if keyword.lower() in user_message.lower():
                is_view_appointments_request = True
                break
        
        if is_view_appointments_request:
            # Verificar se o usuário tem consultas agendadas
            if 'appointment_data' in session_data[user_id] and 'id' in session_data[user_id]['appointment_data']:
                appointment = session_data[user_id]['appointment_data']
                
                # Mensagens para diferentes idiomas
                appointments_messages = {
                    'pt': f"📋 Suas consultas:\n\n📅 Data: {appointment['date']}\n🕒 Hora: {appointment['time']}\n🆔 ID: {appointment['id']}",
                    'ja': f"📋 あなたの予約:\n\n📅 日付: {appointment['date']}\n🕒 時間: {appointment['time']}\n🆔 ID: {appointment['id']}",
                    'en': f"📋 Your appointments:\n\n📅 Date: {appointment['date']}\n🕒 Time: {appointment['time']}\n🆔 ID: {appointment['id']}"
                }
                
                # Opções após visualização de consultas
                options_labels = {
                    'pt': ["📅 Nova consulta", "❌ Cancelar", "ℹ️ Informações"],
                    'ja': ["📅 新しい予約", "❌ キャンセル", "ℹ️ 情報"],
                    'en': ["📅 New appointment", "❌ Cancel", "ℹ️ Information"]
                }
                
                options_values = {
                    'pt': ["Nova consulta", "Cancelar", "Informações"],
                    'ja': ["新しい予約", "キャンセル", "情報"],
                    'en': ["New appointment", "Cancel", "Information"]
                }
                
                options_quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][0], text=options_values[current_language][0])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][1], text=options_values[current_language][1])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][2], text=options_values[current_language][2]))
                    ]
                )
                
                # Enviar mensagem com consultas agendadas
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=appointments_messages.get(current_language, appointments_messages['en']),
                        quick_reply=options_quick_reply
                    )
                )
            else:
                # Mensagens para diferentes idiomas quando não há consultas
                no_appointments_messages = {
                    'pt': "Você não tem consultas. Deseja agendar agora?",
                    'ja': "予約はありません。今予約しますか？",
                    'en': "No appointments. Book now?"
                }
                
                # Opções quando não há consultas
                options_labels = {
                    'pt': ["📅 Agendar", "ℹ️ Informações", "👨‍⚕️ Falar"],
                    'ja': ["📅 予約する", "ℹ️ 情報", "👨‍⚕️ 話す"],
                    'en': ["📅 Book", "ℹ️ Information", "👨‍⚕️ Talk"]
                }
                
                options_values = {
                    'pt': ["Agendar consulta", "Informações", "Falar"],
                    'ja': ["予約する", "情報", "話す"],
                    'en': ["Book appointment", "Information", "Talk"]
                }
                
                options_quick_reply = QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][0], text=options_values[current_language][0])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][1], text=options_values[current_language][1])),
                        QuickReplyButton(action=MessageAction(label=options_labels[current_language][2], text=options_values[current_language][2]))
                    ]
                )
                
                # Enviar mensagem quando não há consultas
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=no_appointments_messages.get(current_language, no_appointments_messages['en']),
                        quick_reply=options_quick_reply
                    )
                )
            return
        
        # Para mensagens não reconhecidas, mostrar o menu principal
        show_main_menu(event, user_id)
        
    except Exception as e:
        app.logger.error(f"Error in handle_message: {str(e)}")
        # Enviar mensagem de erro genérica
        error_messages = {
            'pt': "Erro. Tente novamente:",
            'ja': "エラー。もう一度お試しください:",
            'en': "Error. Try again:"
        }
        
        # Tentar obter o idioma atual, ou usar inglês como padrão
        current_language = 'en'
        if user_id in session_data and 'current_language' in session_data[user_id]:
            current_language = session_data[user_id]['current_language']
        
        # Criar botões de resposta rápida para seleção de idioma (ordem: japonês, português, inglês)
        language_quick_reply = QuickReply(
            items=[
                QuickReplyButton(action=MessageAction(label="🇯🇵 日本語", text="日本語")),
                QuickReplyButton(action=MessageAction(label="🇧🇷 Português", text="Português")),
                QuickReplyButton(action=MessageAction(label="🇺🇸 English", text="English")),
                QuickReplyButton(action=MessageAction(label="🌐 Others", text="Others"))
            ]
        )
        
        # Enviar mensagem de erro com opções de idioma
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text=error_messages.get(current_language, error_messages['en']),
                quick_reply=language_quick_reply
            )
        )

def show_main_menu(event, user_id):
    # Obter o idioma atual
    current_language = session_data[user_id]['current_language']
    
    # Mensagens de boas-vindas para diferentes idiomas
    welcome_messages = {
        'pt': f"Bem-vindo à {CLINIC_NAME}! Como posso ajudar?",
        'ja': f"{CLINIC_NAME}へようこそ！ご用件は？",
        'en': f"Welcome to {CLINIC_NAME}! How can I help?"
    }
    
    # Opções do menu principal
    options_labels = {
        'pt': ["📅 Agendar", "ℹ️ Informações", "👨‍⚕️ Falar"],
        'ja': ["📅 予約する", "ℹ️ 情報", "👨‍⚕️ 話す"],
        'en': ["📅 Book", "ℹ️ Information", "👨‍⚕️ Talk"]
    }
    
    options_values = {
        'pt': ["Agendar consulta", "Informações", "Falar"],
        'ja': ["予約する", "情報", "話す"],
        'en': ["Book appointment", "Information", "Talk"]
    }
    
    options_quick_reply = QuickReply(
        items=[
            QuickReplyButton(action=MessageAction(label=options_labels[current_language][0], text=options_values[current_language][0])),
            QuickReplyButton(action=MessageAction(label=options_labels[current_language][1], text=options_values[current_language][1])),
            QuickReplyButton(action=MessageAction(label=options_labels[current_language][2], text=options_values[current_language][2]))
        ]
    )
    
    # Enviar mensagem de boas-vindas com opções
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=welcome_messages.get(current_language, welcome_messages['en']),
            quick_reply=options_quick_reply
        )
    )

@app.route("/", methods=['GET'])
def health_check():
    return 'Chatbot LINE para Clínica Tanaka está funcionando!'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
