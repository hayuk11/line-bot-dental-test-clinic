import os
import openai
import logging
from typing import Dict, List, Optional, Any

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class TranslationManager:
    """
    Gerenciador de traduções para o chatbot LINE.
    Suporta tradução entre múltiplos idiomas e detecção automática de idioma.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o gerenciador de traduções.
        
        Args:
            api_key: Chave da API OpenAI. Se não fornecida, tenta obter da variável de ambiente.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY não configurada. Tradução avançada não estará disponível.")
        
        # Idiomas suportados nativamente (sem necessidade de tradução via API)
        self.supported_languages = {
            "ja": {
                "name": "日本語",
                "flag": "🇯🇵",
                "welcome_message": "クリニカ・タナカへようこそ！ご希望の言語を選択してください。",
                "appointment_prompt": "診察の予約をしますか？",
                "common_phrases": {
                    "yes": "はい",
                    "no": "いいえ",
                    "thank_you": "ありがとうございます",
                    "goodbye": "さようなら",
                    "help": "ヘルプ"
                },
                "appointment_flow": {
                    "date_prompt": "希望日を選択してください（例：2025-05-01）：",
                    "time_prompt": "希望時間を選択してください：",
                    "reason_prompt": "診察の理由を教えてください：",
                    "confirm_prompt": "以下の予約内容でよろしいですか？",
                    "success_message": "予約が完了しました！確認のメッセージが届きます。",
                    "cancel_message": "予約をキャンセルしました。"
                }
            },
            "en": {
                "name": "English",
                "flag": "🇺🇸",
                "welcome_message": "Welcome to Clinica Tanaka! Please select your preferred language.",
                "appointment_prompt": "Would you like to schedule an appointment?",
                "common_phrases": {
                    "yes": "Yes",
                    "no": "No",
                    "thank_you": "Thank you",
                    "goodbye": "Goodbye",
                    "help": "Help"
                },
                "appointment_flow": {
                    "date_prompt": "Please select your preferred date (e.g., 2025-05-01):",
                    "time_prompt": "Please select your preferred time:",
                    "reason_prompt": "Please tell us the reason for your visit:",
                    "confirm_prompt": "Please confirm your appointment details:",
                    "success_message": "Your appointment has been scheduled! You will receive a confirmation message.",
                    "cancel_message": "Your appointment has been canceled."
                }
            },
            "pt": {
                "name": "Português",
                "flag": "🇧🇷",
                "welcome_message": "Bem-vindo à Clínica Tanaka! Por favor, selecione seu idioma preferido.",
                "appointment_prompt": "Gostaria de agendar uma consulta?",
                "common_phrases": {
                    "yes": "Sim",
                    "no": "Não",
                    "thank_you": "Obrigado",
                    "goodbye": "Adeus",
                    "help": "Ajuda"
                },
                "appointment_flow": {
                    "date_prompt": "Por favor, selecione a data desejada (ex: 2025-05-01):",
                    "time_prompt": "Por favor, selecione o horário desejado:",
                    "reason_prompt": "Por favor, informe o motivo da consulta:",
                    "confirm_prompt": "Por favor, confirme os detalhes do seu agendamento:",
                    "success_message": "Sua consulta foi agendada! Você receberá uma mensagem de confirmação.",
                    "cancel_message": "Seu agendamento foi cancelado."
                }
            },
            "zh": {
                "name": "中文",
                "flag": "🇨🇳",
                "welcome_message": "欢迎来到田中诊所！请选择您的首选语言。",
                "appointment_prompt": "您想预约看诊吗？",
                "common_phrases": {
                    "yes": "是",
                    "no": "否",
                    "thank_you": "谢谢",
                    "goodbye": "再见",
                    "help": "帮助"
                },
                "appointment_flow": {
                    "date_prompt": "请选择您希望的日期（例如：2025-05-01）：",
                    "time_prompt": "请选择您希望的时间：",
                    "reason_prompt": "请告诉我们您就诊的原因：",
                    "confirm_prompt": "请确认您的预约详情：",
                    "success_message": "您的预约已安排！您将收到确认消息。",
                    "cancel_message": "您的预约已取消。"
                }
            },
            "ko": {
                "name": "한국어",
                "flag": "🇰🇷",
                "welcome_message": "다나카 클리닉에 오신 것을 환영합니다! 원하는 언어를 선택해 주세요.",
                "appointment_prompt": "진료 예약을 하시겠습니까?",
                "common_phrases": {
                    "yes": "예",
                    "no": "아니오",
                    "thank_you": "감사합니다",
                    "goodbye": "안녕히 가세요",
                    "help": "도움말"
                },
                "appointment_flow": {
                    "date_prompt": "원하시는 날짜를 선택해 주세요 (예: 2025-05-01):",
                    "time_prompt": "원하시는 시간을 선택해 주세요:",
                    "reason_prompt": "진료 이유를 알려주세요:",
                    "confirm_prompt": "예약 정보를 확인해 주세요:",
                    "success_message": "예약이 완료되었습니다! 확인 메시지가 발송됩니다.",
                    "cancel_message": "예약이 취소되었습니다."
                }
            },
            "es": {
                "name": "Español",
                "flag": "🇪🇸",
                "welcome_message": "¡Bienvenido a Clínica Tanaka! Por favor, seleccione su idioma preferido.",
                "appointment_prompt": "¿Le gustaría programar una cita?",
                "common_phrases": {
                    "yes": "Sí",
                    "no": "No",
                    "thank_you": "Gracias",
                    "goodbye": "Adiós",
                    "help": "Ayuda"
                },
                "appointment_flow": {
                    "date_prompt": "Por favor, seleccione la fecha deseada (ej: 2025-05-01):",
                    "time_prompt": "Por favor, seleccione la hora deseada:",
                    "reason_prompt": "Por favor, indique el motivo de su consulta:",
                    "confirm_prompt": "Por favor, confirme los detalles de su cita:",
                    "success_message": "¡Su cita ha sido programada! Recibirá un mensaje de confirmación.",
                    "cancel_message": "Su cita ha sido cancelada."
                }
            },
            "tl": {
                "name": "Tagalog",
                "flag": "🇵🇭",
                "welcome_message": "Maligayang pagdating sa Clinica Tanaka! Mangyaring piliin ang iyong gustong wika.",
                "appointment_prompt": "Gusto mo bang mag-iskedyul ng appointment?",
                "common_phrases": {
                    "yes": "Oo",
                    "no": "Hindi",
                    "thank_you": "Salamat",
                    "goodbye": "Paalam",
                    "help": "Tulong"
                },
                "appointment_flow": {
                    "date_prompt": "Mangyaring piliin ang iyong gustong petsa (hal., 2025-05-01):",
                    "time_prompt": "Mangyaring piliin ang iyong gustong oras:",
                    "reason_prompt": "Mangyaring sabihin sa amin ang dahilan ng iyong pagbisita:",
                    "confirm_prompt": "Mangyaring kumpirmahin ang mga detalye ng iyong appointment:",
                    "success_message": "Naka-iskedyul na ang iyong appointment! Makakatanggap ka ng mensahe ng kumpirmasyon.",
                    "cancel_message": "Nakansela na ang iyong appointment."
                }
            },
            "vi": {
                "name": "Tiếng Việt",
                "flag": "🇻🇳",
                "welcome_message": "Chào mừng đến với Phòng khám Tanaka! Vui lòng chọn ngôn ngữ ưa thích của bạn.",
                "appointment_prompt": "Bạn có muốn đặt lịch hẹn không?",
                "common_phrases": {
                    "yes": "Có",
                    "no": "Không",
                    "thank_you": "Cảm ơn",
                    "goodbye": "Tạm biệt",
                    "help": "Trợ giúp"
                },
                "appointment_flow": {
                    "date_prompt": "Vui lòng chọn ngày bạn muốn (ví dụ: 2025-05-01):",
                    "time_prompt": "Vui lòng chọn thời gian bạn muốn:",
                    "reason_prompt": "Vui lòng cho chúng tôi biết lý do bạn đến khám:",
                    "confirm_prompt": "Vui lòng xác nhận chi tiết cuộc hẹn của bạn:",
                    "success_message": "Cuộc hẹn của bạn đã được lên lịch! Bạn sẽ nhận được tin nhắn xác nhận.",
                    "cancel_message": "Cuộc hẹn của bạn đã bị hủy."
                }
            }
        }
        
        # Mapeamento de códigos de idioma para nomes completos
        self.language_names = {
            "ja": "Japanese",
            "en": "English",
            "pt": "Portuguese",
            "zh": "Chinese",
            "ko": "Korean",
            "es": "Spanish",
            "tl": "Tagalog",
            "vi": "Vietnamese",
            "fr": "French",
            "de": "German",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
            "th": "Thai",
            "id": "Indonesian"
        }
        
        # Inicializar OpenAI se a chave estiver disponível
        if self.api_key:
            openai.api_key = self.api_key
    
    def get_language_options(self) -> List[Dict[str, str]]:
        """
        Retorna as opções de idioma disponíveis para seleção pelo usuário.
        
        Returns:
            Lista de dicionários com informações de cada idioma suportado.
        """
        options = []
        for code, data in self.supported_languages.items():
            options.append({
                "code": code,
                "name": data["name"],
                "flag": data["flag"]
            })
        
        # Adicionar opção para outros idiomas
        options.append({
            "code": "other",
            "name": "Other Languages",
            "flag": "🌐"
        })
        
        return options
    
    def get_language_data(self, language_code: str) -> Dict[str, Any]:
        """
        Retorna os dados de um idioma específico.
        
        Args:
            language_code: Código do idioma (ex: "ja", "en", "pt").
            
        Returns:
            Dicionário com dados do idioma ou dados do idioma padrão (inglês) se não encontrado.
        """
        return self.supported_languages.get(language_code, self.supported_languages["en"])
    
    def detect_language(self, text: str) -> str:
        """
        Detecta o idioma de um texto usando a API OpenAI.
        
        Args:
            text: Texto para detectar o idioma.
            
        Returns:
            Código do idioma detectado (ex: "ja", "en", "pt") ou "en" se não for possível detectar.
        """
        if not self.api_key or not text:
            return "en"
        
        try:
            prompt = f"Detect the language of the following text and respond with only the ISO 639-1 language code (e.g., 'en', 'ja', 'pt', etc.):\n\n{text}"
            
            response = self._call_openai_api(prompt)
            
            if response and "choices" in response:
                detected_code = response["choices"][0]["message"]["content"].strip().lower()
                
                # Verificar se o código é válido
                if detected_code in self.language_names:
                    return detected_code
                
                # Tentar extrair código válido se a resposta contiver mais informações
                for code in self.language_names.keys():
                    if code in detected_code:
                        return code
            
            logger.warning(f"Não foi possível detectar o idioma do texto: {text[:50]}...")
            return "en"
        except Exception as e:
            logger.error(f"Erro ao detectar idioma: {str(e)}")
            return "en"
    
    def translate_text(self, text: str, source_lang: str = None, target_lang: str = "en") -> str:
        """
        Traduz um texto de um idioma para outro usando a API OpenAI.
        
        Args:
            text: Texto a ser traduzido.
            source_lang: Idioma de origem (opcional, será detectado automaticamente se não fornecido).
            target_lang: Idioma de destino (padrão: inglês).
            
        Returns:
            Texto traduzido ou o texto original se não for possível traduzir.
        """
        if not self.api_key or not text:
            return text
        
        # Se o idioma de origem não for fornecido, detectar automaticamente
        if not source_lang:
            source_lang = self.detect_language(text)
        
        # Se o idioma de origem for o mesmo que o de destino, retornar o texto original
        if source_lang == target_lang:
            return text
        
        try:
            source_name = self.language_names.get(source_lang, "unknown language")
            target_name = self.language_names.get(target_lang, "English")
            
            prompt = f"Translate the following {source_name} text to {target_name}. Provide only the translation without explanations or notes:\n\n{text}"
            
            response = self._call_openai_api(prompt)
            
            if response and "choices" in response:
                return response["choices"][0]["message"]["content"].strip()
            
            logger.warning(f"Não foi possível traduzir o texto: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"Erro ao traduzir texto: {str(e)}")
            return text
    
    def get_multilingual_response(self, message_key: str, language_code: str) -> str:
        """
        Obtém uma resposta em um idioma específico com base em uma chave de mensagem.
        
        Args:
            message_key: Chave da mensagem (ex: "welcome_message", "appointment_prompt").
            language_code: Código do idioma desejado.
            
        Returns:
            Mensagem no idioma especificado.
        """
        # Verificar se o idioma é suportado nativamente
        if language_code in self.supported_languages:
            # Verificar se a mensagem existe diretamente
            if message_key in self.supported_languages[language_code]:
                return self.supported_languages[language_code][message_key]
            
            # Verificar se a mensagem está em appointment_flow
            if "appointment_flow" in self.supported_languages[language_code] and message_key in self.supported_languages[language_code]["appointment_flow"]:
                return self.supported_languages[language_code]["appointment_flow"][message_key]
            
            # Verificar se a mensagem está em common_phrases
            if "common_phrases" in self.supported_languages[language_code] and message_key in self.supported_languages[language_code]["common_phrases"]:
                return self.supported_languages[language_code]["common_phrases"][message_key]
        
        # Se não encontrar, obter a mensagem em inglês e traduzir
        english_message = ""
        if message_key in self.supported_languages["en"]:
            english_message = self.supported_languages["en"][message_key]
        elif "appointment_flow" in self.supported_languages["en"] and message_key in self.supported_languages["en"]["appointment_flow"]:
            english_message = self.supported_languages["en"]["appointment_flow"][message_key]
        elif "common_phrases" in self.supported_languages["en"] and message_key in self.supported_languages["en"]["common_phrases"]:
            english_message = self.supported_languages["en"]["common_phrases"][message_key]
        else:
            logger.warning(f"Chave de mensagem não encontrada: {message_key}")
            return f"Message not found: {message_key}"
        
        # Traduzir para o idioma desejado
        return self.translate_text(english_message, "en", language_code)
    
    def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """
        Faz uma chamada à API OpenAI.
        
        Args:
            prompt: Prompt para enviar à API.
            
        Returns:
            Resposta da API ou None em caso de erro.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that specializes in language translation and detection."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            return response
        except Exception as e:
            logger.error(f"Erro na chamada à API OpenAI: {str(e)}")
            return None
    
    def create_language_selection_message(self) -> Dict[str, Any]:
        """
        Cria uma mensagem de seleção de idioma para o usuário.
        
        Returns:
            Mensagem formatada para a API LINE com opções de idioma.
        """
        language_options = self.get_language_options()
        
        # Criar mensagem de texto multilíngue
        welcome_text = "🌍 言語を選択してください / Please select your language / Por favor, selecione seu idioma"
        
        # Criar botões para cada idioma
        actions = []
        for option in language_options:
            actions.append({
                "type": "postback",
                "label": f"{option['flag']} {option['name']}",
                "data": f"language={option['code']}",
                "displayText": f"{option['flag']} {option['name']}"
            })
        
        # Criar template de botões
        template = {
            "type": "buttons",
            "text": welcome_text,
            "actions": actions[:4]  # Limite de 4 botões por template
        }
        
        # Se houver mais de 4 idiomas, criar carrossel
        if len(language_options) > 4:
            columns = []
            
            # Primeiro grupo já foi usado nos botões acima
            remaining_options = language_options[4:]
            
            # Criar colunas para cada grupo de 3 idiomas
            for i in range(0, len(remaining_options), 3):
                group = remaining_options[i:i+3]
                actions = []
                
                for option in group:
                    actions.append({
                        "type": "postback",
                        "label": f"{option['flag']} {option['name']}",
                        "data": f"language={option['code']}",
                        "displayText": f"{option['flag']} {option['name']}"
                    })
                
                # Preencher com ações vazias se necessário
                while len(actions) < 3:
                    actions.append({
                        "type": "postback",
                        "label": " ",
                        "data": "language=none",
                        "displayText": " "
                    })
                
                columns.append({
                    "title": "More Languages",
                    "text": "Select your preferred language",
                    "actions": actions
                })
            
            # Retornar mensagem de texto e carrossel
            return [
                {
                    "type": "template",
                    "altText": "Language Selection",
                    "template": template
                },
                {
                    "type": "template",
                    "altText": "More Languages",
                    "template": {
                        "type": "carousel",
                        "columns": columns
                    }
                }
            ]
        
        # Se houver apenas 4 ou menos idiomas, retornar apenas os botões
        return {
            "type": "template",
            "altText": "Language Selection",
            "template": template
        }
    
    def create_multilingual_message(self, message_key: str, language_code: str, **kwargs) -> Dict[str, str]:
        """
        Cria uma mensagem multilíngue com base em uma chave de mensagem.
        
        Args:
            message_key: Chave da mensagem.
            language_code: Código do idioma.
            **kwargs: Parâmetros para formatação da mensagem.
            
        Returns:
            Mensagem formatada para a API LINE.
        """
        message = self.get_multilingual_response(message_key, language_code)
        
        # Formatar mensagem com parâmetros adicionais
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                logger.error(f"Erro ao formatar mensagem: {str(e)}")
        
        return {
            "type": "text",
            "text": message
        }
