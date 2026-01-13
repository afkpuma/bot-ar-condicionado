# Documentação: Services (`services/`)

O diretório `services/` contém integrações com sistemas externos e adaptadores.

## Integrações

### `google_calendar_service.py`
Responsável pela comunicação com a API do Google Calendar.
- Funções:
    - `horario_disponivel(...)`: Verifica conflitos de horário.
    - `criar_evento(...)`: Insere o evento na agenda.
    - Gerencia eventos no Google Calendar.
    - **Feature:** Gera link automático do Google Maps na descrição do evento com base no endereço do cliente.
    - Usa `ZoneInfo` para garantir horários corretos.

### `supabase_client.py`
Cliente inicializado do Supabase.
- Exporta a instância `supabase` pronta para uso.

### `agendamentos_service.py`
Camada de persistência para a tabela principal de agendamentos.
- Função `salvar_agendamento(...)`: Formata e insere dados na tabela `agendamentos`.
- Salva dados do agendamento e ID do evento do Calendar.

## Adaptadores

### `whatsapp_service.py`
**Legado/Adaptador**.
- Mantido para compatibilidade com o `main.py` antigo.
- Atua como uma fachada (Facade) para o `BotManager`.
- Função `processar_mensagem_whatsapp`: Apenas delega para `BotManager().process_message()`.
