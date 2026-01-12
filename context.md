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
├── core/                        # Configurações globais e Enums
│   ├── constants.py             # Centralização de durações e estados
│   └── context.md               # Documentação das constantes
│
├── services/                    # Lógica de negócio
│   ├── whatsapp_service.py      # Orquestrador de mensagens
│   ├── state_handlers.py        # Handlers individuais por estado
│   ├── agendamentos_service.py  # Persistência no banco
│   ├── google_calendar_service.py # Integração com Google Calendar
│   ├── supabase_client.py       # Cliente do Supabase
│   └── context.md               # Documentação detalhada de services
│
├── models/                      # Modelos Pydantic
│   └── __init__.py              # Definições de Cliente e Agendamento
│
├── tests/                       # Testes automatizados
│   ├── unit/                    # Testes de funções isoladas
│   ├── integration/             # Testes de fluxo completo
│   └── context.md               # Estratégia de testes
│
├── scripts/                     # Scripts de apoio e automação
│
└── credentials/                 # Credenciais (NÃO COMMITAR)
    └── bot-ar-condicionado-*.json
```

## 🔄 Fluxo de Dados
1. **Cliente envia mensagem** no WhatsApp
2. **WPPConnect** envia webhook POST para `/whatsapp`
3. **whatsapp_service.py** processa a mensagem e gerencia o estado da conversa
4. Sistema **verifica disponibilidade** no Google Calendar
5. **Cria evento** no Google Calendar
6. **Salva agendamento** no Supabase
7. **Retorna confirmação** para o cliente via WhatsApp

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
- servico, data, hora, nome (text)
- rua, numero, bairro, cidade, cep (text)
- updated_at (timestamp) - Controle de timeout
- created_at (timestamp)

## 📚 Roadmap de Aprendizado
- [x] Visão geral do sistema (Sem código)
- [x] Preparação do ambiente
- [x] FastAPI Simples
- [x] Integração com Supabase
- [x] Integração com Google Calendar
- [x] Melhorias de código (Type Hints, Validações)
- [ ] Integração completa com WhatsApp usando Evolution - API de Webhooks
- [ ] Testes automatizados
- [ ] Deploy em produção

## 🔍 Troubleshooting (Integrações)

### Google Calendar
1. **Credenciais**: O arquivo JSON deve estar em `credentials/` e ser UTF-8 **sem BOM**.
2. **Email no .env**: Certifique-se de que o `GOOGLE_CALENDAR_ID` é exatamente o email do seu Gmail pessoal.
3. **Compartilhamento**: O calendário deve ser compartilhado com o email da Service Account (`client_email` do JSON).
4. **Timezone**: O sistema usa `America/Sao_Paulo`. Datas devem ser futuras.
5. **Logs**: Procure por prefixos `DEBUG:` no terminal para ver o link do evento criado.

### Supabase
1. **Variáveis de Ambiente**: Verifique `SUPABASE_URL` e `SUPABASE_KEY` no `.env`.
2. **Tabelas**: Certifique-se de que as tabelas `agendamentos` e `conversas_whatsapp` existem.

### WhatsApp
1. **Reset de Conversa**: Use `menu` ou `recomeçar` para forçar o reinício a qualquer momento.
2. **Saudações**: `oi` ou `opa` só resetam se você não estiver no meio de um agendamento.
3. **Timeout**: A sessão expira após 5 minutos de silêncio para segurança dos dados.
4. **Webhook**: O endpoint `/whatsapp` deve estar acessível via Ngrok (se local).
