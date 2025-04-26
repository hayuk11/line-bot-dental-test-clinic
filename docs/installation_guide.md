# Guia de Instalação e Configuração

## Requisitos do Sistema

### Servidor
- Sistema Operacional: Ubuntu 20.04 LTS ou superior
- CPU: 2 cores ou mais
- RAM: 4GB ou mais
- Armazenamento: 20GB ou mais
- Python 3.8 ou superior
- Node.js 14 ou superior (para o painel administrativo)

### Banco de Dados
- Supabase (plano gratuito ou pago)

### Serviços Externos
- Conta LINE Business
- Conta OpenAI API (para tradução multilíngue)
- Opcional: Conta Google Cloud (para integração com Google Calendar)
- Opcional: Conta Microsoft Azure (para integração com Outlook)

## Passo a Passo de Instalação

### 1. Configuração do Ambiente

```bash
# Clonar o repositório
git clone https://github.com/clinicatanaka/line-chatbot.git
cd line-chatbot

# Criar ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 2. Configuração do Supabase

1. Crie uma conta no [Supabase](https://supabase.io/)
2. Crie um novo projeto
3. Execute os scripts SQL em `migrations/` para criar as tabelas necessárias
4. Copie a URL e a chave API para o arquivo `.env`

### 3. Configuração do LINE Messaging API

1. Crie uma conta no [LINE Developers](https://developers.line.biz/)
2. Crie um novo provedor e um novo canal Messaging API
3. Configure o webhook URL para apontar para seu servidor: `https://seu-servidor.com/webhook`
4. Copie o Channel Secret e o Channel Access Token para o arquivo `.env`

### 4. Configuração do Painel Administrativo

```bash
# Instalar dependências do painel administrativo
cd admin-panel
npm install

# Construir o painel administrativo
npm run build

# Voltar para a raiz do projeto
cd ..
```

### 5. Iniciar o Servidor

```bash
# Iniciar o servidor Flask
python app.py
```

Para produção, recomendamos usar Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Configuração Inicial

### 1. Acesso ao Painel Administrativo

1. Acesse `https://seu-servidor.com/admin`
2. Faça login com as credenciais padrão:
   - Usuário: `admin`
   - Senha: `admin123`
3. **Importante**: Altere a senha padrão imediatamente

### 2. Configuração da Clínica

1. Vá para "Configurações" > "Informações da Clínica"
2. Preencha os dados da clínica:
   - Nome
   - Endereço
   - Telefone
   - Email
   - Horários de funcionamento

### 3. Configuração do Chatbot

1. Vá para "Configurações" > "Chatbot"
2. Personalize as mensagens de boas-vindas em diferentes idiomas
3. Configure as opções de agendamento:
   - Duração padrão das consultas
   - Tempo mínimo de antecedência para agendamento
   - Horários disponíveis para agendamento

### 4. Integração com Calendário (Opcional)

1. Vá para "Configurações" > "Integrações"
2. Selecione o tipo de calendário (Google, Outlook, iCal)
3. Siga as instruções para autorizar a integração

## Personalização

### Personalização de Mensagens

1. Vá para "Configurações" > "Mensagens"
2. Personalize as mensagens para cada etapa do fluxo de conversa
3. Você pode personalizar mensagens em todos os idiomas suportados

### Personalização Visual

1. Vá para "Configurações" > "Aparência"
2. Faça upload do logo da clínica
3. Personalize as cores do painel administrativo
4. Configure o estilo dos cartões rich menu do LINE

## Manutenção

### Backup do Banco de Dados

Recomendamos configurar backups automáticos do Supabase. Alternativamente:

```bash
# Exportar dados do Supabase
supabase db dump -f backup.sql
```

### Atualização do Sistema

```bash
# Atualizar o código
git pull

# Atualizar dependências
pip install -r requirements.txt

# Reiniciar o servidor
sudo systemctl restart line-chatbot
```

### Monitoramento

1. Vá para "Monitoramento" no painel administrativo
2. Verifique logs de sistema, desempenho e erros
3. Configure alertas para eventos importantes

## Solução de Problemas

### Problemas Comuns

1. **Webhook não está funcionando**
   - Verifique se a URL do webhook está correta no LINE Developers
   - Verifique se o servidor está acessível publicamente
   - Verifique os logs do servidor para erros

2. **Erro de autenticação com Supabase**
   - Verifique se as credenciais no arquivo `.env` estão corretas
   - Verifique se o projeto Supabase está ativo

3. **Integração com calendário não funciona**
   - Verifique se as credenciais de API estão corretas
   - Verifique se as permissões foram concedidas corretamente

### Suporte

Para suporte técnico:
- Email: suporte@clinicatanaka.com
- Telefone: +81-XX-XXXX-XXXX
- Portal de suporte: https://suporte.clinicatanaka.com
