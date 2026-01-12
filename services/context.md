# Contexto - Services

Este diretório contém a lógica de processamento de mensagens e integração com o banco de dados.

## `whatsapp_service.py`

Gerencia o fluxo conversacional do bot. Atua como orquestrador principal (`Engine`), decidindo para qual estado o usuário deve ir. Ele delega a validação de dados e regras de negócio específicas para o `state_handlers.py`.

## `state_handlers.py`

Contém a lógica de validação e processamento para cada estado (SERVICO, DATA, HORA, etc.). Isolando essa lógica, garantimos que o motor do bot (`whatsapp_service.py`) permaneça limpo e fácil de manter.

## `google_calendar_service.py`

Interface de integração com a API do Google Calendar. Fornece métodos para:
- `horario_disponivel`: Verifica conflitos de agenda.
- `criar_evento`: Consolida o agendamento no calendário.

## `agendamentos_service.py`

Interface direta com a tabela `agendamentos` do Supabase. Responsável pela persistência final dos dados após confirmação.
