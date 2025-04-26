import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple

from translation_manager import TranslationManager

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ConversationManager:
    """
    Gerenciador de conversas para o chatbot LINE.
    Gerencia o fluxo de conversa, estados dos usuários e processamento de mensagens.
    """
    
    def __init__(self, supabase_manager, line_manager, translation_manager: Optional[TranslationManager] = None):
        """
        Inicializa o gerenciador de conversas.
        
        Args:
            supabase_manager: Instância do gerenciador do Supabase.
            line_manager: Instância do gerenciador do LINE.
            translation_manager: Instância do gerenciador de traduções.
        """
        self.supabase_manager = supabase_manager
        self.line_manager = line_manager
        self.translation_manager = translation_manager or TranslationManager()
        
        # Estados dos usuários
        self.user_states = {}
        
        # Comandos disponíveis
        self.commands = {
            "agendar": self.handle_appointment,
            "cancelar": self.handle_cancellation,
            "ajuda": self.handle_help,
            "idioma": self.handle_language_change,
            "meuid": self.handle_user_id,
            "falar": self.handle_talk_to_clinic
        }
        
        # Carregar estados dos usuários do banco de dados
        self._load_user_states()
    
    def _load_user_states(self):
        """
        Carrega os estados dos usuários do banco de dados.
        """
        try:
            # Obter estados dos usuários do Supabase
            result = self.supabase_manager.get_all_user_states()
            if result:
                for user_state in result:
                    line_user_id = user_state.get("line_user_id")
                    state_data = user_state.get("state_data")
                    if line_user_id and state_data:
                        self.user_states[line_user_id] = state_data
            logger.info(f"Carregados {len(self.user_states)} estados de usuários do banco de dados.")
        except Exception as e:
            logger.error(f"Erro ao carregar estados dos usuários: {str(e)}")
    
    def _save_user_state(self, line_user_id: str):
        """
        Salva o estado de um usuário no banco de dados.
        
        Args:
            line_user_id: ID do usuário no LINE.
        """
        try:
            if line_user_id in self.user_states:
                self.supabase_manager.update_user_state(line_user_id, self.user_states[line_user_id])
                logger.info(f"Estado do usuário {line_user_id} salvo no banco de dados.")
        except Exception as e:
            logger.error(f"Erro ao salvar estado do usuário {line_user_id}: {str(e)}")
    
    def get_user_state(self, line_user_id: str) -> Dict[str, Any]:
        """
        Obtém o estado atual de um usuário.
        
        Args:
            line_user_id: ID do usuário no LINE.
            
        Returns:
            Dicionário com o estado do usuário.
        """
        if line_user_id not in self.user_states:
            # Inicializar estado para novo usuário
            self.user_states[line_user_id] = {
                "language": "ja",  # Idioma padrão: japonês
                "current_flow": None,
                "appointment_step": None,
                "appointment_data": {},
                "is_new_user": True
            }
            self._save_user_state(line_user_id)
        
        return self.user_states[line_user_id]
    
    def update_user_state(self, line_user_id: str, updates: Dict[str, Any]):
        """
        Atualiza o estado de um usuário.
        
        Args:
            line_user_id: ID do usuário no LINE.
            updates: Dicionário com atualizações para o estado.
        """
        user_state = self.get_user_state(line_user_id)
        user_state.update(updates)
        self._save_user_state(line_user_id)
    
    def process_message(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Processa uma mensagem recebida de um usuário.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas como resposta.
        """
        user_state = self.get_user_state(line_user_id)
        
        # Verificar se é um novo usuário
        if user_state.get("is_new_user", True):
            # Enviar mensagem de boas-vindas e seleção de idioma
            self.update_user_state(line_user_id, {"is_new_user": False})
            return self._send_welcome_message(line_user_id)
        
        # Verificar se está em um fluxo específico
        current_flow = user_state.get("current_flow")
        if current_flow:
            # Continuar o fluxo atual
            if current_flow == "appointment":
                return self.handle_appointment(line_user_id, message)
            elif current_flow == "cancellation":
                return self.handle_cancellation(line_user_id, message)
            elif current_flow == "language_change":
                return self.handle_language_change(line_user_id, message)
            elif current_flow == "talk_to_clinic":
                return self.handle_talk_to_clinic(line_user_id, message)
        
        # Verificar se é um comando conhecido
        lower_message = message.lower().strip()
        
        # Detectar idioma da mensagem
        detected_language = self.translation_manager.detect_language(message)
        
        # Se o idioma detectado for diferente do idioma atual do usuário, atualizar
        if detected_language != user_state.get("language"):
            logger.info(f"Idioma detectado ({detected_language}) diferente do idioma atual ({user_state.get('language')})")
            # Apenas atualizar se for um idioma suportado nativamente
            if detected_language in self.translation_manager.supported_languages:
                self.update_user_state(line_user_id, {"language": detected_language})
                user_state["language"] = detected_language
        
        # Traduzir mensagem para inglês para processamento de comandos
        english_message = self.translation_manager.translate_text(message, detected_language, "en").lower().strip()
        
        # Verificar comandos em diferentes idiomas
        command_found = False
        
        # Comandos em inglês
        if "appointment" in english_message or "schedule" in english_message or "book" in english_message:
            return self.handle_appointment(line_user_id, message)
        elif "cancel" in english_message:
            return self.handle_cancellation(line_user_id, message)
        elif "help" in english_message:
            return self.handle_help(line_user_id, message)
        elif "language" in english_message or "idioma" in english_message:
            return self.handle_language_change(line_user_id, message)
        elif "myid" in english_message or "my id" in english_message:
            return self.handle_user_id(line_user_id, message)
        elif "talk" in english_message or "speak" in english_message or "chat" in english_message:
            return self.handle_talk_to_clinic(line_user_id, message)
        
        # Verificar comandos específicos em português
        if user_state.get("language") == "pt" or detected_language == "pt":
            if "agendar" in lower_message or "marcar" in lower_message or "consulta" in lower_message:
                return self.handle_appointment(line_user_id, message)
            elif "cancelar" in lower_message:
                return self.handle_cancellation(line_user_id, message)
            elif "ajuda" in lower_message:
                return self.handle_help(line_user_id, message)
            elif "idioma" in lower_message or "língua" in lower_message:
                return self.handle_language_change(line_user_id, message)
            elif "meuid" in lower_message or "meu id" in lower_message:
                return self.handle_user_id(line_user_id, message)
            elif "falar" in lower_message or "conversar" in lower_message:
                return self.handle_talk_to_clinic(line_user_id, message)
        
        # Verificar comandos específicos em japonês
        if user_state.get("language") == "ja" or detected_language == "ja":
            if "予約" in message or "よやく" in message:
                return self.handle_appointment(line_user_id, message)
            elif "キャンセル" in message or "取り消し" in message:
                return self.handle_cancellation(line_user_id, message)
            elif "ヘルプ" in message or "助け" in message:
                return self.handle_help(line_user_id, message)
            elif "言語" in message or "げんご" in message:
                return self.handle_language_change(line_user_id, message)
            elif "ID" in message or "アイディー" in message:
                return self.handle_user_id(line_user_id, message)
            elif "話す" in message or "連絡" in message:
                return self.handle_talk_to_clinic(line_user_id, message)
        
        # Se não for um comando conhecido, enviar menu principal
        return self._send_main_menu(line_user_id)
    
    def process_postback(self, line_user_id: str, data: str) -> List[Dict]:
        """
        Processa um postback recebido de um usuário.
        
        Args:
            line_user_id: ID do usuário no LINE.
            data: Dados do postback.
            
        Returns:
            Lista de mensagens a serem enviadas como resposta.
        """
        user_state = self.get_user_state(line_user_id)
        
        # Processar dados do postback
        data_parts = data.split("=")
        if len(data_parts) != 2:
            logger.warning(f"Formato de postback inválido: {data}")
            return self._send_main_menu(line_user_id)
        
        action, value = data_parts
        
        # Processar ações específicas
        if action == "language":
            # Atualizar idioma do usuário
            self.update_user_state(line_user_id, {"language": value})
            
            # Enviar mensagem de confirmação no novo idioma
            language_data = self.translation_manager.get_language_data(value)
            welcome_message = language_data.get("welcome_message", "Welcome!")
            
            # Enviar menu principal
            return [
                {"type": "text", "text": welcome_message},
                *self._send_main_menu(line_user_id)
            ]
        
        elif action == "menu":
            # Processar seleção do menu principal
            if value == "appointment":
                return self.handle_appointment(line_user_id, "")
            elif value == "cancel":
                return self.handle_cancellation(line_user_id, "")
            elif value == "help":
                return self.handle_help(line_user_id, "")
            elif value == "language":
                return self.handle_language_change(line_user_id, "")
            elif value == "talk":
                return self.handle_talk_to_clinic(line_user_id, "")
        
        elif action == "appointment":
            # Processar ações relacionadas a agendamentos
            if value == "confirm":
                return self._confirm_appointment(line_user_id)
            elif value == "cancel":
                self.update_user_state(line_user_id, {
                    "current_flow": None,
                    "appointment_step": None,
                    "appointment_data": {}
                })
                
                # Enviar mensagem de cancelamento
                language = user_state.get("language", "ja")
                cancel_message = self.translation_manager.get_multilingual_response("cancel_message", language)
                
                return [
                    {"type": "text", "text": cancel_message},
                    *self._send_main_menu(line_user_id)
                ]
            elif value.startswith("date_"):
                # Processar seleção de data
                selected_date = value.replace("date_", "")
                self.update_user_state(line_user_id, {
                    "appointment_data": {
                        **user_state.get("appointment_data", {}),
                        "date": selected_date
                    },
                    "appointment_step": "time"
                })
                
                return self._request_appointment_time(line_user_id)
            
            elif value.startswith("time_"):
                # Processar seleção de horário
                selected_time = value.replace("time_", "")
                self.update_user_state(line_user_id, {
                    "appointment_data": {
                        **user_state.get("appointment_data", {}),
                        "time": selected_time
                    },
                    "appointment_step": "reason"
                })
                
                return self._request_appointment_reason(line_user_id)
        
        # Se não for uma ação conhecida, enviar menu principal
        return self._send_main_menu(line_user_id)
    
    def _send_welcome_message(self, line_user_id: str) -> List[Dict]:
        """
        Envia mensagem de boas-vindas e seleção de idioma.
        
        Args:
            line_user_id: ID do usuário no LINE.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        # Criar mensagem de seleção de idioma
        language_selection = self.translation_manager.create_language_selection_message()
        
        # Se for uma lista, retornar diretamente
        if isinstance(language_selection, list):
            return language_selection
        
        # Caso contrário, retornar como lista com um item
        return [language_selection]
    
    def _send_main_menu(self, line_user_id: str) -> List[Dict]:
        """
        Envia o menu principal para o usuário.
        
        Args:
            line_user_id: ID do usuário no LINE.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Obter textos no idioma do usuário
        appointment_text = self.translation_manager.get_multilingual_response("appointment_prompt", language)
        help_text = self.translation_manager.get_multilingual_response("help", language)
        language_text = f"{self.translation_manager.get_language_data(language)['flag']} {self.translation_manager.get_language_data(language)['name']}"
        talk_text = self.translation_manager.translate_text("Talk to the Clinic", "en", language)
        
        # Criar template de botões
        template = {
            "type": "buttons",
            "text": appointment_text,
            "actions": [
                {
                    "type": "postback",
                    "label": appointment_text,
                    "data": "menu=appointment",
                    "displayText": appointment_text
                },
                {
                    "type": "postback",
                    "label": talk_text,
                    "data": "menu=talk",
                    "displayText": talk_text
                },
                {
                    "type": "postback",
                    "label": help_text,
                    "data": "menu=help",
                    "displayText": help_text
                },
                {
                    "type": "postback",
                    "label": language_text,
                    "data": "menu=language",
                    "displayText": language_text
                }
            ]
        }
        
        return [{
            "type": "template",
            "altText": appointment_text,
            "template": template
        }]
    
    def handle_appointment(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Gerencia o fluxo de agendamento de consulta.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Verificar se o usuário já está no fluxo de agendamento
        if user_state.get("current_flow") != "appointment":
            # Iniciar fluxo de agendamento
            self.update_user_state(line_user_id, {
                "current_flow": "appointment",
                "appointment_step": "date",
                "appointment_data": {}
            })
            
            # Verificar se o paciente já existe
            patient = self.supabase_manager.get_patient_by_line_id(line_user_id)
            
            if not patient:
                # Novo paciente, solicitar nome
                return self._request_patient_name(line_user_id)
            else:
                # Paciente existente, solicitar data
                return self._request_appointment_date(line_user_id)
        
        # Continuar fluxo de agendamento
        appointment_step = user_state.get("appointment_step")
        
        if appointment_step == "name":
            # Processar nome do paciente
            if not message.strip():
                # Nome vazio, solicitar novamente
                return self._request_patient_name(line_user_id, True)
            
            # Salvar nome do paciente
            self.update_user_state(line_user_id, {
                "appointment_data": {
                    **user_state.get("appointment_data", {}),
                    "name": message.strip()
                },
                "appointment_step": "phone"
            })
            
            # Solicitar telefone
            return self._request_patient_phone(line_user_id)
        
        elif appointment_step == "phone":
            # Processar telefone do paciente
            if not message.strip():
                # Telefone vazio, solicitar novamente
                return self._request_patient_phone(line_user_id, True)
            
            # Salvar telefone do paciente
            self.update_user_state(line_user_id, {
                "appointment_data": {
                    **user_state.get("appointment_data", {}),
                    "phone": message.strip()
                },
                "appointment_step": "date"
            })
            
            # Criar paciente no banco de dados
            appointment_data = user_state.get("appointment_data", {})
            self.supabase_manager.create_patient(
                line_user_id=line_user_id,
                name=appointment_data.get("name", ""),
                phone=appointment_data.get("phone", ""),
                preferred_language=language
            )
            
            # Solicitar data
            return self._request_appointment_date(line_user_id)
        
        elif appointment_step == "date":
            # Processar data da consulta
            if not self._validate_date(message):
                # Data inválida, solicitar novamente
                return self._request_appointment_date(line_user_id, True)
            
            # Salvar data da consulta
            self.update_user_state(line_user_id, {
                "appointment_data": {
                    **user_state.get("appointment_data", {}),
                    "date": message.strip()
                },
                "appointment_step": "time"
            })
            
            # Solicitar horário
            return self._request_appointment_time(line_user_id)
        
        elif appointment_step == "time":
            # Processar horário da consulta
            if not self._validate_time(message):
                # Horário inválido, solicitar novamente
                return self._request_appointment_time(line_user_id, True)
            
            # Salvar horário da consulta
            self.update_user_state(line_user_id, {
                "appointment_data": {
                    **user_state.get("appointment_data", {}),
                    "time": message.strip()
                },
                "appointment_step": "reason"
            })
            
            # Solicitar motivo
            return self._request_appointment_reason(line_user_id)
        
        elif appointment_step == "reason":
            # Processar motivo da consulta
            if not message.strip():
                # Motivo vazio, solicitar novamente
                return self._request_appointment_reason(line_user_id, True)
            
            # Salvar motivo da consulta
            self.update_user_state(line_user_id, {
                "appointment_data": {
                    **user_state.get("appointment_data", {}),
                    "reason": message.strip()
                },
                "appointment_step": "confirm"
            })
            
            # Solicitar confirmação
            return self._request_appointment_confirmation(line_user_id)
        
        elif appointment_step == "confirm":
            # Processar confirmação
            lower_message = message.lower().strip()
            yes_text = self.translation_manager.get_multilingual_response("yes", language).lower()
            
            # Traduzir mensagem para inglês para verificar confirmação
            english_message = self.translation_manager.translate_text(message, None, "en").lower().strip()
            
            if lower_message == yes_text or "yes" in english_message or "sim" in lower_message or "はい" in message:
                # Confirmado, salvar agendamento
                return self._confirm_appointment(line_user_id)
            else:
                # Não confirmado, cancelar agendamento
                self.update_user_state(line_user_id, {
                    "current_flow": None,
                    "appointment_step": None,
                    "appointment_data": {}
                })
                
                # Enviar mensagem de cancelamento
                cancel_message = self.translation_manager.get_multilingual_response("cancel_message", language)
                
                return [
                    {"type": "text", "text": cancel_message},
                    *self._send_main_menu(line_user_id)
                ]
        
        # Se chegou aqui, algo deu errado, reiniciar fluxo
        self.update_user_state(line_user_id, {
            "current_flow": None,
            "appointment_step": None,
            "appointment_data": {}
        })
        
        return self._send_main_menu(line_user_id)
    
    def _request_patient_name(self, line_user_id: str, is_retry: bool = False) -> List[Dict]:
        """
        Solicita o nome do paciente.
        
        Args:
            line_user_id: ID do usuário no LINE.
            is_retry: Se é uma nova tentativa após erro.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Traduzir mensagem
        if is_retry:
            message = self.translation_manager.translate_text(
                "Please enter your name to continue with the appointment.",
                "en", language
            )
        else:
            message = self.translation_manager.translate_text(
                "To schedule an appointment, please enter your full name:",
                "en", language
            )
        
        return [{"type": "text", "text": message}]
    
    def _request_patient_phone(self, line_user_id: str, is_retry: bool = False) -> List[Dict]:
        """
        Solicita o telefone do paciente.
        
        Args:
            line_user_id: ID do usuário no LINE.
            is_retry: Se é uma nova tentativa após erro.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Traduzir mensagem
        if is_retry:
            message = self.translation_manager.translate_text(
                "Please enter a valid phone number to continue.",
                "en", language
            )
        else:
            message = self.translation_manager.translate_text(
                "Please enter your phone number:",
                "en", language
            )
        
        return [{"type": "text", "text": message}]
    
    def _request_appointment_date(self, line_user_id: str, is_retry: bool = False) -> List[Dict]:
        """
        Solicita a data da consulta.
        
        Args:
            line_user_id: ID do usuário no LINE.
            is_retry: Se é uma nova tentativa após erro.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Obter mensagem de solicitação de data
        if is_retry:
            message = self.translation_manager.translate_text(
                "Please enter a valid date in the format YYYY-MM-DD (e.g., 2025-05-01).",
                "en", language
            )
        else:
            message = self.translation_manager.get_multilingual_response("date_prompt", language)
        
        # Obter datas disponíveis (próximos 7 dias úteis)
        available_dates = self._get_available_dates(7)
        
        # Criar botões para datas disponíveis
        actions = []
        for date_str, date_display in available_dates:
            actions.append({
                "type": "postback",
                "label": date_display,
                "data": f"appointment=date_{date_str}",
                "displayText": date_display
            })
        
        # Criar template de botões
        template = {
            "type": "buttons",
            "text": message,
            "actions": actions[:4]  # Limite de 4 botões
        }
        
        return [{
            "type": "template",
            "altText": message,
            "template": template
        }]
    
    def _request_appointment_time(self, line_user_id: str, is_retry: bool = False) -> List[Dict]:
        """
        Solicita o horário da consulta.
        
        Args:
            line_user_id: ID do usuário no LINE.
            is_retry: Se é uma nova tentativa após erro.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Obter mensagem de solicitação de horário
        if is_retry:
            message = self.translation_manager.translate_text(
                "Please enter a valid time in the format HH:MM (e.g., 14:30).",
                "en", language
            )
        else:
            message = self.translation_manager.get_multilingual_response("time_prompt", language)
        
        # Obter horários disponíveis
        available_times = self._get_available_times()
        
        # Criar botões para horários disponíveis
        actions = []
        for time_str in available_times[:4]:  # Limite de 4 botões
            actions.append({
                "type": "postback",
                "label": time_str,
                "data": f"appointment=time_{time_str}",
                "displayText": time_str
            })
        
        # Criar template de botões
        template = {
            "type": "buttons",
            "text": message,
            "actions": actions
        }
        
        return [{
            "type": "template",
            "altText": message,
            "template": template
        }]
    
    def _request_appointment_reason(self, line_user_id: str, is_retry: bool = False) -> List[Dict]:
        """
        Solicita o motivo da consulta.
        
        Args:
            line_user_id: ID do usuário no LINE.
            is_retry: Se é uma nova tentativa após erro.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Obter mensagem de solicitação de motivo
        if is_retry:
            message = self.translation_manager.translate_text(
                "Please enter the reason for your appointment to continue.",
                "en", language
            )
        else:
            message = self.translation_manager.get_multilingual_response("reason_prompt", language)
        
        return [{"type": "text", "text": message}]
    
    def _request_appointment_confirmation(self, line_user_id: str) -> List[Dict]:
        """
        Solicita confirmação do agendamento.
        
        Args:
            line_user_id: ID do usuário no LINE.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        appointment_data = user_state.get("appointment_data", {})
        
        # Obter dados do paciente
        patient = self.supabase_manager.get_patient_by_line_id(line_user_id)
        patient_name = patient.get("name") if patient else appointment_data.get("name", "")
        
        # Obter mensagem de confirmação
        confirm_prompt = self.translation_manager.get_multilingual_response("confirm_prompt", language)
        
        # Traduzir detalhes
        date_label = self.translation_manager.translate_text("Date", "en", language)
        time_label = self.translation_manager.translate_text("Time", "en", language)
        reason_label = self.translation_manager.translate_text("Reason", "en", language)
        
        # Criar mensagem de confirmação
        confirmation_text = f"{confirm_prompt}\n\n"
        confirmation_text += f"{date_label}: {appointment_data.get('date')}\n"
        confirmation_text += f"{time_label}: {appointment_data.get('time')}\n"
        confirmation_text += f"{reason_label}: {appointment_data.get('reason')}\n"
        
        # Obter textos para botões
        yes_text = self.translation_manager.get_multilingual_response("yes", language)
        no_text = self.translation_manager.get_multilingual_response("no", language)
        
        # Criar template de botões
        template = {
            "type": "buttons",
            "text": confirmation_text,
            "actions": [
                {
                    "type": "postback",
                    "label": yes_text,
                    "data": "appointment=confirm",
                    "displayText": yes_text
                },
                {
                    "type": "postback",
                    "label": no_text,
                    "data": "appointment=cancel",
                    "displayText": no_text
                }
            ]
        }
        
        return [{
            "type": "template",
            "altText": confirm_prompt,
            "template": template
        }]
    
    def _confirm_appointment(self, line_user_id: str) -> List[Dict]:
        """
        Confirma e salva o agendamento.
        
        Args:
            line_user_id: ID do usuário no LINE.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        appointment_data = user_state.get("appointment_data", {})
        
        # Obter dados do paciente
        patient = self.supabase_manager.get_patient_by_line_id(line_user_id)
        
        if not patient:
            logger.error(f"Paciente não encontrado para o usuário {line_user_id}")
            # Enviar mensagem de erro
            error_message = self.translation_manager.translate_text(
                "An error occurred while scheduling your appointment. Please try again.",
                "en", language
            )
            
            return [
                {"type": "text", "text": error_message},
                *self._send_main_menu(line_user_id)
            ]
        
        # Salvar agendamento no banco de dados
        appointment_id = self.supabase_manager.create_appointment(
            patient_id=patient.get("id"),
            appointment_date=appointment_data.get("date"),
            appointment_time=appointment_data.get("time"),
            reason=appointment_data.get("reason")
        )
        
        if not appointment_id:
            logger.error(f"Erro ao criar agendamento para o usuário {line_user_id}")
            # Enviar mensagem de erro
            error_message = self.translation_manager.translate_text(
                "An error occurred while scheduling your appointment. Please try again.",
                "en", language
            )
            
            return [
                {"type": "text", "text": error_message},
                *self._send_main_menu(line_user_id)
            ]
        
        # Limpar estado do usuário
        self.update_user_state(line_user_id, {
            "current_flow": None,
            "appointment_step": None,
            "appointment_data": {}
        })
        
        # Enviar mensagem de sucesso
        success_message = self.translation_manager.get_multilingual_response("success_message", language)
        
        # Notificar a clínica sobre o novo agendamento
        self._notify_clinic_about_appointment(patient, appointment_data)
        
        return [
            {"type": "text", "text": success_message},
            *self._send_main_menu(line_user_id)
        ]
    
    def _notify_clinic_about_appointment(self, patient: Dict[str, Any], appointment_data: Dict[str, Any]):
        """
        Notifica a clínica sobre um novo agendamento.
        
        Args:
            patient: Dados do paciente.
            appointment_data: Dados do agendamento.
        """
        try:
            # Obter ID do dono da clínica
            clinic_owner_id = os.getenv("CLINIC_LINE_USER_ID")
            
            if not clinic_owner_id:
                logger.warning("CLINIC_LINE_USER_ID não configurado. Notificação não enviada.")
                return
            
            # Criar mensagem de notificação
            notification = f"🔔 New Appointment / 新しい予約\n\n"
            notification += f"Patient / 患者: {patient.get('name')}\n"
            notification += f"Date / 日付: {appointment_data.get('date')}\n"
            notification += f"Time / 時間: {appointment_data.get('time')}\n"
            notification += f"Reason / 理由: {appointment_data.get('reason')}\n"
            notification += f"Language / 言語: {self.translation_manager.language_names.get(patient.get('preferred_language', 'ja'), 'Japanese')}"
            
            # Enviar notificação
            self.line_manager.push_message(clinic_owner_id, [{"type": "text", "text": notification}])
            
            logger.info(f"Notificação enviada para o dono da clínica: {clinic_owner_id}")
        except Exception as e:
            logger.error(f"Erro ao notificar clínica sobre agendamento: {str(e)}")
    
    def handle_cancellation(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Gerencia o fluxo de cancelamento de consulta.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Implementação básica, pode ser expandida conforme necessário
        cancel_message = self.translation_manager.translate_text(
            "To cancel an appointment, please contact the clinic directly.",
            "en", language
        )
        
        return [
            {"type": "text", "text": cancel_message},
            *self._send_main_menu(line_user_id)
        ]
    
    def handle_help(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Gerencia o fluxo de ajuda.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Traduzir mensagem de ajuda
        help_message = self.translation_manager.translate_text(
            "Here's how you can use this chatbot:\n\n"
            "• To schedule an appointment, type 'appointment' or click the button\n"
            "• To change language, type 'language' or click the button\n"
            "• To talk to the clinic, type 'talk' or click the button\n"
            "• To see your LINE user ID, type 'myid'\n\n"
            "For any other assistance, please contact the clinic directly.",
            "en", language
        )
        
        return [
            {"type": "text", "text": help_message},
            *self._send_main_menu(line_user_id)
        ]
    
    def handle_language_change(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Gerencia o fluxo de mudança de idioma.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        # Atualizar estado do usuário
        self.update_user_state(line_user_id, {"current_flow": "language_change"})
        
        # Enviar mensagem de seleção de idioma
        return self._send_welcome_message(line_user_id)
    
    def handle_user_id(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Envia o ID do usuário no LINE.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Traduzir mensagem
        id_message = self.translation_manager.translate_text(
            f"Your LINE User ID is:\n{line_user_id}\n\nThis ID is used to identify you in our system.",
            "en", language
        )
        
        return [
            {"type": "text", "text": id_message},
            *self._send_main_menu(line_user_id)
        ]
    
    def handle_talk_to_clinic(self, line_user_id: str, message: str) -> List[Dict]:
        """
        Gerencia o fluxo de conversa direta com a clínica.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem recebida.
            
        Returns:
            Lista de mensagens a serem enviadas.
        """
        user_state = self.get_user_state(line_user_id)
        language = user_state.get("language", "ja")
        
        # Verificar se o usuário já está no fluxo de conversa
        if user_state.get("current_flow") != "talk_to_clinic":
            # Iniciar fluxo de conversa
            self.update_user_state(line_user_id, {"current_flow": "talk_to_clinic"})
            
            # Traduzir mensagem
            talk_message = self.translation_manager.translate_text(
                "Please type your message to the clinic. A staff member will respond as soon as possible.\n\nTo return to the main menu, type 'menu'.",
                "en", language
            )
            
            return [{"type": "text", "text": talk_message}]
        
        # Verificar se o usuário quer voltar ao menu
        lower_message = message.lower().strip()
        
        # Traduzir mensagem para inglês para verificar comando de menu
        english_message = self.translation_manager.translate_text(message, None, "en").lower().strip()
        
        if lower_message == "menu" or "menu" in english_message:
            # Voltar ao menu principal
            self.update_user_state(line_user_id, {"current_flow": None})
            return self._send_main_menu(line_user_id)
        
        # Encaminhar mensagem para a clínica
        self._forward_message_to_clinic(line_user_id, message)
        
        # Traduzir mensagem de confirmação
        confirm_message = self.translation_manager.translate_text(
            "Your message has been sent to the clinic. They will respond as soon as possible.",
            "en", language
        )
        
        return [{"type": "text", "text": confirm_message}]
    
    def _forward_message_to_clinic(self, line_user_id: str, message: str):
        """
        Encaminha uma mensagem para a clínica.
        
        Args:
            line_user_id: ID do usuário no LINE.
            message: Mensagem a ser encaminhada.
        """
        try:
            # Obter ID do dono da clínica
            clinic_owner_id = os.getenv("CLINIC_LINE_USER_ID")
            
            if not clinic_owner_id:
                logger.warning("CLINIC_LINE_USER_ID não configurado. Mensagem não encaminhada.")
                return
            
            # Obter dados do paciente
            patient = self.supabase_manager.get_patient_by_line_id(line_user_id)
            patient_name = patient.get("name", "Unknown") if patient else "Unknown"
            
            # Criar mensagem de encaminhamento
            forwarded_message = f"📩 Message from / からのメッセージ: {patient_name}\n\n"
            forwarded_message += message
            
            # Adicionar informações do paciente
            if patient:
                language_name = self.translation_manager.language_names.get(
                    patient.get("preferred_language", "ja"), "Japanese"
                )
                forwarded_message += f"\n\n(Language / 言語: {language_name})"
            
            # Enviar mensagem
            self.line_manager.push_message(clinic_owner_id, [{"type": "text", "text": forwarded_message}])
            
            logger.info(f"Mensagem encaminhada para o dono da clínica: {clinic_owner_id}")
        except Exception as e:
            logger.error(f"Erro ao encaminhar mensagem para a clínica: {str(e)}")
    
    def _validate_date(self, date_str: str) -> bool:
        """
        Valida uma string de data.
        
        Args:
            date_str: String de data no formato YYYY-MM-DD.
            
        Returns:
            True se a data for válida, False caso contrário.
        """
        import re
        from datetime import datetime
        
        # Verificar formato
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        
        # Verificar se é uma data válida
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.now()
            
            # Verificar se a data é futura
            if date_obj.date() < today.date():
                return False
            
            return True
        except ValueError:
            return False
    
    def _validate_time(self, time_str: str) -> bool:
        """
        Valida uma string de horário.
        
        Args:
            time_str: String de horário no formato HH:MM.
            
        Returns:
            True se o horário for válido, False caso contrário.
        """
        import re
        
        # Verificar formato
        if not re.match(r"^\d{1,2}:\d{2}$", time_str):
            return False
        
        # Verificar se é um horário válido
        try:
            hours, minutes = map(int, time_str.split(":"))
            
            if hours < 0 or hours > 23 or minutes < 0 or minutes > 59:
                return False
            
            # Verificar se está dentro do horário de funcionamento (9:00 - 18:00)
            if hours < 9 or (hours == 18 and minutes > 0) or hours > 18:
                return False
            
            return True
        except ValueError:
            return False
    
    def _get_available_dates(self, num_days: int = 7) -> List[Tuple[str, str]]:
        """
        Obtém datas disponíveis para agendamento.
        
        Args:
            num_days: Número de dias úteis a serem retornados.
            
        Returns:
            Lista de tuplas (data_str, data_display) com datas disponíveis.
        """
        from datetime import datetime, timedelta
        import locale
        
        # Configurar locale para exibição de datas
        try:
            locale.setlocale(locale.LC_TIME, "ja_JP.UTF-8")
        except:
            pass
        
        # Data atual
        current_date = datetime.now()
        
        # Lista de datas disponíveis
        available_dates = []
        
        # Adicionar próximos dias úteis
        days_added = 0
        while days_added < num_days:
            current_date += timedelta(days=1)
            
            # Pular finais de semana (0 = segunda, 6 = domingo)
            if current_date.weekday() >= 5:
                continue
            
            # Formatar data
            date_str = current_date.strftime("%Y-%m-%d")
            
            # Formatar exibição da data
            try:
                # Tentar usar formato japonês
                date_display = current_date.strftime("%m月%d日(%a)")
            except:
                # Fallback para formato padrão
                date_display = current_date.strftime("%b %d (%a)")
            
            available_dates.append((date_str, date_display))
            days_added += 1
        
        return available_dates
    
    def _get_available_times(self) -> List[str]:
        """
        Obtém horários disponíveis para agendamento.
        
        Returns:
            Lista de strings com horários disponíveis.
        """
        # Horários de funcionamento: 9:00 - 18:00, intervalos de 30 minutos
        available_times = []
        
        for hour in range(9, 18):
            for minute in [0, 30]:
                # Pular 12:00 e 12:30 (horário de almoço)
                if hour == 12:
                    continue
                
                time_str = f"{hour:02d}:{minute:02d}"
                available_times.append(time_str)
        
        return available_times
