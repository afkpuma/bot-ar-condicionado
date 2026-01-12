# Documentação: Services (`services/`)

O diretório `services/` contém integrações com sistemas externos e adaptadores.

## Integrações

### `google_calendar_service.py`
Responsável pela comunicação com a API do Google Calendar.
- Funções:
    - `horario_disponivel(...)`: Verifica conflitos de horário.
    - `criar_evento(...)`: Insere o evento na agenda.

### `supabase_client.py`
Cliente inicializado do Supabase.
- Exporta a instância `supabase` pronta para uso.

### `agendamentos_service.py`
Camada de persistência para a tabela principal de agendamentos.
- Função `salvar_agendamento(...)`: Formata e insere dados na tabela `agendamentos`.

## Adaptadores

### `whatsapp_service.py`
**Legado/Adaptador**.
- Mantido para compatibilidade com o `main.py` antigo.
- Atua como uma fachada (Facade) para o `BotManager`.
- Função `processar_mensagem_whatsapp`: Apenas delega para `BotManager().process_message()`.
