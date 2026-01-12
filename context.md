# Bot de WhatsApp - Ar-Condicionado

## 🎯 Objetivo
Bot de WhatsApp para empresa de Ar-Condicionado que automatiza agendamentos de serviços.

## 🛠 Serviços Oferecidos
- **Limpeza** (Duração: 1h, Preço: Fixo)
- **Instalação** (Duração: 3h, Preço: Fixo)
- **Manutenção** (Duração: 1h, Preço: Visita técnica)

## 🏗 Stack Tecnológica
- **Backend**: FastAPI (API REST)
- **Banco de Dados**: Supabase (PostgreSQL)
- **Agenda**: Google Calendar API
- **WhatsApp**: Evolution - API de Webhooks
- **Localização**: Português (Brasil) - Formato de data `DD/MM/AAAA` e fuso `America/Sao_Paulo`.

## 📁 Estrutura do Projeto
```
bot-ar-condicionado/
├── main.py                      # Arquivo principal da API FastAPI
├── requirements.txt             # Dependências do projeto
├── .env                         # Variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
│
├── core/                        # Núcleo da aplicação
│   ├── config.py                # Configurações (Pydantic Settings)
│   ├── logger.py                # Logging padronizado
│   ├── constants.py             # Enums e constantes globais
│   ├── exceptions.py            # Exceções customizadas
│   └── context.md               # Documentação do módulo core
│
├── bot/                         # Lógica do Bot
│   ├── manager.py               # Orquestrador (BotManager)
│   ├── states.py                # Estados da conversa (Enum)
│   ├── context.py               # Contexto do usuário (UserContext)
│   ├── handlers/                # Manipuladores de mensagens (Info, Booking)
│   └── context.md               # Documentação do módulo bot
│
├── models/                      # Modelos de Dados (Pydantic)
│   └── __init__.py              # Definições de Cliente, Agendamento, Webhook
│
├── services/                    # Integrações e Adaptadores
│   ├── whatsapp_service.py      # Adaptador para BotManager
│   ├── agendamentos_service.py  # Persistência no banco
│   ├── google_calendar_service.py # Integração com Google Calendar
│   ├── supabase_client.py       # Cliente do Supabase
│   └── context.md               # Documentação do módulo services
│
├── tests/                       # Testes automatizados
│   ├── unit/                    # Testes de unidade
│   └── context.md               # Estratégia de testes
│
├── scripts/                     # Scripts de apoio
│
└── credentials/                 # Credenciais (NÃO COMMITAR)
```

## 🔄 Fluxo de Dados
1. **Cliente envia mensagem** no WhatsApp
2. **Evolution API** envia webhook POST para `/whatsapp`
3. **whatsapp_service.py** recebe e repassa para **BotManager** (`bot/manager.py`)
4. **BotManager** recupera/cria o **UserContext** (Supabase)
5. **Handlers** (`InfoHandler`, `BookingHandler`) processam a intenção
6. Se necessário, sistema verifica **Google Calendar** e salva em **Supabase**
7. **BotManager** retorna a resposta para o cliente via adapter

## 🗄️ Banco de Dados (Supabase)

### Tabela: `agendamentos`
- nome_cliente (text)
- telefone (text)
- servico (text)
- data_hora (timestamp)
- duracao_horas (integer)
- rua, numero, bairro, cidade, cep (text)
- calendar_event_id (text)
- status (text)

### Tabela: `conversas_whatsapp`
- telefone (text) - PK
- etapa (text) - Estado da conversa
- data, hora, nome, servico (text) - Dados de contexto (JSONB flatten)
- updated_at (timestampWithTimeZone) - Controle de sessão
- created_at (timestamp)

## 📚 Roadmap de Aprendizado
- [x] Visão geral do sistema (Sem código)
- [x] Preparação do ambiente
- [x] FastAPI Simples
- [x] Integração com Supabase
- [x] Integração com Google Calendar
- [x] Refatoração Arquitetural (Core/Bot/Handlers)
- [ ] Integração completa com WhatsApp usando Evolution - API de Webhooks
- [ ] Testes automatizados
- [ ] Deploy em produção

## 🔍 Troubleshooting
- **Logs**: Verifique o console do Uvicorn para logs formatados via `core.logger`.
- **Environment**: Garanta que `.env` possui `SUPABASE_URL`, `SUPABASE_KEY` e ID do Calendar.
- **Sessão**: Se o bot travar, digite `menu` ou espere 5 min (timeout).
