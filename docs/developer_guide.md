# Guia do Desenvolvedor - Chatbot LINE para Clínicas

## Introdução

Este guia fornece informações detalhadas para desenvolvedores que precisam estender, personalizar ou manter o Chatbot LINE para Clínicas. O sistema foi projetado com modularidade e extensibilidade em mente, permitindo adaptações para necessidades específicas.

## Estrutura do Projeto

### Visão Geral da Estrutura

```
line_bot_commercial/
├── admin-panel/           # Painel administrativo web (Next.js)
│   ├── src/               # Código-fonte do painel
│   │   ├── app/           # Páginas do aplicativo Next.js
│   │   ├── components/    # Componentes React reutilizáveis
│   │   ├── hooks/         # Hooks React personalizados
│   │   └── lib/           # Funções utilitárias
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
    ├── technical_documentation.md # Documentação técnica
    ├── admin_guide.md     # Guia do administrador
    └── developer_guide.md # Este documento
```

### Componentes Principais

#### Chatbot LINE (Flask)

- **app.py**: Ponto de entrada da aplicação Flask, configura rotas e inicializa componentes
- **line_manager.py**: Gerencia a comunicação com a LINE Messaging API
- **supabase_manager.py**: Gerencia a comunicação com o banco de dados Supabase
- **translation_manager.py**: Gerencia traduções e integração com OpenAI API
- **conversation_manager.py**: Gerencia o fluxo de conversa e estados do chatbot

#### Painel Administrativo (Next.js)

