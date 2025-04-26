# Documentação Técnica - Chatbot LINE para Clínicas

## Visão Geral do Sistema

O Chatbot LINE para Clínicas é uma solução comercial completa para agendamento de consultas e comunicação com pacientes, desenvolvida especificamente para o mercado japonês. O sistema consiste em dois componentes principais:

1. **Chatbot LINE**: Interface de comunicação com os pacientes através da plataforma LINE, permitindo agendamento de consultas, seleção de idioma e comunicação direta com a clínica.

2. **Painel Administrativo Web**: Interface para as clínicas gerenciarem agendamentos, pacientes, configurações e visualizarem relatórios.

Esta documentação técnica fornece informações detalhadas sobre a arquitetura, instalação, configuração e uso do sistema.

## Arquitetura do Sistema

### Componentes Principais

```
line_bot_commercial/
├── admin-panel/           # Painel administrativo web (Next.js)
│   ├── src/               # Código-fonte do painel
│   ├── tests/             # Testes automatizados
│   └── ...
├── line_bot/              # Chatbot LINE (Flask)
│   ├── app.py             # Arquivo principal do chatbot
│   ├── line_manager.py    # Gerenciador da integração com LINE API
│   ├── supabase_manager.py # Gerenciador da integração com Supabase
│   ├── translation_manager.py # Gerenciador de traduções
│   ├── conversation_manager.py # Gerenciador do fluxo de conversa
│   └── ...
└── docs/                  # Documentação
    ├── admin_guide.md     # Guia do administrador
    ├── developer_guide.md # Guia do desenvolvedor
    └── api_reference.md   # Referência da API
```

### Tecnologias Utilizadas

- **Backend do Chatbot**: Python, Flask
- **Frontend do Painel**: Next.js, React, Tailwind CSS
- **Banco de Dados**: Supabase (PostgreSQL)
- **APIs Externas**: LINE Messaging API, OpenAI API
- **Testes**: Vitest, React Testing Library
- **Monitoramento**: Sistema de logs personalizado, Performance Monitor

### Fluxo de Dados

1. O paciente interage com o chatbot através do aplicativo LINE
2. O chatbot processa a mensagem e determina a intenção do usuário
3. Se necessário, o chatbot consulta o banco de dados para informações
4. O chatbot responde ao paciente e/ou registra informações no banco de dados
5. O painel administrativo web exibe os dados em tempo real para a clínica
6. A clínica pode gerenciar agendamentos, pacientes e configurações através do painel

## Instalação e Configuração

### Requisitos do Sistema

- Python 3.8+
- Node.js 16+
- PostgreSQL 13+ (ou conta Supabase)
- Conta LINE Developers com canal Messaging API configurado
- Conta OpenAI API (opcional, para tradução avançada)

### Instalação do Chatbot LINE

