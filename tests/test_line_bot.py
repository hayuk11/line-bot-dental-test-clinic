import unittest
import os
import sys
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Adicionar diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos para teste
from line_bot.translation_manager import TranslationManager
from line_bot.conversation_manager import ConversationManager
from line_bot.calendar_manager import CalendarManager
from line_bot.reporting_manager import ReportingManager
from line_bot.line_manager import LineManager
from line_bot.supabase_manager import SupabaseManager

class TestTranslationManager(unittest.TestCase):
    """Testes para o gerenciador de traduções."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para OpenAI API
        self.openai_patcher = patch('openai.ChatCompletion.create')
        self.mock_openai = self.openai_patcher.start()
        
        # Configurar resposta mock
        self.mock_openai.return_value = {
            'choices': [{'message': {'content': 'Texto traduzido'}}]
        }
        
        # Inicializar gerenciador de traduções
        self.translation_manager = TranslationManager()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.openai_patcher.stop()
    
    def test_detect_language(self):
        """Testa a detecção de idioma."""
        # Configurar resposta mock para detecção de idioma
        self.mock_openai.return_value = {
            'choices': [{'message': {'content': 'japanese'}}]
        }
        
        # Testar detecção de idioma
        language = self.translation_manager.detect_language("こんにちは")
        
        # Verificar se a API foi chamada corretamente
        self.mock_openai.assert_called_once()
        
        # Verificar resultado
        self.assertEqual(language, "japanese")
    
    def test_translate_text(self):
        """Testa a tradução de texto."""
        # Configurar resposta mock para tradução
        self.mock_openai.return_value = {
            'choices': [{'message': {'content': 'Hello'}}]
        }
        
        # Testar tradução
        translated = self.translation_manager.translate_text("こんにちは", "japanese", "english")
        
        # Verificar se a API foi chamada corretamente
        self.mock_openai.assert_called_once()
        
        # Verificar resultado
        self.assertEqual(translated, "Hello")
    
    def test_get_multilingual_message(self):
        """Testa a geração de mensagens multilíngues."""
        # Configurar respostas mock para traduções
        self.mock_openai.side_effect = [
            {'choices': [{'message': {'content': 'Hello'}}]},
            {'choices': [{'message': {'content': 'Olá'}}]},
            {'choices': [{'message': {'content': '你好'}}]}
        ]
        
        # Testar geração de mensagem multilíngue
        message = self.translation_manager.get_multilingual_message(
            "こんにちは",
            "japanese",
            ["english", "portuguese", "chinese"]
        )
        
        # Verificar se a API foi chamada corretamente
        self.assertEqual(self.mock_openai.call_count, 3)
        
        # Verificar resultado
        self.assertIn("Hello", message)
        self.assertIn("Olá", message)
        self.assertIn("你好", message)
        self.assertIn("こんにちは", message)


class TestConversationManager(unittest.TestCase):
    """Testes para o gerenciador de conversas."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mocks para dependências
        self.line_manager = MagicMock()
        self.supabase_manager = MagicMock()
        self.translation_manager = MagicMock()
        self.calendar_manager = MagicMock()
        
        # Inicializar gerenciador de conversas
        self.conversation_manager = ConversationManager(
            self.line_manager,
            self.supabase_manager,
            self.translation_manager,
            self.calendar_manager
        )
    
    def test_handle_text_message(self):
        """Testa o processamento de mensagens de texto."""
        # Configurar mocks
        self.translation_manager.detect_language.return_value = "english"
        self.supabase_manager.get_user_state.return_value = None
        
        # Testar processamento de mensagem inicial
        self.conversation_manager.handle_text_message("user123", "Hello")
        
        # Verificar se as funções corretas foram chamadas
        self.translation_manager.detect_language.assert_called_once_with("Hello")
        self.supabase_manager.get_user_state.assert_called_once_with("user123")
        self.line_manager.send_welcome_message.assert_called_once()
    
    def test_handle_postback(self):
        """Testa o processamento de eventos postback."""
        # Configurar mocks
        self.supabase_manager.get_user_state.return_value = {
            "state": "language_selection",
            "language": None
        }
        
        # Testar processamento de postback
        self.conversation_manager.handle_postback("user123", "language=english")
        
        # Verificar se as funções corretas foram chamadas
        self.supabase_manager.get_user_state.assert_called_once_with("user123")
        self.supabase_manager.update_user_state.assert_called_once()
        self.line_manager.send_message.assert_called_once()
    
    def test_process_appointment_request(self):
        """Testa o processamento de solicitação de agendamento."""
        # Configurar mocks
        self.supabase_manager.get_user_state.return_value = {
            "state": "main_menu",
            "language": "english"
        }
        
        # Testar processamento de solicitação de agendamento
        self.conversation_manager.process_appointment_request("user123")
        
        # Verificar se as funções corretas foram chamadas
        self.supabase_manager.update_user_state.assert_called_once()
        self.line_manager.send_message.assert_called_once()
    
    def test_validate_date_format(self):
        """Testa a validação de formato de data."""
        # Testar data válida
        valid_date = "2025-05-01"
        self.assertTrue(self.conversation_manager.validate_date_format(valid_date))
        
        # Testar data inválida
        invalid_date = "01/05/2025"
        self.assertFalse(self.conversation_manager.validate_date_format(invalid_date))
        
        # Testar data futura
        past_date = "2020-01-01"
        self.assertFalse(self.conversation_manager.validate_date_format(past_date))


