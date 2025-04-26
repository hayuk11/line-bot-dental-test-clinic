import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ReportingManager:
    """
    Gerenciador de relatórios e estatísticas para o chatbot LINE.
    Gera relatórios sobre agendamentos, pacientes e uso do sistema.
    """
    
    def __init__(self, supabase_manager):
        """
        Inicializa o gerenciador de relatórios.
        
        Args:
            supabase_manager: Instância do gerenciador do Supabase.
        """
        self.supabase_manager = supabase_manager
        
        # Configurar estilo dos gráficos
        self._setup_plot_style()
    
    def _setup_plot_style(self):
        """
        Configura o estilo dos gráficos para relatórios.
        """
        # Configurar estilo Seaborn
        sns.set(style="whitegrid")
        
        # Configurar estilo Matplotlib
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.labelsize'] = 14
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 12
        plt.rcParams['ytick.labelsize'] = 12
        plt.rcParams['legend.fontsize'] = 12
        plt.rcParams['figure.titlesize'] = 18
    
    def generate_appointment_report(self, start_date: str, end_date: str, clinic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera relatório de agendamentos para o período especificado.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD.
            clinic_id: ID da clínica (opcional, para sistemas multi-clínica).
            
        Returns:
            Dicionário com dados do relatório e gráficos codificados em base64.
        """
        try:
            # Obter agendamentos do período
            appointments = self.supabase_manager.get_appointments_by_date_range(start_date, end_date, clinic_id)
            
            if not appointments:
                return {
                    "success": False,
                    "message": "Nenhum agendamento encontrado no período especificado.",
                    "data": None
                }
            
            # Converter para DataFrame
            df = pd.DataFrame(appointments)
            
            # Adicionar colunas de data e hora formatadas
            df['date'] = pd.to_datetime(df['appointment_date'])
            df['time'] = pd.to_datetime(df['appointment_time'], format='%H:%M').dt.time
            df['day_of_week'] = df['date'].dt.day_name()
            df['month'] = df['date'].dt.month_name()
            df['hour'] = pd.to_datetime(df['appointment_time'], format='%H:%M').dt.hour
            
            # Estatísticas gerais
            total_appointments = len(df)
            confirmed_appointments = len(df[df['status'] == 'confirmed'])
            cancelled_appointments = len(df[df['status'] == 'cancelled'])
            pending_appointments = len(df[df['status'] == 'pending'])
            
            confirmation_rate = (confirmed_appointments / total_appointments) * 100 if total_appointments > 0 else 0
            cancellation_rate = (cancelled_appointments / total_appointments) * 100 if total_appointments > 0 else 0
            
            # Agendamentos por dia da semana
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            appointments_by_day = df['day_of_week'].value_counts().reindex(day_order).fillna(0).to_dict()
            
            # Agendamentos por hora do dia
            appointments_by_hour = df['hour'].value_counts().sort_index().to_dict()
            
            # Agendamentos por mês
            month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                          'July', 'August', 'September', 'October', 'November', 'December']
            appointments_by_month = df['month'].value_counts().reindex(month_order).fillna(0).to_dict()
            
            # Agendamentos por status
            appointments_by_status = df['status'].value_counts().to_dict()
            
            # Gerar gráficos
            graphs = {}
            
            # Gráfico de agendamentos por dia da semana
            graphs['appointments_by_day'] = self._create_bar_chart(
                appointments_by_day, 
                'Agendamentos por Dia da Semana', 
                'Dia da Semana', 
                'Número de Agendamentos'
            )
            
            # Gráfico de agendamentos por hora
            graphs['appointments_by_hour'] = self._create_bar_chart(
                appointments_by_hour, 
                'Agendamentos por Hora do Dia', 
                'Hora do Dia', 
                'Número de Agendamentos'
            )
            
            # Gráfico de agendamentos por status
            graphs['appointments_by_status'] = self._create_pie_chart(
                appointments_by_status, 
                'Distribuição de Status de Agendamentos'
            )
            
            # Gráfico de agendamentos por mês
            graphs['appointments_by_month'] = self._create_bar_chart(
                appointments_by_month, 
                'Agendamentos por Mês', 
                'Mês', 
                'Número de Agendamentos'
            )
            
            # Compilar relatório
            report = {
                "success": True,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_appointments": total_appointments,
                    "confirmed_appointments": confirmed_appointments,
                    "cancelled_appointments": cancelled_appointments,
                    "pending_appointments": pending_appointments,
                    "confirmation_rate": round(confirmation_rate, 2),
                    "cancellation_rate": round(cancellation_rate, 2)
                },
                "distributions": {
                    "by_day": appointments_by_day,
                    "by_hour": appointments_by_hour,
                    "by_month": appointments_by_month,
                    "by_status": appointments_by_status
                },
                "graphs": graphs
            }
            
            return report
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de agendamentos: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao gerar relatório: {str(e)}",
                "data": None
            }
    
    def generate_patient_report(self, start_date: Optional[str] = None, end_date: Optional[str] = None, clinic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera relatório de pacientes.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD (opcional).
            end_date: Data final no formato YYYY-MM-DD (opcional).
            clinic_id: ID da clínica (opcional, para sistemas multi-clínica).
            
        Returns:
            Dicionário com dados do relatório e gráficos codificados em base64.
        """
        try:
            # Obter todos os pacientes
            patients = self.supabase_manager.get_all_patients(clinic_id)
            
            if not patients:
                return {
                    "success": False,
                    "message": "Nenhum paciente encontrado.",
                    "data": None
                }
            
            # Converter para DataFrame
            df = pd.DataFrame(patients)
            
            # Adicionar coluna de data de criação formatada
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['month_created'] = df['created_at'].dt.month_name()
                df['year_created'] = df['created_at'].dt.year
            
            # Filtrar por período, se especificado
            if start_date and end_date:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                df_filtered = df[(df['created_at'] >= start_dt) & (df['created_at'] <= end_dt)]
            else:
                df_filtered = df
            
            # Estatísticas gerais
            total_patients = len(df)
            new_patients = len(df_filtered) if start_date and end_date else total_patients
            
            # Pacientes por idioma preferido
            patients_by_language = df['preferred_language'].value_counts().to_dict()
            
            # Pacientes por mês de criação (se houver data de criação)
            patients_by_month = {}
            if 'month_created' in df.columns:
                month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                              'July', 'August', 'September', 'October', 'November', 'December']
                patients_by_month = df_filtered['month_created'].value_counts().reindex(month_order).fillna(0).to_dict()
            
            # Número médio de agendamentos por paciente
            appointments = self.supabase_manager.get_all_appointments(clinic_id)
            if appointments:
                appointments_df = pd.DataFrame(appointments)
                appointments_per_patient = appointments_df.groupby('patient_id').size()
                avg_appointments_per_patient = appointments_per_patient.mean()
                max_appointments_per_patient = appointments_per_patient.max()
            else:
                avg_appointments_per_patient = 0
                max_appointments_per_patient = 0
            
            # Gerar gráficos
            graphs = {}
            
            # Gráfico de pacientes por idioma
            graphs['patients_by_language'] = self._create_pie_chart(
                patients_by_language, 
                'Distribuição de Pacientes por Idioma'
            )
            
            # Gráfico de novos pacientes por mês
            if patients_by_month:
                graphs['patients_by_month'] = self._create_bar_chart(
                    patients_by_month, 
                    'Novos Pacientes por Mês', 
                    'Mês', 
                    'Número de Pacientes'
                )
            
            # Compilar relatório
            report = {
                "success": True,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                } if start_date and end_date else None,
                "summary": {
                    "total_patients": total_patients,
                    "new_patients": new_patients,
                    "avg_appointments_per_patient": round(avg_appointments_per_patient, 2),
                    "max_appointments_per_patient": max_appointments_per_patient
                },
                "distributions": {
                    "by_language": patients_by_language,
                    "by_month": patients_by_month if patients_by_month else None
                },
                "graphs": graphs
            }
            
            return report
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de pacientes: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao gerar relatório: {str(e)}",
                "data": None
            }
    
    def generate_usage_report(self, start_date: str, end_date: str, clinic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera relatório de uso do chatbot.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD.
            clinic_id: ID da clínica (opcional, para sistemas multi-clínica).
            
        Returns:
            Dicionário com dados do relatório e gráficos codificados em base64.
        """
        try:
            # Obter logs de uso do período
            usage_logs = self.supabase_manager.get_usage_logs(start_date, end_date, clinic_id)
            
            if not usage_logs:
                return {
                    "success": False,
                    "message": "Nenhum log de uso encontrado no período especificado.",
                    "data": None
                }
            
            # Converter para DataFrame
            df = pd.DataFrame(usage_logs)
            
            # Adicionar colunas de data e hora formatadas
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.day_name()
            
            # Estatísticas gerais
            total_interactions = len(df)
            unique_users = df['line_user_id'].nunique()
            
            # Interações por tipo
            interactions_by_type = df['interaction_type'].value_counts().to_dict()
            
            # Interações por dia da semana
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            interactions_by_day = df['day_of_week'].value_counts().reindex(day_order).fillna(0).to_dict()
            
            # Interações por hora do dia
            interactions_by_hour = df['hour'].value_counts().sort_index().to_dict()
            
            # Interações por idioma
            interactions_by_language = df['language'].value_counts().to_dict()
            
            # Tempo médio de conversa
            avg_conversation_time = 0
            if 'conversation_duration' in df.columns:
                avg_conversation_time = df['conversation_duration'].mean()
            
            # Gerar gráficos
            graphs = {}
            
            # Gráfico de interações por tipo
            graphs['interactions_by_type'] = self._create_pie_chart(
                interactions_by_type, 
                'Distribuição de Interações por Tipo'
            )
            
            # Gráfico de interações por dia da semana
            graphs['interactions_by_day'] = self._create_bar_chart(
                interactions_by_day, 
                'Interações por Dia da Semana', 
                'Dia da Semana', 
                'Número de Interações'
            )
            
            # Gráfico de interações por hora
            graphs['interactions_by_hour'] = self._create_bar_chart(
                interactions_by_hour, 
                'Interações por Hora do Dia', 
                'Hora do Dia', 
                'Número de Interações'
            )
            
            # Gráfico de interações por idioma
            graphs['interactions_by_language'] = self._create_pie_chart(
                interactions_by_language, 
                'Distribuição de Interações por Idioma'
            )
            
            # Compilar relatório
            report = {
                "success": True,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_interactions": total_interactions,
                    "unique_users": unique_users,
                    "avg_conversation_time": round(avg_conversation_time, 2) if avg_conversation_time else None
                },
                "distributions": {
                    "by_type": interactions_by_type,
                    "by_day": interactions_by_day,
                    "by_hour": interactions_by_hour,
                    "by_language": interactions_by_language
                },
                "graphs": graphs
            }
            
            return report
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de uso: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao gerar relatório: {str(e)}",
                "data": None
            }
    
    def generate_performance_report(self, start_date: str, end_date: str, clinic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera relatório de desempenho do sistema.
        
        Args:
            start_date: Data inicial no formato YYYY-MM-DD.
            end_date: Data final no formato YYYY-MM-DD.
            clinic_id: ID da clínica (opcional, para sistemas multi-clínica).
            
        Returns:
            Dicionário com dados do relatório e gráficos codificados em base64.
        """
        try:
            # Obter logs de desempenho do período
            performance_logs = self.supabase_manager.get_performance_logs(start_date, end_date, clinic_id)
            
            if not performance_logs:
                return {
                    "success": False,
                    "message": "Nenhum log de desempenho encontrado no período especificado.",
                    "data": None
                }
            
            # Converter para DataFrame
            df = pd.DataFrame(performance_logs)
            
            # Adicionar colunas de data e hora formatadas
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
            # Estatísticas gerais
            total_requests = len(df)
            avg_response_time = df['response_time'].mean() if 'response_time' in df.columns else None
            error_count = len(df[df['status'] == 'error']) if 'status' in df.columns else 0
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            # Tempo de resposta por hora
            response_time_by_hour = df.groupby('hour')['response_time'].mean().to_dict() if 'response_time' in df.columns else {}
            
            # Erros por tipo
            errors_by_type = df[df['status'] == 'error']['error_type'].value_counts().to_dict() if 'error_type' in df.columns else {}
            
            # Gerar gráficos
            graphs = {}
            
            # Gráfico de tempo de resposta por hora
            if response_time_by_hour:
                graphs['response_time_by_hour'] = self._create_line_chart(
                    response_time_by_hour, 
                    'Tempo Médio de Resposta por Hora', 
                    'Hora do Dia', 
                    'Tempo de Resposta (ms)'
                )
            
            # Gráfico de erros por tipo
            if errors_by_type:
                graphs['errors_by_type'] = self._create_pie_chart(
                    errors_by_type, 
                    'Distribuição de Erros por Tipo'
                )
            
            # Compilar relatório
            report = {
                "success": True,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "summary": {
                    "total_requests": total_requests,
                    "avg_response_time": round(avg_response_time, 2) if avg_response_time else None,
                    "error_count": error_count,
                    "error_rate": round(error_rate, 2)
                },
                "distributions": {
                    "response_time_by_hour": response_time_by_hour,
                    "errors_by_type": errors_by_type
                },
                "graphs": graphs
            }
            
            return report
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de desempenho: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao gerar relatório: {str(e)}",
                "data": None
            }
    
    def generate_dashboard_summary(self, days: int = 30, clinic_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gera um resumo para o dashboard.
        
        Args:
            days: Número de dias para incluir no resumo (padrão: 30).
            clinic_id: ID da clínica (opcional, para sistemas multi-clínica).
            
        Returns:
            Dicionário com dados do resumo.
        """
        try:
            # Calcular datas
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Obter dados de agendamentos
            appointments = self.supabase_manager.get_appointments_by_date_range(start_date, end_date, clinic_id)
            
            # Obter dados de pacientes
            patients = self.supabase_manager.get_all_patients(clinic_id)
            
            # Calcular estatísticas
            total_appointments = len(appointments) if appointments else 0
            total_patients = len(patients) if patients else 0
            
            # Agendamentos por status
            appointments_by_status = {}
            if appointments:
                df_appointments = pd.DataFrame(appointments)
                appointments_by_status = df_appointments['status'].value_counts().to_dict()
            
            # Novos pacientes no período
            new_patients = 0
            if patients and 'created_at' in patients[0]:
                df_patients = pd.DataFrame(patients)
                df_patients['created_at'] = pd.to_datetime(df_patients['created_at'])
                new_patients = len(df_patients[df_patients['created_at'] >= pd.to_datetime(start_date)])
            
            # Próximos agendamentos
            upcoming_appointments = []
            if appointments:
                df_appointments = pd.DataFrame(appointments)
                df_appointments['date'] = pd.to_datetime(df_appointments['appointment_date'])
                df_appointments['time'] = df_appointments['appointment_time']
                
                # Filtrar agendamentos futuros e confirmados
                today = datetime.now().date()
                future_appointments = df_appointments[
                    (df_appointments['date'].dt.date >= today) & 
                    (df_appointments['status'] == 'confirmed')
                ]
                
                # Ordenar por data e hora
                future_appointments = future_appointments.sort_values(by=['date', 'time'])
                
                # Obter os próximos 5 agendamentos
                for _, row in future_appointments.head(5).iterrows():
                    patient = self.supabase_manager.get_patient_by_id(row['patient_id'])
                    patient_name = patient.get('name', 'Unknown') if patient else 'Unknown'
                    
                    upcoming_appointments.append({
                        'id': row['id'],
                        'date': row['appointment_date'],
                        'time': row['appointment_time'],
                        'patient_name': patient_name,
                        'reason': row.get('reason', '')
                    })
            
            # Compilar resumo
            summary = {
                "success": True,
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": days
                },
                "appointments": {
                    "total": total_appointments,
                    "by_status": appointments_by_status,
                    "upcoming": upcoming_appointments
                },
                "patients": {
                    "total": total_patients,
                    "new": new_patients
                }
            }
            
            return summary
        except Exception as e:
            logger.error(f"Erro ao gerar resumo do dashboard: {str(e)}")
            return {
                "success": False,
                "message": f"Erro ao gerar resumo: {str(e)}",
                "data": None
            }
    
    def export_report_to_pdf(self, report_type: str, report_data: Dict[str, Any], output_file: str) -> bool:
        """
        Exporta um relatório para PDF.
        
        Args:
            report_type: Tipo de relatório ('appointment', 'patient', 'usage', 'performance').
            report_data: Dados do relatório.
            output_file: Caminho do arquivo de saída.
            
        Returns:
            True se a exportação foi bem-sucedida, False caso contrário.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Verificar se o relatório foi gerado com sucesso
            if not report_data.get('success', False):
                logger.error(f"Não é possível exportar relatório com erro: {report_data.get('message', 'Unknown error')}")
                return False
            
            # Criar documento PDF
            doc = SimpleDocTemplate(output_file, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Adicionar estilo personalizado para título
            styles.add(ParagraphStyle(
                name='Title',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=12
            ))
            
            # Adicionar estilo personalizado para subtítulo
            styles.add(ParagraphStyle(
                name='Subtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=6
            ))
            
            # Elementos do documento
            elements = []
            
            # Título do relatório
            title_text = f"Relatório de {self._get_report_title(report_type)}"
            elements.append(Paragraph(title_text, styles['Title']))
            elements.append(Spacer(1, 0.25 * inch))
            
            # Período do relatório
            if report_data.get('period'):
                period_text = f"Período: {report_data['period']['start_date']} a {report_data['period']['end_date']}"
                elements.append(Paragraph(period_text, styles['Normal']))
                elements.append(Spacer(1, 0.25 * inch))
            
            # Resumo
            elements.append(Paragraph("Resumo", styles['Subtitle']))
            
            # Criar tabela de resumo
            summary_data = [['Métrica', 'Valor']]
            for key, value in report_data.get('summary', {}).items():
                # Formatar chave para exibição
                display_key = key.replace('_', ' ').title()
                summary_data.append([display_key, str(value)])
            
            summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.25 * inch))
            
            # Adicionar gráficos
            if report_data.get('graphs'):
                elements.append(Paragraph("Gráficos", styles['Subtitle']))
                
                for graph_name, graph_data in report_data['graphs'].items():
                    # Decodificar imagem base64
                    image_data = base64.b64decode(graph_data.split(',')[1])
                    
                    # Salvar temporariamente
                    temp_image_path = f"/tmp/{graph_name}.png"
                    with open(temp_image_path, 'wb') as f:
                        f.write(image_data)
                    
                    # Adicionar ao documento
                    img = Image(temp_image_path, width=6*inch, height=4*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.25 * inch))
                    
                    # Remover arquivo temporário
                    os.remove(temp_image_path)
            
            # Construir documento
            doc.build(elements)
            
            logger.info(f"Relatório exportado com sucesso para {output_file}")
            return True
        except ImportError:
            logger.error("Biblioteca ReportLab não instalada. Execute: pip install reportlab")
            return False
        except Exception as e:
            logger.error(f"Erro ao exportar relatório para PDF: {str(e)}")
            return False
    
    def export_report_to_excel(self, report_type: str, report_data: Dict[str, Any], output_file: str) -> bool:
        """
        Exporta um relatório para Excel.
        
        Args:
            report_type: Tipo de relatório ('appointment', 'patient', 'usage', 'performance').
            report_data: Dados do relatório.
            output_file: Caminho do arquivo de saída.
            
        Returns:
            True se a exportação foi bem-sucedida, False caso contrário.
        """
        try:
            # Verificar se o relatório foi gerado com sucesso
            if not report_data.get('success', False):
                logger.error(f"Não é possível exportar relatório com erro: {report_data.get('message', 'Unknown error')}")
                return False
            
            # Criar arquivo Excel
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                # Planilha de resumo
                summary_df = pd.DataFrame({
                    'Métrica': list(report_data.get('summary', {}).keys()),
                    'Valor': list(report_data.get('summary', {}).values())
                })
                summary_df.to_excel(writer, sheet_name='Resumo', index=False)
                
                # Planilha para cada distribuição
                for dist_name, dist_data in report_data.get('distributions', {}).items():
                    if dist_data:
                        dist_df = pd.DataFrame({
                            'Categoria': list(dist_data.keys()),
                            'Valor': list(dist_data.values())
                        })
                        sheet_name = dist_name.replace('by_', '').title()
                        dist_df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Adicionar gráficos
                if report_data.get('graphs'):
                    workbook = writer.book
                    
                    # Planilha de gráficos
                    worksheet = workbook.add_worksheet('Gráficos')
                    
                    row = 0
                    for graph_name, graph_data in report_data['graphs'].items():
                        # Decodificar imagem base64
                        image_data = base64.b64decode(graph_data.split(',')[1])
                        
                        # Salvar temporariamente
                        temp_image_path = f"/tmp/{graph_name}.png"
                        with open(temp_image_path, 'wb') as f:
                            f.write(image_data)
                        
                        # Adicionar título
                        title = graph_name.replace('_', ' ').title()
                        worksheet.write(row, 0, title)
                        row += 1
                        
                        # Inserir imagem
                        worksheet.insert_image(row, 0, temp_image_path)
                        row += 20  # Espaço para a imagem
                        
                        # Remover arquivo temporário
                        os.remove(temp_image_path)
            
            logger.info(f"Relatório exportado com sucesso para {output_file}")
            return True
        except ImportError:
            logger.error("Biblioteca XlsxWriter não instalada. Execute: pip install xlsxwriter")
            return False
        except Exception as e:
            logger.error(f"Erro ao exportar relatório para Excel: {str(e)}")
            return False
    
    def export_report_to_csv(self, report_type: str, report_data: Dict[str, Any], output_dir: str) -> bool:
        """
        Exporta um relatório para CSV.
        
        Args:
            report_type: Tipo de relatório ('appointment', 'patient', 'usage', 'performance').
            report_data: Dados do relatório.
            output_dir: Diretório de saída para os arquivos CSV.
            
        Returns:
            True se a exportação foi bem-sucedida, False caso contrário.
        """
        try:
            # Verificar se o relatório foi gerado com sucesso
            if not report_data.get('success', False):
                logger.error(f"Não é possível exportar relatório com erro: {report_data.get('message', 'Unknown error')}")
                return False
            
            # Verificar se o diretório existe
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Arquivo de resumo
            summary_df = pd.DataFrame({
                'Métrica': list(report_data.get('summary', {}).keys()),
                'Valor': list(report_data.get('summary', {}).values())
            })
            summary_df.to_csv(f"{output_dir}/{report_type}_summary.csv", index=False)
            
            # Arquivo para cada distribuição
            for dist_name, dist_data in report_data.get('distributions', {}).items():
                if dist_data:
                    dist_df = pd.DataFrame({
                        'Categoria': list(dist_data.keys()),
                        'Valor': list(dist_data.values())
                    })
                    dist_df.to_csv(f"{output_dir}/{report_type}_{dist_name}.csv", index=False)
            
            logger.info(f"Relatório exportado com sucesso para {output_dir}")
            return True
        except Exception as e:
            logger.error(f"Erro ao exportar relatório para CSV: {str(e)}")
            return False
    
    def _create_bar_chart(self, data: Dict[str, Any], title: str, xlabel: str, ylabel: str) -> str:
        """
        Cria um gráfico de barras.
        
        Args:
            data: Dicionário com dados para o gráfico.
            title: Título do gráfico.
            xlabel: Rótulo do eixo X.
            ylabel: Rótulo do eixo Y.
            
        Returns:
            String base64 da imagem do gráfico.
        """
        plt.figure(figsize=(10, 6))
        
        # Criar gráfico
        ax = sns.barplot(x=list(data.keys()), y=list(data.values()))
        
        # Configurar rótulos
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        
        # Adicionar valores nas barras
        for i, v in enumerate(data.values()):
            ax.text(i, v + 0.1, str(v), ha='center')
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_pie_chart(self, data: Dict[str, Any], title: str) -> str:
        """
        Cria um gráfico de pizza.
        
        Args:
            data: Dicionário com dados para o gráfico.
            title: Título do gráfico.
            
        Returns:
            String base64 da imagem do gráfico.
        """
        plt.figure(figsize=(8, 8))
        
        # Criar gráfico
        plt.pie(
            list(data.values()),
            labels=list(data.keys()),
            autopct='%1.1f%%',
            startangle=90,
            shadow=True
        )
        
        # Configurar rótulos
        plt.title(title)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_line_chart(self, data: Dict[str, Any], title: str, xlabel: str, ylabel: str) -> str:
        """
        Cria um gráfico de linha.
        
        Args:
            data: Dicionário com dados para o gráfico.
            title: Título do gráfico.
            xlabel: Rótulo do eixo X.
            ylabel: Rótulo do eixo Y.
            
        Returns:
            String base64 da imagem do gráfico.
        """
        plt.figure(figsize=(10, 6))
        
        # Ordenar dados
        sorted_data = {k: data[k] for k in sorted(data.keys())}
        
        # Criar gráfico
        plt.plot(list(sorted_data.keys()), list(sorted_data.values()), marker='o')
        
        # Configurar rótulos
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        
        plt.tight_layout()
        
        # Converter para base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _get_report_title(self, report_type: str) -> str:
        """
        Obtém o título do relatório com base no tipo.
        
        Args:
            report_type: Tipo de relatório.
            
        Returns:
            Título do relatório.
        """
        titles = {
            'appointment': 'Agendamentos',
            'patient': 'Pacientes',
            'usage': 'Uso do Sistema',
            'performance': 'Desempenho do Sistema'
        }
        
        return titles.get(report_type, 'Relatório')