- **src/app/**: Páginas do aplicativo Next.js (login, dashboard, agendamentos, etc.)
- **src/components/**: Componentes React reutilizáveis
  - **auth/**: Componentes de autenticação
  - **monitoring/**: Componentes de monitoramento e logs
  - **ui/**: Componentes de interface do usuário
- **src/hooks/**: Hooks React personalizados
- **src/lib/**: Funções utilitárias e clientes API

## Ambiente de Desenvolvimento

### Configuração do Ambiente

#### Requisitos

- Python 3.8+
- Node.js 16+
- Git
- Editor de código (recomendado: VS Code)

#### Configuração do Chatbot

1. Clone o repositório:
   ```bash
   git clone https://github.com/sua-empresa/line-bot-commercial.git
   cd line-bot-commercial/line_bot
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

5. Inicie o servidor de desenvolvimento:
   ```bash
   python app.py
   ```

#### Configuração do Painel Administrativo

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

### Ferramentas de Desenvolvimento

#### Recomendadas para o Chatbot (Python)

- **Linting**: flake8, pylint
- **Formatação**: black
- **Testes**: pytest
- **Documentação**: Sphinx

#### Recomendadas para o Painel (JavaScript/TypeScript)

- **Linting**: ESLint
- **Formatação**: Prettier
- **Testes**: Vitest, React Testing Library
- **Documentação**: JSDoc

## Fluxo de Desenvolvimento

### Processo de Desenvolvimento

1. **Planejamento**: Defina claramente os requisitos e escopo da alteração
2. **Desenvolvimento**: Implemente as alterações seguindo as convenções de código
3. **Testes**: Escreva testes automatizados para as novas funcionalidades
4. **Revisão**: Realize uma revisão de código antes de finalizar
5. **Documentação**: Atualize a documentação conforme necessário

### Convenções de Código

#### Python (Chatbot)

- Siga o PEP 8 para estilo de código
- Use docstrings no formato Google para documentação
- Mantenha funções pequenas e com responsabilidade única
- Use tipagem estática quando possível

Exemplo:
```python
def get_patient_by_line_id(line_user_id: str) -> Optional[Dict[str, Any]]:
    """Busca um paciente pelo ID do LINE.
    
    Args:
        line_user_id: ID do usuário no LINE.
        
    Returns:
        Dicionário com dados do paciente ou None se não encontrado.
    """
    try:
        result = supabase_client.table("patients").select("*").eq("line_user_id", line_user_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar paciente: {str(e)}")
        return None
```

#### JavaScript/TypeScript (Painel)

- Use ESLint e Prettier para formatação consistente
- Prefira componentes funcionais e hooks em React
- Use tipagem TypeScript para todos os componentes
- Organize imports em ordem alfabética

Exemplo:
```typescript
interface PatientProps {
  id: number;
  name: string;
  preferredLanguage: string;
  lastContact?: Date;
}

const PatientCard: React.FC<PatientProps> = ({ id, name, preferredLanguage, lastContact }) => {
  const formatDate = (date?: Date): string => {
    if (!date) return 'Nunca';
    return new Intl.DateTimeFormat('pt-BR').format(date);
  };
  
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <h3 className="text-lg font-medium">{name}</h3>
      <p className="text-sm text-gray-500">ID: {id}</p>
      <p className="text-sm">Idioma: {preferredLanguage}</p>
      <p className="text-sm">Último contato: {formatDate(lastContact)}</p>
    </div>
  );
};

export default PatientCard;
```

### Controle de Versão

- Use Git para controle de versão
- Siga o modelo de branching GitFlow:
  - `main`: Código em produção
  - `develop`: Código em desenvolvimento
  - `feature/*`: Novas funcionalidades
  - `bugfix/*`: Correções de bugs
  - `release/*`: Preparação para release
- Escreva mensagens de commit descritivas seguindo o padrão Conventional Commits

## Extensão e Personalização

### Adição de Novas Funcionalidades ao Chatbot

#### Adição de Novos Comandos

Para adicionar um novo comando ao chatbot:

1. Abra o arquivo `conversation_manager.py`
2. Adicione uma nova função de handler para o comando:
   ```python
   def handle_new_command(self, line_user_id: str, message: str) -> List[Dict]:
       """Processa o novo comando.
       
       Args:
           line_user_id: ID do usuário no LINE.
           message: Mensagem recebida.
           
       Returns:
           Lista de mensagens a serem enviadas como resposta.
       """
       # Implementação do comando
       return [{"type": "text", "text": "Resposta ao novo comando"}]
   ```

3. Adicione o comando ao dicionário de comandos em `__init__`:
   ```python
   self.commands = {
       "agendar": self.handle_appointment,
       "cancelar": self.handle_cancellation,
       "novo_comando": self.handle_new_command,  # Novo comando
       # ...
   }
   ```

#### Modificação do Fluxo de Conversa

Para modificar o fluxo de conversa:

1. Abra o arquivo `conversation_manager.py`
2. Localize a função `handle_appointment` ou outra função de fluxo relevante
3. Modifique as etapas do fluxo conforme necessário:
   ```python
   def handle_appointment(self, line_user_id: str, message: str) -> List[Dict]:
       user_state = self.get_user_state(line_user_id)
       
       if user_state.get("appointment_step") == "date":
           # Processar data
           # ...
       elif user_state.get("appointment_step") == "time":
           # Processar horário
           # ...
       elif user_state.get("appointment_step") == "nova_etapa":
           # Nova etapa no fluxo
           # ...
   ```

### Personalização do Painel Administrativo

#### Adição de Novas Páginas

Para adicionar uma nova página ao painel:

1. Crie um novo arquivo em `admin-panel/src/app/nova-pagina/page.tsx`:
   ```tsx
   "use client";
   
   import { useState, useEffect } from "react";
   import Link from "next/link";
   
   export default function NovaPagina() {
     const [data, setData] = useState([]);
     
     useEffect(() => {
       // Carregar dados
     }, []);
     
     return (
       <div className="min-h-screen bg-gray-100">
         <header className="bg-white shadow">
           <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
             <h1 className="text-3xl font-bold text-gray-900">Nova Página</h1>
           </div>
         </header>
         
         <main>
           <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
             {/* Conteúdo da página */}
           </div>
         </main>
       </div>
     );
   }
   ```

2. Adicione um link para a nova página no menu de navegação em `admin-panel/src/components/ui/Sidebar.tsx`

#### Criação de Novos Componentes

Para criar um novo componente:

1. Crie um novo arquivo em `admin-panel/src/components/ui/NovoComponente.tsx`:
   ```tsx
   import { useState } from "react";
   
   interface NovoComponenteProps {
     titulo: string;
     onAction: () => void;
   }
   
   export default function NovoComponente({ titulo, onAction }: NovoComponenteProps) {
     const [isActive, setIsActive] = useState(false);
     
     return (
       <div className="bg-white p-4 rounded-lg shadow">
         <h3 className="text-lg font-medium">{titulo}</h3>
         <button
           onClick={() => {
             setIsActive(!isActive);
             onAction();
           }}
           className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
         >
           {isActive ? "Ativo" : "Inativo"}
         </button>
       </div>
     );
   }
   ```

2. Importe e utilize o componente onde necessário

### Integração com Sistemas Externos

#### Integração com Novos Serviços

Para integrar com um novo serviço externo:

1. Crie um novo arquivo para o gerenciador do serviço, por exemplo `external_service_manager.py`:
   ```python
   import requests
   import logging
   from typing import Dict, Any, Optional
   
   logger = logging.getLogger(__name__)
   
   class ExternalServiceManager:
       def __init__(self, api_key: str, base_url: str):
           self.api_key = api_key
           self.base_url = base_url
           
       def get_data(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
           """Obtém dados do serviço externo.
           
           Args:
               endpoint: Endpoint da API.
               params: Parâmetros da requisição.
               
           Returns:
               Dados retornados ou None em caso de erro.
           """
           try:
               response = requests.get(
                   f"{self.base_url}/{endpoint}",
                   params=params,
                   headers={"Authorization": f"Bearer {self.api_key}"}
               )
               response.raise_for_status()
               return response.json()
           except Exception as e:
               logger.error(f"Erro ao acessar serviço externo: {str(e)}")
               return None
   ```

2. Importe e utilize o gerenciador onde necessário

#### Extensão da API REST

Para adicionar novos endpoints à API REST:

1. Abra o arquivo `app.py`
2. Adicione uma nova rota:
   ```python
   @app.route('/api/novo-recurso', methods=['GET', 'POST'])
   def novo_recurso():
       if request.method == 'GET':
           # Implementação do GET
           return jsonify({"status": "success", "data": {...}})
       elif request.method == 'POST':
           data = request.json
           # Implementação do POST
           return jsonify({"status": "success", "message": "Recurso criado"})
   ```

## Testes

### Testes do Chatbot (Python)

#### Testes Unitários

Utilize pytest para testes unitários:

```python
# test_translation_manager.py
import pytest
from translation_manager import TranslationManager

def test_translate_text():
    manager = TranslationManager(api_key="fake_key")
    # Mock da chamada à API
    manager._call_openai_api = lambda prompt: {"choices": [{"message": {"content": "Translated text"}}]}
    
    result = manager.translate_text("Original text", "en", "ja")
    assert result == "Translated text"

def test_detect_language():
    manager = TranslationManager(api_key="fake_key")
    # Mock da chamada à API
    manager._call_openai_api = lambda prompt: {"choices": [{"message": {"content": "ja"}}]}
    
    result = manager.detect_language("こんにちは")
    assert result == "ja"
```

#### Testes de Integração

Teste a integração entre componentes:

```python
# test_integration.py
import pytest
from app import app
from conversation_manager import ConversationManager
from line_manager import LineManager

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_webhook_endpoint(client, monkeypatch):
    # Mock do LineManager
    def mock_parse_webhook_request(request):
        return {"destination": "123", "events": [{"type": "message", "message": {"text": "agendar"}}]}
    
    def mock_reply_message(reply_token, messages):
        return True
    
    monkeypatch.setattr(LineManager, "parse_webhook_request", mock_parse_webhook_request)
    monkeypatch.setattr(LineManager, "reply_message", mock_reply_message)
    
    response = client.post('/webhook', json={
        "destination": "123",
        "events": [{"type": "message", "message": {"text": "agendar"}}]
    })
    
    assert response.status_code == 200
```

### Testes do Painel Administrativo (JavaScript/TypeScript)

#### Testes de Componentes

Utilize Vitest e React Testing Library para testar componentes:

```tsx
// PatientCard.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import PatientCard from '../src/components/ui/PatientCard';

describe('PatientCard', () => {
  it('renderiza corretamente', () => {
    render(
      <PatientCard
        id={1}
        name="João Silva"
        preferredLanguage="Português"
        lastContact={new Date('2025-04-20')}
      />
    );
    
    expect(screen.getByText('João Silva')).toBeInTheDocument();
    expect(screen.getByText('ID: 1')).toBeInTheDocument();
    expect(screen.getByText('Idioma: Português')).toBeInTheDocument();
    expect(screen.getByText(/Último contato:/)).toBeInTheDocument();
  });
  
  it('exibe "Nunca" quando não há data de último contato', () => {
    render(
      <PatientCard
        id={2}
        name="Maria Tanaka"
        preferredLanguage="Japonês"
      />
    );
    
    expect(screen.getByText('Último contato: Nunca')).toBeInTheDocument();
  });
});
```

#### Testes de Páginas

Teste páginas completas:

```tsx
// AgendamentosPage.test.tsx
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import AgendamentosPage from '../src/app/agendamentos/page';

// Mock do localStorage e outros recursos necessários
// ...

describe('AgendamentosPage', () => {
  beforeEach(() => {
    // Configurar mocks
  });
  
  it('renderiza corretamente', () => {
    render(<AgendamentosPage />);
    
    expect(screen.getByText('Gerenciamento de Agendamentos')).toBeInTheDocument();
    expect(screen.getByText('Visualização em Lista')).toBeInTheDocument();
    expect(screen.getByText('Visualização em Calendário')).toBeInTheDocument();
  });
  
  it('alterna entre visualizações', () => {
    render(<AgendamentosPage />);
    
    // Verificar visualização inicial (lista)
    expect(screen.getByTestId('list-view')).toBeVisible();
    expect(screen.queryByTestId('calendar-view')).not.toBeVisible();
    
    // Clicar no botão de visualização em calendário
    fireEvent.click(screen.getByText('Visualização em Calendário'));
    
    // Verificar se a visualização mudou
    expect(screen.queryByTestId('list-view')).not.toBeVisible();
    expect(screen.getByTestId('calendar-view')).toBeVisible();
  });
});
```

## Implantação

### Implantação do Chatbot

#### Servidor Dedicado/VPS

1. Prepare o servidor com Python e dependências
2. Clone o repositório
3. Configure o ambiente virtual e instale dependências
4. Configure o arquivo `.env` com credenciais de produção
5. Configure um servidor WSGI (Gunicorn, uWSGI)
6. Configure um proxy reverso (Nginx, Apache)
7. Configure SSL/TLS
8. Inicie o serviço

Exemplo de configuração Nginx:
```nginx
server {
    listen 80;
    server_name chatbot.clinica-tanaka.com;
    
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl;
    server_name chatbot.clinica-tanaka.com;
    
    ssl_certificate /etc/letsencrypt/live/chatbot.clinica-tanaka.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chatbot.clinica-tanaka.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Plataformas de Nuvem

O chatbot pode ser implantado em:

- **Heroku**: Utilize o Procfile fornecido
- **Google Cloud Run**: Utilize o Dockerfile fornecido
- **AWS Lambda**: Utilize o adaptador AWS Lambda fornecido

### Implantação do Painel Administrativo

#### Servidor Dedicado/VPS

1. Prepare o servidor com Node.js
2. Clone o repositório
3. Instale dependências
4. Configure o arquivo `.env.local` com credenciais de produção
5. Construa a aplicação: `npm run build`
6. Configure um servidor web (Nginx, Apache)
7. Configure SSL/TLS
8. Inicie o serviço: `npm start`

#### Plataformas de Nuvem

O painel pode ser implantado em:

- **Vercel**: Integração direta com Next.js
- **Netlify**: Utilize o arquivo `netlify.toml` fornecido
- **Firebase Hosting**: Utilize o arquivo `firebase.json` fornecido

## Manutenção e Suporte

### Monitoramento

#### Logs do Sistema

Os logs são armazenados em:

- **Desenvolvimento**: Console e localStorage
- **Produção**: Arquivo de log e/ou serviço de logging (Sentry, LogDNA)

Para configurar um serviço de logging externo:

1. Adicione a biblioteca cliente ao projeto
2. Configure as credenciais no arquivo `.env`
3. Atualize o sistema de logs para enviar eventos ao serviço

#### Alertas

Configure alertas para:

- Erros críticos
- Falhas de autenticação
- Uso elevado de recursos
- Tempos de resposta lentos

### Atualizações

#### Atualizações de Segurança

1. Mantenha as dependências atualizadas:
   ```bash
   # Para o chatbot
   pip list --outdated
   pip install --upgrade <pacote>
   
   # Para o painel
   npm outdated
   npm update
   ```

2. Aplique patches de segurança imediatamente
3. Realize testes completos após atualizações

#### Atualizações de Funcionalidades

1. Desenvolva em uma branch separada
2. Escreva testes para as novas funcionalidades
3. Atualize a documentação
4. Realize testes completos
5. Implante em ambiente de staging antes da produção

## Referências

### Documentação de APIs

- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/)
- [Supabase API](https://supabase.io/docs/reference/javascript/supabase-client)
- [OpenAI API](https://platform.openai.com/docs/api-reference)

### Bibliotecas Principais

- [Flask](https://flask.palletsprojects.com/)
- [LINE Bot SDK for Python](https://github.com/line/line-bot-sdk-python)
- [Supabase Python](https://github.com/supabase-community/supabase-py)
- [Next.js](https://nextjs.org/docs)
- [React](https://reactjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)

---

© 2025 Sua Empresa. Todos os direitos reservados.