class TestCalendarManager(unittest.TestCase):
    """Testes para o gerenciador de calendário."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para Supabase
        self.supabase_manager = MagicMock()
        
        # Inicializar gerenciador de calendário
        self.calendar_manager = CalendarManager(self.supabase_manager)
    
    def test_get_available_slots(self):
        """Testa a obtenção de slots disponíveis."""
        # Configurar mock para eventos existentes
        self.calendar_manager.get_events = MagicMock(return_value=[
            {
                "start": "2025-05-01T10:00:00Z",
                "end": "2025-05-01T10:30:00Z"
            }
        ])
        
        # Testar obtenção de slots disponíveis
        slots = self.calendar_manager.get_available_slots("2025-05-01")
        
        # Verificar se a função foi chamada corretamente
        self.calendar_manager.get_events.assert_called_once_with("2025-05-01", "2025-05-01")
        
        # Verificar que o slot ocupado não está nos resultados
        for slot in slots:
            if slot["date"] == "2025-05-01" and slot["time"] == "10:00":
                self.fail("Slot ocupado não deveria estar disponível")
    
    def test_update_appointment_status(self):
        """Testa a atualização de status de agendamento."""
        # Configurar mocks
        self.supabase_manager.update_appointment_status.return_value = True
        self.calendar_manager.create_calendar_event = MagicMock(return_value=True)
        
        # Testar atualização de status
        result = self.calendar_manager.update_appointment_status(123, "confirmed")
        
        # Verificar se as funções corretas foram chamadas
        self.supabase_manager.update_appointment_status.assert_called_once_with(123, "confirmed")
        self.calendar_manager.create_calendar_event.assert_called_once_with(123)
        
        # Verificar resultado
        self.assertTrue(result)


class TestReportingManager(unittest.TestCase):
    """Testes para o gerenciador de relatórios."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para Supabase
        self.supabase_manager = MagicMock()
        
        # Inicializar gerenciador de relatórios
        self.reporting_manager = ReportingManager(self.supabase_manager)
    
    def test_generate_appointment_report(self):
        """Testa a geração de relatório de agendamentos."""
        # Configurar mock para agendamentos
        self.supabase_manager.get_appointments_by_date_range.return_value = [
            {
                "id": 1,
                "patient_id": 101,
                "appointment_date": "2025-05-01",
                "appointment_time": "10:00",
                "status": "confirmed",
                "reason": "Consulta de rotina"
            },
            {
                "id": 2,
                "patient_id": 102,
                "appointment_date": "2025-05-01",
                "appointment_time": "11:00",
                "status": "pending",
                "reason": "Dor de cabeça"
            }
        ]
        
        # Testar geração de relatório
        report = self.reporting_manager.generate_appointment_report("2025-05-01", "2025-05-31")
        
        # Verificar se a função foi chamada corretamente
        self.supabase_manager.get_appointments_by_date_range.assert_called_once_with("2025-05-01", "2025-05-31", None)
        
        # Verificar resultado
        self.assertTrue(report["success"])
        self.assertEqual(report["summary"]["total_appointments"], 2)
        self.assertEqual(report["summary"]["confirmed_appointments"], 1)
        self.assertEqual(report["summary"]["pending_appointments"], 1)
    
    def test_generate_dashboard_summary(self):
        """Testa a geração de resumo para dashboard."""
        # Configurar mocks
        self.supabase_manager.get_appointments_by_date_range.return_value = [
            {
                "id": 1,
                "patient_id": 101,
                "appointment_date": "2025-05-01",
                "appointment_time": "10:00",
                "status": "confirmed"
            }
        ]
        
        self.supabase_manager.get_all_patients.return_value = [
            {
                "id": 101,
                "name": "John Doe",
                "preferred_language": "english",
                "created_at": "2025-04-01T00:00:00"
            }
        ]
        
        self.supabase_manager.get_patient_by_id.return_value = {
            "id": 101,
            "name": "John Doe",
            "preferred_language": "english"
        }
        
        # Testar geração de resumo
        summary = self.reporting_manager.generate_dashboard_summary(30)
        
        # Verificar resultado
        self.assertTrue(summary["success"])
        self.assertEqual(summary["appointments"]["total"], 1)
        self.assertEqual(summary["patients"]["total"], 1)


