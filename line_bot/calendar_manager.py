import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CalendarManager:
    """
    Gerenciador de integração com calendários para o chatbot LINE.
    Suporta Google Calendar, Microsoft Outlook e Apple Calendar (iCal).
    """
    
    def __init__(self, supabase_manager):
        """
        Inicializa o gerenciador de calendário.
        
        Args:
            supabase_manager: Instância do gerenciador do Supabase.
        """
        self.supabase_manager = supabase_manager
        
        # Configurações de calendário
        self.calendar_settings = {
            "google": {
                "enabled": os.getenv("GOOGLE_CALENDAR_ENABLED", "false").lower() == "true",
                "credentials_file": os.getenv("GOOGLE_CALENDAR_CREDENTIALS", ""),
                "calendar_id": os.getenv("GOOGLE_CALENDAR_ID", "primary")
            },
            "outlook": {
                "enabled": os.getenv("OUTLOOK_CALENDAR_ENABLED", "false").lower() == "true",
                "client_id": os.getenv("OUTLOOK_CLIENT_ID", ""),
                "client_secret": os.getenv("OUTLOOK_CLIENT_SECRET", ""),
                "tenant_id": os.getenv("OUTLOOK_TENANT_ID", "")
            },
            "ical": {
                "enabled": os.getenv("ICAL_CALENDAR_ENABLED", "false").lower() == "true",
                "url": os.getenv("ICAL_CALENDAR_URL", "")
            }
        }
        
        # Inicializar clientes de calendário
        self._init_calendar_clients()
    
    def _init_calendar_clients(self):
        """
        Inicializa os clientes de calendário conforme configurações.
        """
        # Google Calendar
        if self.calendar_settings["google"]["enabled"]:
            try:
                self._init_google_calendar()
                logger.info("Cliente do Google Calendar inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente do Google Calendar: {str(e)}")
                self.calendar_settings["google"]["enabled"] = False
        
        # Microsoft Outlook
        if self.calendar_settings["outlook"]["enabled"]:
            try:
                self._init_outlook_calendar()
                logger.info("Cliente do Microsoft Outlook inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente do Microsoft Outlook: {str(e)}")
                self.calendar_settings["outlook"]["enabled"] = False
        
        # Apple Calendar (iCal)
        if self.calendar_settings["ical"]["enabled"]:
            try:
                self._init_ical_calendar()
                logger.info("Cliente do Apple Calendar (iCal) inicializado com sucesso.")
            except Exception as e:
                logger.error(f"Erro ao inicializar cliente do Apple Calendar (iCal): {str(e)}")
                self.calendar_settings["ical"]["enabled"] = False
    
    def _init_google_calendar(self):
        """
        Inicializa o cliente do Google Calendar.
        """
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
            
            credentials_file = self.calendar_settings["google"]["credentials_file"]
            
            if not credentials_file or not os.path.exists(credentials_file):
                logger.warning("Arquivo de credenciais do Google Calendar não encontrado.")
                self.calendar_settings["google"]["enabled"] = False
                return
            
            # Carregar credenciais
            credentials = service_account.Credentials.from_service_account_file(
                credentials_file,
                scopes=["https://www.googleapis.com/auth/calendar"]
            )
            
            # Construir serviço
            self.google_calendar = build("calendar", "v3", credentials=credentials)
            
            logger.info("Cliente do Google Calendar inicializado com sucesso.")
        except ImportError:
            logger.error("Bibliotecas do Google Calendar não instaladas. Execute: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            self.calendar_settings["google"]["enabled"] = False
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente do Google Calendar: {str(e)}")
            self.calendar_settings["google"]["enabled"] = False
    
    def _init_outlook_calendar(self):
        """
        Inicializa o cliente do Microsoft Outlook Calendar.
        """
        try:
            import msal
            
            client_id = self.calendar_settings["outlook"]["client_id"]
            client_secret = self.calendar_settings["outlook"]["client_secret"]
            tenant_id = self.calendar_settings["outlook"]["tenant_id"]
            
            if not client_id or not client_secret or not tenant_id:
                logger.warning("Credenciais do Microsoft Outlook incompletas.")
                self.calendar_settings["outlook"]["enabled"] = False
                return
            
            # Configurar aplicativo MSAL
            self.outlook_app = msal.ConfidentialClientApplication(
                client_id,
                authority=f"https://login.microsoftonline.com/{tenant_id}",
                client_credential=client_secret
            )
            
            # Escopo para calendário
            self.outlook_scopes = ["https://graph.microsoft.com/Calendars.ReadWrite"]
            
            logger.info("Cliente do Microsoft Outlook inicializado com sucesso.")
        except ImportError:
            logger.error("Biblioteca MSAL não instalada. Execute: pip install msal")
            self.calendar_settings["outlook"]["enabled"] = False
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente do Microsoft Outlook: {str(e)}")
            self.calendar_settings["outlook"]["enabled"] = False
    
    def _init_ical_calendar(self):
        """
        Inicializa o cliente do Apple Calendar (iCal).
        """
        try:
            import icalendar
            
            url = self.calendar_settings["ical"]["url"]
            
            if not url:
                logger.warning("URL do calendário iCal não configurada.")
                self.calendar_settings["ical"]["enabled"] = False
                return
            
            # Testar acesso ao calendário
            response = requests.get(url)
            response.raise_for_status()
            
            # Verificar se é um calendário iCal válido
            icalendar.Calendar.from_ical(response.text)
            
            logger.info("Cliente do Apple Calendar (iCal) inicializado com sucesso.")
        except ImportError:
            logger.error("Biblioteca icalendar não instalada. Execute: pip install icalendar")
            self.calendar_settings["ical"]["enabled"] = False
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente do Apple Calendar (iCal): {str(e)}")
            self.calendar_settings["ical"]["enabled"] = False
    
    def get_available_slots(self, start_date: str, end_date: str = None, duration_minutes: int = 30) -> List[Dict[str, str]]:
        """
        Obtém slots disponíveis para agendamento.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD (opcional, padrão: start_date).
            duration_minutes: Duração da consulta em minutos (padrão: 30).
            
        Returns:
            Lista de slots disponíveis no formato {date: YYYY-MM-DD, time: HH:MM}.
        """
        # Se end_date não for fornecido, usar start_date
        if not end_date:
            end_date = start_date
        
        # Converter strings para objetos datetime
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Incluir o dia final completo
        
        # Obter eventos existentes
        existing_events = self.get_events(start_date, end_date)
        
        # Gerar todos os slots possíveis
        all_slots = self._generate_all_slots(start_datetime, end_datetime, duration_minutes)
        
        # Filtrar slots ocupados
        available_slots = self._filter_available_slots(all_slots, existing_events, duration_minutes)
        
        return available_slots
    
    def _generate_all_slots(self, start_datetime: datetime, end_datetime: datetime, duration_minutes: int) -> List[Dict[str, str]]:
        """
        Gera todos os slots possíveis dentro do horário de funcionamento.
        
        Args:
            start_datetime: Data e hora inicial.
            end_datetime: Data e hora final.
            duration_minutes: Duração da consulta em minutos.
            
        Returns:
            Lista de slots no formato {date: YYYY-MM-DD, time: HH:MM}.
        """
        # Horário de funcionamento: 9:00 - 18:00, exceto almoço (12:00 - 13:00)
        business_hours = {
            0: {"start": "09:00", "end": "18:00", "lunch_start": "12:00", "lunch_end": "13:00"},  # Segunda
            1: {"start": "09:00", "end": "18:00", "lunch_start": "12:00", "lunch_end": "13:00"},  # Terça
            2: {"start": "09:00", "end": "18:00", "lunch_start": "12:00", "lunch_end": "13:00"},  # Quarta
            3: {"start": "09:00", "end": "18:00", "lunch_start": "12:00", "lunch_end": "13:00"},  # Quinta
            4: {"start": "09:00", "end": "18:00", "lunch_start": "12:00", "lunch_end": "13:00"},  # Sexta
            5: None,  # Sábado - fechado
            6: None   # Domingo - fechado
        }
        
        all_slots = []
        current_date = start_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        
        while current_date < end_datetime:
            # Verificar se é dia útil
            weekday = current_date.weekday()
            if weekday in business_hours and business_hours[weekday]:
                hours = business_hours[weekday]
                
                # Horário de início
                start_time = datetime.strptime(hours["start"], "%H:%M").time()
                current_slot = datetime.combine(current_date.date(), start_time)
                
                # Horário de término
                end_time = datetime.strptime(hours["end"], "%H:%M").time()
                end_slot = datetime.combine(current_date.date(), end_time)
                
                # Horário de almoço
                lunch_start = datetime.strptime(hours["lunch_start"], "%H:%M").time()
                lunch_start_dt = datetime.combine(current_date.date(), lunch_start)
                
                lunch_end = datetime.strptime(hours["lunch_end"], "%H:%M").time()
                lunch_end_dt = datetime.combine(current_date.date(), lunch_end)
                
                # Gerar slots
                while current_slot < end_slot:
                    # Verificar se está no horário de almoço
                    if current_slot >= lunch_start_dt and current_slot < lunch_end_dt:
                        current_slot = lunch_end_dt
                        continue
                    
                    # Adicionar slot
                    slot_info = {
                        "date": current_slot.strftime("%Y-%m-%d"),
                        "time": current_slot.strftime("%H:%M")
                    }
                    all_slots.append(slot_info)
                    
                    # Avançar para o próximo slot
                    current_slot += timedelta(minutes=duration_minutes)
            
            # Avançar para o próximo dia
            current_date += timedelta(days=1)
        
        return all_slots
    
    def _filter_available_slots(self, all_slots: List[Dict[str, str]], existing_events: List[Dict[str, Any]], duration_minutes: int) -> List[Dict[str, str]]:
        """
        Filtra slots disponíveis removendo os que conflitam com eventos existentes.
        
        Args:
            all_slots: Lista de todos os slots possíveis.
            existing_events: Lista de eventos existentes.
            duration_minutes: Duração da consulta em minutos.
            
        Returns:
            Lista de slots disponíveis.
        """
        available_slots = []
        
        for slot in all_slots:
            slot_date = slot["date"]
            slot_time = slot["time"]
            
            # Converter para datetime
            slot_datetime = datetime.strptime(f"{slot_date} {slot_time}", "%Y-%m-%d %H:%M")
            slot_end_datetime = slot_datetime + timedelta(minutes=duration_minutes)
            
            # Verificar conflitos
            conflict = False
            for event in existing_events:
                event_start = datetime.fromisoformat(event["start"].replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(event["end"].replace("Z", "+00:00"))
                
                # Converter para timezone local se necessário
                if event_start.tzinfo:
                    event_start = event_start.astimezone(None).replace(tzinfo=None)
                if event_end.tzinfo:
                    event_end = event_end.astimezone(None).replace(tzinfo=None)
                
                # Verificar sobreposição
                if (slot_datetime < event_end and slot_end_datetime > event_start):
                    conflict = True
                    break
            
            if not conflict:
                available_slots.append(slot)
        
        return available_slots
    
    def get_events(self, start_date: str, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Obtém eventos de calendário para o período especificado.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD (opcional, padrão: start_date).
            
        Returns:
            Lista de eventos.
        """
        # Se end_date não for fornecido, usar start_date
        if not end_date:
            end_date = start_date
        
        # Converter para formato ISO
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d").isoformat() + "Z"
        end_datetime = (datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).isoformat() + "Z"
        
        all_events = []
        
        # Obter eventos do Google Calendar
        if self.calendar_settings["google"]["enabled"]:
            try:
                google_events = self._get_google_calendar_events(start_datetime, end_datetime)
                all_events.extend(google_events)
            except Exception as e:
                logger.error(f"Erro ao obter eventos do Google Calendar: {str(e)}")
        
        # Obter eventos do Microsoft Outlook
        if self.calendar_settings["outlook"]["enabled"]:
            try:
                outlook_events = self._get_outlook_calendar_events(start_datetime, end_datetime)
                all_events.extend(outlook_events)
            except Exception as e:
                logger.error(f"Erro ao obter eventos do Microsoft Outlook: {str(e)}")
        
        # Obter eventos do Apple Calendar (iCal)
        if self.calendar_settings["ical"]["enabled"]:
            try:
                ical_events = self._get_ical_calendar_events(start_datetime, end_datetime)
                all_events.extend(ical_events)
            except Exception as e:
                logger.error(f"Erro ao obter eventos do Apple Calendar (iCal): {str(e)}")
        
        # Obter agendamentos do banco de dados
        try:
            db_events = self._get_db_appointments(start_date, end_date)
            all_events.extend(db_events)
        except Exception as e:
            logger.error(f"Erro ao obter agendamentos do banco de dados: {str(e)}")
        
        return all_events
    
    def _get_google_calendar_events(self, start_datetime: str, end_datetime: str) -> List[Dict[str, Any]]:
        """
        Obtém eventos do Google Calendar.
        
        Args:
            start_datetime: Data e hora inicial no formato ISO.
            end_datetime: Data e hora final no formato ISO.
            
        Returns:
            Lista de eventos.
        """
        if not self.calendar_settings["google"]["enabled"]:
            return []
        
        try:
            calendar_id = self.calendar_settings["google"]["calendar_id"]
            
            # Obter eventos
            events_result = self.google_calendar.events().list(
                calendarId=calendar_id,
                timeMin=start_datetime,
                timeMax=end_datetime,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
            
            events = events_result.get("items", [])
            
            # Formatar eventos
            formatted_events = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))
                
                formatted_events.append({
                    "id": event["id"],
                    "title": event["summary"],
                    "start": start,
                    "end": end,
                    "source": "google"
                })
            
            return formatted_events
        except Exception as e:
            logger.error(f"Erro ao obter eventos do Google Calendar: {str(e)}")
            return []
    
    def _get_outlook_calendar_events(self, start_datetime: str, end_datetime: str) -> List[Dict[str, Any]]:
        """
        Obtém eventos do Microsoft Outlook Calendar.
        
        Args:
            start_datetime: Data e hora inicial no formato ISO.
            end_datetime: Data e hora final no formato ISO.
            
        Returns:
            Lista de eventos.
        """
        if not self.calendar_settings["outlook"]["enabled"]:
            return []
        
        try:
            # Obter token de acesso
            result = self.outlook_app.acquire_token_for_client(scopes=self.outlook_scopes)
            
            if "access_token" not in result:
                logger.error(f"Erro ao obter token de acesso para Microsoft Outlook: {result.get('error')}")
                return []
            
            # Configurar cabeçalhos
            headers = {
                "Authorization": f"Bearer {result['access_token']}",
                "Content-Type": "application/json"
            }
            
            # Formatar datas para o formato esperado pela API
            start_param = start_datetime.replace("Z", "")
            end_param = end_datetime.replace("Z", "")
            
            # Obter eventos
            url = f"https://graph.microsoft.com/v1.0/me/calendarView?startDateTime={start_param}&endDateTime={end_param}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            events = response.json().get("value", [])
            
            # Formatar eventos
            formatted_events = []
            for event in events:
                formatted_events.append({
                    "id": event["id"],
                    "title": event["subject"],
                    "start": event["start"]["dateTime"] + "Z",
                    "end": event["end"]["dateTime"] + "Z",
                    "source": "outlook"
                })
            
            return formatted_events
        except Exception as e:
            logger.error(f"Erro ao obter eventos do Microsoft Outlook: {str(e)}")
            return []
    
    def _get_ical_calendar_events(self, start_datetime: str, end_datetime: str) -> List[Dict[str, Any]]:
        """
        Obtém eventos do Apple Calendar (iCal).
        
        Args:
            start_datetime: Data e hora inicial no formato ISO.
            end_datetime: Data e hora final no formato ISO.
            
        Returns:
            Lista de eventos.
        """
        if not self.calendar_settings["ical"]["enabled"]:
            return []
        
        try:
            import icalendar
            from dateutil import rrule
            
            url = self.calendar_settings["ical"]["url"]
            
            # Obter calendário
            response = requests.get(url)
            response.raise_for_status()
            
            cal = icalendar.Calendar.from_ical(response.text)
            
            # Converter strings ISO para objetos datetime
            start_dt = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end_datetime.replace("Z", "+00:00"))
            
            # Formatar eventos
            formatted_events = []
            
            for component in cal.walk():
                if component.name == "VEVENT":
                    event_start = component.get("dtstart").dt
                    event_end = component.get("dtend").dt
                    
                    # Converter para datetime se for date
                    if isinstance(event_start, datetime.date) and not isinstance(event_start, datetime.datetime):
                        event_start = datetime.combine(event_start, datetime.min.time())
                    if isinstance(event_end, datetime.date) and not isinstance(event_end, datetime.datetime):
                        event_end = datetime.combine(event_end, datetime.min.time())
                    
                    # Adicionar timezone se não tiver
                    if event_start.tzinfo is None:
                        event_start = event_start.replace(tzinfo=start_dt.tzinfo)
                    if event_end.tzinfo is None:
                        event_end = event_end.replace(tzinfo=end_dt.tzinfo)
                    
                    # Verificar se o evento está no período solicitado
                    if event_end >= start_dt and event_start <= end_dt:
                        formatted_events.append({
                            "id": str(component.get("uid")),
                            "title": str(component.get("summary")),
                            "start": event_start.isoformat(),
                            "end": event_end.isoformat(),
                            "source": "ical"
                        })
                    
                    # Processar eventos recorrentes
                    if "rrule" in component:
                        rrule_str = component.get("rrule").to_ical().decode("utf-8")
                        rule = rrule.rrulestr(rrule_str, dtstart=event_start)
                        
                        # Obter ocorrências no período
                        for occurrence in rule.between(start_dt, end_dt, inc=True):
                            # Calcular duração do evento original
                            duration = event_end - event_start
                            
                            # Calcular fim da ocorrência
                            occurrence_end = occurrence + duration
                            
                            formatted_events.append({
                                "id": f"{str(component.get('uid'))}-{occurrence.isoformat()}",
                                "title": str(component.get("summary")),
                                "start": occurrence.isoformat(),
                                "end": occurrence_end.isoformat(),
                                "source": "ical"
                            })
            
            return formatted_events
        except Exception as e:
            logger.error(f"Erro ao obter eventos do Apple Calendar (iCal): {str(e)}")
            return []
    
    def _get_db_appointments(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Obtém agendamentos do banco de dados.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD.
            
        Returns:
            Lista de agendamentos formatados como eventos.
        """
        try:
            # Obter agendamentos do Supabase
            appointments = self.supabase_manager.get_appointments_by_date_range(start_date, end_date)
            
            # Formatar agendamentos como eventos
            formatted_events = []
            
            for appointment in appointments:
                # Combinar data e hora
                start_datetime = f"{appointment['appointment_date']}T{appointment['appointment_time']}:00"
                
                # Calcular hora de término (padrão: 30 minutos)
                start_dt = datetime.fromisoformat(start_datetime)
                end_dt = start_dt + timedelta(minutes=30)
                
                # Obter dados do paciente
                patient = self.supabase_manager.get_patient_by_id(appointment["patient_id"])
                patient_name = patient.get("name", "Unknown") if patient else "Unknown"
                
                formatted_events.append({
                    "id": str(appointment["id"]),
                    "title": f"Appointment: {patient_name}",
                    "start": start_datetime + "Z",
                    "end": end_dt.isoformat() + "Z",
                    "source": "database",
                    "status": appointment.get("status", "pending"),
                    "patient_id": appointment["patient_id"],
                    "reason": appointment.get("reason", "")
                })
            
            return formatted_events
        except Exception as e:
            logger.error(f"Erro ao obter agendamentos do banco de dados: {str(e)}")
            return []
    
    def create_calendar_event(self, appointment_id: int) -> bool:
        """
        Cria um evento de calendário para um agendamento.
        
        Args:
            appointment_id: ID do agendamento.
            
        Returns:
            True se o evento foi criado com sucesso, False caso contrário.
        """
        try:
            # Obter dados do agendamento
            appointment = self.supabase_manager.get_appointment_by_id(appointment_id)
            
            if not appointment:
                logger.error(f"Agendamento não encontrado: {appointment_id}")
                return False
            
            # Obter dados do paciente
            patient = self.supabase_manager.get_patient_by_id(appointment["patient_id"])
            
            if not patient:
                logger.error(f"Paciente não encontrado: {appointment['patient_id']}")
                return False
            
            # Combinar data e hora
            start_datetime = f"{appointment['appointment_date']}T{appointment['appointment_time']}:00"
            
            # Calcular hora de término (padrão: 30 minutos)
            start_dt = datetime.fromisoformat(start_datetime)
            end_dt = start_dt + timedelta(minutes=30)
            
            # Criar evento no Google Calendar
            if self.calendar_settings["google"]["enabled"]:
                try:
                    self._create_google_calendar_event(
                        patient["name"],
                        appointment.get("reason", ""),
                        start_dt.isoformat() + "Z",
                        end_dt.isoformat() + "Z"
                    )
                    logger.info(f"Evento criado no Google Calendar para o agendamento {appointment_id}")
                    return True
                except Exception as e:
                    logger.error(f"Erro ao criar evento no Google Calendar: {str(e)}")
            
            # Criar evento no Microsoft Outlook
            if self.calendar_settings["outlook"]["enabled"]:
                try:
                    self._create_outlook_calendar_event(
                        patient["name"],
                        appointment.get("reason", ""),
                        start_dt.isoformat(),
                        end_dt.isoformat()
                    )
                    logger.info(f"Evento criado no Microsoft Outlook para o agendamento {appointment_id}")
                    return True
                except Exception as e:
                    logger.error(f"Erro ao criar evento no Microsoft Outlook: {str(e)}")
            
            # Apple Calendar (iCal) é somente leitura via URL
            
            logger.warning("Nenhum calendário configurado para criação de eventos.")
            return False
        except Exception as e:
            logger.error(f"Erro ao criar evento de calendário: {str(e)}")
            return False
    
    def _create_google_calendar_event(self, summary: str, description: str, start_time: str, end_time: str) -> str:
        """
        Cria um evento no Google Calendar.
        
        Args:
            summary: Título do evento.
            description: Descrição do evento.
            start_time: Hora de início no formato ISO.
            end_time: Hora de término no formato ISO.
            
        Returns:
            ID do evento criado.
        """
        if not self.calendar_settings["google"]["enabled"]:
            raise Exception("Google Calendar não está habilitado.")
        
        calendar_id = self.calendar_settings["google"]["calendar_id"]
        
        event = {
            "summary": summary,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Tokyo"
            }
        }
        
        event = self.google_calendar.events().insert(calendarId=calendar_id, body=event).execute()
        return event["id"]
    
    def _create_outlook_calendar_event(self, summary: str, description: str, start_time: str, end_time: str) -> str:
        """
        Cria um evento no Microsoft Outlook Calendar.
        
        Args:
            summary: Título do evento.
            description: Descrição do evento.
            start_time: Hora de início no formato ISO.
            end_time: Hora de término no formato ISO.
            
        Returns:
            ID do evento criado.
        """
        if not self.calendar_settings["outlook"]["enabled"]:
            raise Exception("Microsoft Outlook não está habilitado.")
        
        # Obter token de acesso
        result = self.outlook_app.acquire_token_for_client(scopes=self.outlook_scopes)
        
        if "access_token" not in result:
            raise Exception(f"Erro ao obter token de acesso: {result.get('error')}")
        
        # Configurar cabeçalhos
        headers = {
            "Authorization": f"Bearer {result['access_token']}",
            "Content-Type": "application/json"
        }
        
        # Criar evento
        event = {
            "subject": summary,
            "body": {
                "contentType": "text",
                "content": description
            },
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Tokyo"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Tokyo"
            }
        }
        
        # Enviar requisição
        url = "https://graph.microsoft.com/v1.0/me/events"
        response = requests.post(url, headers=headers, json=event)
        response.raise_for_status()
        
        return response.json()["id"]
    
    def update_appointment_status(self, appointment_id: int, status: str) -> bool:
        """
        Atualiza o status de um agendamento e sincroniza com o calendário.
        
        Args:
            appointment_id: ID do agendamento.
            status: Novo status (confirmed, cancelled, rescheduled).
            
        Returns:
            True se a atualização foi bem-sucedida, False caso contrário.
        """
        try:
            # Atualizar status no banco de dados
            success = self.supabase_manager.update_appointment_status(appointment_id, status)
            
            if not success:
                logger.error(f"Erro ao atualizar status do agendamento {appointment_id}")
                return False
            
            # Se confirmado, criar evento no calendário
            if status == "confirmed":
                self.create_calendar_event(appointment_id)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar status do agendamento: {str(e)}")
            return False
    
    def get_calendar_integration_status(self) -> Dict[str, bool]:
        """
        Obtém o status de integração com calendários.
        
        Returns:
            Dicionário com status de cada integração.
        """
        return {
            "google": self.calendar_settings["google"]["enabled"],
            "outlook": self.calendar_settings["outlook"]["enabled"],
            "ical": self.calendar_settings["ical"]["enabled"]
        }