1. Clone o repositório:
   ```bash
   git clone https://github.com/sua-empresa/line-bot-commercial.git
   cd line-bot-commercial/line_bot
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

4. Inicie o servidor:
   ```bash
   python app.py
   ```

### Instalação do Painel Administrativo

1. Navegue até a pasta do painel:
   ```bash
   cd ../admin-panel
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env.local
   # Edite o arquivo .env.local com suas credenciais
   ```

4. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

5. Para produção, construa e inicie o servidor:
   ```bash
   npm run build
   npm start
   ```

### Configuração do Banco de Dados

1. Crie um projeto no Supabase (https://supabase.com)
2. Execute os scripts SQL fornecidos para criar as tabelas necessárias:
   ```sql
   -- Tabela de pacientes
   CREATE TABLE patients (
     id SERIAL PRIMARY KEY,
     line_user_id VARCHAR(255) NOT NULL UNIQUE,
     name VARCHAR(255),
     phone VARCHAR(50),
     email VARCHAR(255),
     preferred_language VARCHAR(10) DEFAULT 'ja',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Tabela de agendamentos
   CREATE TABLE appointments (
     id SERIAL PRIMARY KEY,
     patient_id INTEGER REFERENCES patients(id),
     appointment_date DATE NOT NULL,
     appointment_time TIME NOT NULL,
     reason TEXT,
     status VARCHAR(20) DEFAULT 'pending',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Tabela de clínicas
   CREATE TABLE clinics (
     id SERIAL PRIMARY KEY,
     name VARCHAR(255) NOT NULL,
     address TEXT,
     phone VARCHAR(50),
     email VARCHAR(255),
     line_official_account_id VARCHAR(255),
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );

   -- Tabela de usuários (para o painel administrativo)
   CREATE TABLE users (
     id SERIAL PRIMARY KEY,
     clinic_id INTEGER REFERENCES clinics(id),
     name VARCHAR(255) NOT NULL,
     email VARCHAR(255) NOT NULL UNIQUE,
     password_hash VARCHAR(255) NOT NULL,
     role VARCHAR(20) DEFAULT 'staff',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
   );
   ```

3. Atualize as credenciais do Supabase no arquivo `.env` do chatbot e `.env.local` do painel administrativo

### Configuração da LINE Messaging API

1. Crie um canal Messaging API no LINE Developers Console (https://developers.line.biz)
2. Configure o webhook URL para apontar para seu servidor: `https://seu-servidor.com/webhook`
3. Habilite as opções "Use webhook" e "Allow bot to join group chats"
4. Copie o Channel Secret e Channel Access Token para o arquivo `.env`

## Uso do Sistema

### Chatbot LINE

O chatbot LINE oferece as seguintes funcionalidades para os pacientes:

1. **Seleção de Idioma**: Pacientes podem escolher entre Japonês, Português, Inglês ou outros idiomas
2. **Agendamento de Consultas**: Fluxo guiado para agendar uma nova consulta
3. **Verificação de Agendamentos**: Consultar agendamentos existentes
4. **Comunicação com a Clínica**: Enviar mensagens diretamente para a clínica

### Painel Administrativo

O painel administrativo oferece as seguintes funcionalidades para as clínicas:

1. **Dashboard**: Visão geral dos agendamentos e estatísticas
2. **Gerenciamento de Agendamentos**: Visualizar, confirmar, recusar e gerenciar agendamentos
3. **Gerenciamento de Pacientes**: Visualizar e gerenciar informações dos pacientes
4. **Configurações**: Personalizar mensagens, horários de funcionamento e outras configurações
5. **Relatórios**: Gerar relatórios de agendamentos, pacientes e uso do sistema
6. **Monitoramento**: Visualizar logs do sistema e métricas de desempenho

## Segurança e Autenticação

### Autenticação do Painel Administrativo

O painel administrativo utiliza autenticação baseada em JWT (JSON Web Tokens) com os seguintes recursos:

1. **Login Seguro**: Autenticação com email e senha
2. **Proteção de Rotas**: Acesso restrito a usuários autenticados
3. **Controle de Permissões**: Diferentes níveis de acesso (admin, staff)
4. **Sessões Persistentes**: Manutenção da sessão entre visitas

### Segurança de Dados

1. **Criptografia**: Dados sensíveis são criptografados em trânsito e em repouso
2. **Validação de Entrada**: Todas as entradas do usuário são validadas para prevenir injeção de código
3. **Proteção CSRF**: Implementação de tokens CSRF para prevenir ataques cross-site request forgery
4. **Rate Limiting**: Limitação de requisições para prevenir ataques de força bruta

## Monitoramento e Logs

### Sistema de Logs

O sistema de logs registra eventos em diferentes níveis:

1. **DEBUG**: Informações detalhadas para desenvolvimento
2. **INFO**: Eventos normais do sistema
3. **WARN**: Avisos que não afetam o funcionamento
4. **ERROR**: Erros que afetam funcionalidades específicas
5. **CRITICAL**: Erros graves que afetam todo o sistema

### Monitoramento de Desempenho

O sistema de monitoramento de desempenho rastreia:

1. **Carregamentos de Página**: Número de visualizações de página
2. **Chamadas de API**: Número e duração de chamadas de API
3. **Erros**: Número e tipo de erros encontrados
4. **Tempo de Resposta**: Tempo médio de resposta das APIs

## Testes Automatizados

### Testes de Interface

Testes automatizados para todas as páginas do painel administrativo:

1. **Login**: Testes de autenticação e validação
2. **Agendamentos**: Testes de visualização, filtragem e gerenciamento
3. **Configurações**: Testes de personalização e salvamento
4. **Relatórios**: Testes de geração e exportação
5. **Monitoramento**: Testes de visualização de logs e métricas

### Testes de Componentes

Testes para componentes individuais:

1. **AuthProvider**: Testes de autenticação e proteção de rotas
2. **LoggingSystem**: Testes de registro de logs
3. **PerformanceMonitor**: Testes de monitoramento de desempenho

## Personalização e Extensão

### Personalização de Mensagens

As mensagens do chatbot podem ser personalizadas através do painel administrativo:

1. **Mensagem de Boas-vindas**: Personalização da mensagem inicial
2. **Confirmações**: Personalização das mensagens de confirmação
3. **Notificações**: Personalização das notificações para pacientes

### Adição de Novos Idiomas

Para adicionar suporte a novos idiomas:

1. Adicione o novo idioma no arquivo `translation_manager.py`
2. Adicione as traduções no painel administrativo
3. Atualize a interface do chatbot para incluir o novo idioma

### Integração com Outros Sistemas

O sistema pode ser integrado com:

1. **Sistemas de Prontuário Eletrônico**: Através da API REST
2. **Calendários Externos**: Google Calendar, Outlook, etc.
3. **Sistemas de Notificação**: Email, SMS, etc.

## Solução de Problemas

### Problemas Comuns

1. **Webhook não recebe eventos**: Verifique a configuração do webhook no LINE Developers Console
2. **Erro de autenticação no painel**: Verifique as credenciais no arquivo `.env.local`
3. **Erro de conexão com o banco de dados**: Verifique as credenciais do Supabase

### Logs de Erro

Os logs de erro podem ser acessados através:

1. **Painel de Monitoramento**: Acesse a página de monitoramento no painel administrativo
2. **Logs do Servidor**: Verifique os logs do servidor onde o chatbot está hospedado
3. **Console do Navegador**: Verifique o console do navegador para erros no frontend

## Suporte e Manutenção

### Atualizações

Para atualizar o sistema:

1. **Chatbot**: Pull das últimas alterações e reinicie o servidor
2. **Painel Administrativo**: Pull das últimas alterações, reconstrua e reinicie o servidor
3. **Banco de Dados**: Execute os scripts de migração fornecidos

### Contato para Suporte

Para suporte técnico, entre em contato:

- Email: suporte@sua-empresa.com
- Telefone: +81 XX-XXXX-XXXX
- Horário de atendimento: Segunda a Sexta, 9h às 18h (JST)

## Licenciamento e Distribuição

Este software é licenciado para uso exclusivo por clínicas que adquiriram a licença. A redistribuição ou revenda não é permitida sem autorização expressa.

---

© 2025 Sua Empresa. Todos os direitos reservados.
