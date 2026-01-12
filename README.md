# Bot de WhatsApp - Ar-Condicionado 🤖❄️

Sistema automatizado de agendamento de serviços de ar-condicionado via WhatsApp.

## 📋 Sobre o Projeto

Este bot permite que clientes agendem serviços de ar-condicionado (limpeza, instalação e manutenção) através de uma conversa natural no WhatsApp. O sistema gerencia automaticamente:

- ✅ Verificação de disponibilidade no Google Calendar
- ✅ Criação de eventos no calendário
- ✅ Armazenamento de agendamentos no banco de dados
- ✅ Fluxo conversacional guiado

## 🛠 Tecnologias

- **Backend**: FastAPI (Python 3.11+)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Agenda**: Google Calendar API
- **WhatsApp**: WPPConnect (webhook)

## 📁 Estrutura do Projeto

```
bot-ar-condicionado/
├── main.py                      # API FastAPI principal
├── requirements.txt             # Dependências
├── .env                         # Variáveis de ambiente (não commitar)
│
├── models/                      # Modelos Pydantic
│   └── __init__.py              # Modelos de dados com validações
│
├── services/                    # Lógica de negócio
│   ├── whatsapp_service.py      # Processamento de mensagens
│   ├── agendamentos_service.py  # Gestão de agendamentos
│   └── supabase_client.py       # Cliente do banco
│
├── scripts/                     # Utilitários
│   ├── calendar_utils.py        # Integração com Google Calendar
│   ├── test_calendar.py         # Testes do Calendar
│   └── test_disponibilidade.py  # Testes de disponibilidade
│
└── credentials/                 # Credenciais (não commitar)
    └── *.json                   # Arquivo de service account
```

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd bot-ar-condicionado
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```
SUPABASE_URL=sua_url_do_supabase
SUPABASE_KEY=sua_chave_do_supabase
```

### 5. Configure o Google Calendar

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto
3. Ative a API do Google Calendar
4. Crie uma conta de serviço
5. Baixe o arquivo JSON de credenciais
6. Coloque o arquivo em `credentials/`
7. Compartilhe seu calendário com o email da conta de serviço

## ▶️ Executando o Projeto

```bash
uvicorn main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## 📡 Endpoints da API

### `GET /`
Verifica se a API está funcionando.

### `POST /whatsapp`
Recebe mensagens do WhatsApp e retorna respostas do bot.

**Exemplo de requisição:**
```json
{
  "telefone": "11987654321",
  "mensagem": "Olá"
}
```

**Parâmetro de query:**
- `?simulacao=true` - Retorna formato de teste

### `POST /agendar`
Cria um agendamento diretamente via API.

**Exemplo de requisição:**
```json
{
  "servico": "limpeza",
  "data": "2026-01-15",
  "hora": "14:30",
  "cliente": {
    "nome": "João Silva",
    "telefone": "11987654321",
    "endereco": {
      "rua": "Rua das Flores",
      "numero": "123",
      "bairro": "Centro",
      "cidade": "São Paulo",
      "cep": "01234-567"
    }
  }
}
```

## 🔄 Fluxo de Conversa no WhatsApp

1. Cliente: "Olá"
2. Bot: "Qual serviço você deseja? limpeza / instalação / manutenção"
3. Cliente: "limpeza"
4. Bot: "Qual data você prefere? (YYYY-MM-DD)"
5. Cliente: "2026-01-15"
6. Bot: "Agora informe o horário (HH:MM)"
7. Cliente: "14:30"
8. Bot: "Qual o seu nome completo?"
9. Cliente: "João Silva"
10. Bot: "Informe seu endereço completo (Rua, Número, Bairro, Cidade, CEP)"
11. Cliente: "Rua das Flores, 123, Centro, São Paulo, 01234-567"
12. Bot: "✅ Agendamento confirmado!"

## 🗄️ Banco de Dados

### Tabela: `agendamentos`
- `nome_cliente` (text)
- `telefone` (text)
- `servico` (text)
- `data_hora` (timestamp)
- `duracao_horas` (integer)
- `rua`, `numero`, `bairro`, `cidade`, `cep` (text)
- `calendar_event_id` (text)
- `status` (text)

### Tabela: `conversas_whatsapp`
- `telefone` (text) - PK
- `etapa` (text)
- `servico`, `data`, `hora`, `nome` (text)
- `rua`, `numero`, `bairro`, `cidade`, `cep` (text)

## 🧪 Testando

### Testar endpoint de WhatsApp
```bash
curl -X POST http://localhost:8000/whatsapp?simulacao=true \
  -H "Content-Type: application/json" \
  -d '{"telefone": "11987654321", "mensagem": "Olá"}'
```

### Testar endpoint de agendamento
```bash
curl -X POST http://localhost:8000/agendar \
  -H "Content-Type: application/json" \
  -d @exemplo_agendamento.json
```

## 📚 Documentação do Código

Todos os arquivos seguem as regras definidas em `.antigravity/rules.rpi`:

- ✅ Type hints em todas as funções
- ✅ Docstrings completas
- ✅ Comentários explicativos
- ✅ Tratamento de erros específicos
- ✅ Validações com Pydantic

## 🤝 Contribuindo

Este projeto foi desenvolvido com foco didático para iniciantes em Python e FastAPI.

## 📄 Licença

Este projeto é de uso educacional.