class TestLineManager(unittest.TestCase):
    """Testes para o gerenciador LINE."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para LINE API
        self.line_bot_api_patcher = patch('line_bot_sdk.LineBotApi')
        self.mock_line_bot_api = self.line_bot_api_patcher.start()
        
        # Inicializar gerenciador LINE
        self.line_manager = LineManager()
        
        # Substituir o cliente LINE pelo mock
        self.line_manager.line_bot_api = self.mock_line_bot_api
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.line_bot_api_patcher.stop()
    
    def test_send_message(self):
        """Testa o envio de mensagem."""
        # Testar envio de mensagem
        self.line_manager.send_message("user123", "Hello")
        
        # Verificar se a API foi chamada corretamente
        self.mock_line_bot_api.push_message.assert_called_once()
    
    def test_send_welcome_message(self):
        """Testa o envio de mensagem de boas-vindas."""
        # Testar envio de mensagem de boas-vindas
        self.line_manager.send_welcome_message("user123")
        
        # Verificar se a API foi chamada corretamente
        self.mock_line_bot_api.push_message.assert_called_once()
    
    def test_send_quick_reply(self):
        """Testa o envio de quick reply."""
        # Testar envio de quick reply
        self.line_manager.send_quick_reply(
            "user123",
            "Please select an option",
            [
                {"label": "Option 1", "text": "option1"},
                {"label": "Option 2", "text": "option2"}
            ]
        )
        
        # Verificar se a API foi chamada corretamente
        self.mock_line_bot_api.push_message.assert_called_once()


class TestSupabaseManager(unittest.TestCase):
    """Testes para o gerenciador Supabase."""
    
    def setUp(self):
        """Configuração para cada teste."""
        # Mock para Supabase
        self.supabase_patcher = patch('supabase.create_client')
        self.mock_supabase = self.supabase_patcher.start()
        
        # Configurar mock para cliente Supabase
        self.mock_client = MagicMock()
        self.mock_supabase.return_value = self.mock_client
        
        # Configurar mock para tabelas
        self.mock_table = MagicMock()
        self.mock_client.table.return_value = self.mock_table
        
        # Inicializar gerenciador Supabase
        self.supabase_manager = SupabaseManager()
        
        # Substituir o cliente Supabase pelo mock
        self.supabase_manager.supabase = self.mock_client
    
    def tearDown(self):
        """Limpeza após cada teste."""
        self.supabase_patcher.stop()
    
    def test_get_user_state(self):
        """Testa a obtenção de estado do usuário."""
        # Configurar mock para resposta
        self.mock_table.select.return_value.eq.return_value.execute.return_value = {
            "data": [{"user_id": "user123", "state": "main_menu", "language": "english"}]
        }
        
        # Testar obtenção de estado
        state = self.supabase_manager.get_user_state("user123")
        
        # Verificar se a API foi chamada corretamente
        self.mock_client.table.assert_called_once_with("user_states")
        
        # Verificar resultado
        self.assertEqual(state["state"], "main_menu")
        self.assertEqual(state["language"], "english")
    
    def test_update_user_state(self):
        """Testa a atualização de estado do usuário."""
        # Configurar mock para resposta
        self.mock_table.upsert.return_value.execute.return_value = {
            "data": [{"user_id": "user123", "state": "appointment_date", "language": "english"}]
        }
        
        # Testar atualização de estado
        state = {
            "state": "appointment_date",
            "language": "english"
        }
        result = self.supabase_manager.update_user_state("user123", state)
        
        # Verificar se a API foi chamada corretamente
        self.mock_client.table.assert_called_once_with("user_states")
        
        # Verificar resultado
        self.assertTrue(result)
    
    def test_create_appointment(self):
        """Testa a criação de agendamento."""
        # Configurar mock para resposta
        self.mock_table.insert.return_value.execute.return_value = {
            "data": [{"id": 1}]
        }
        
        # Testar criação de agendamento
        appointment_data = {
            "patient_id": 101,
            "appointment_date": "2025-05-01",
            "appointment_time": "10:00",
            "reason": "Consulta de rotina",
            "status": "pending"
        }
        result = self.supabase_manager.create_appointment(appointment_data)
        
        # Verificar se a API foi chamada corretamente
        self.mock_client.table.assert_called_once_with("appointments")
        
        # Verificar resultado
        self.assertEqual(result, 1)


if __name__ == '__main__':
    unittest.main()
