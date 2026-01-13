# Documentação: Bot (`bot/`)

O diretório `bot/` encapsula a lógica conversacional e o gerenciamento de estado do bot.

## Componentes Principais

### `manager.py`: `BotManager`
O orquestrador central do bot.
- Mantém a lista de Handlers registrados.
- Gerencia o contexto do usuário (Recupera/Salva no Supabase).
- Roteia mensagens para o handler apropriado (`process_message`).

### `context.py`: `UserContext`
Representa o estado atual de um usuário.
- Atributos: `phone`, `state` (Enum), `data` (Dict), `updated_at`.
- Abstrai a complexidade do banco de dados para os handlers.

### `states.py`
Re-exporta `ConversationState` do core para conveniência, ou define estados específicos se necessário.

## Handlers (`bot/handlers/`)
Os handlers implementam a lógica de negócio para estados ou intenções específicas. Todo handler herda de `BaseHandler`.

### `base.py`: `BaseHandler`
Interface abstrata que define:
- `should_handle(context, message)`: Retorna True se este handler deve processar a mensagem.
- `handle(context, message)`: Executa a lógica e retorna a resposta (str).

### `info_handler.py`: `InfoHandler`
Cuida de comandos informativos e globais.
- Comandos: `menu`, `oi`, `ajuda`.
- Responsável por resetar o fluxo para o início e exibir o menu principal (Opções 1-4).

### `booking_handler.py`: `BookingHandler`
Gerencia o fluxo complexo de agendamento (Máquina de Estados).
- Coleta dados passo-a-passo: Nome -> Endereço -> Data -> Confirmação.
- Interage com `services` para verificar agenda e salvar dados.

### `cancellation_handler.py`: `CancellationHandler`
Gerencia o fluxo de cancelamento e visualização de agendamentos.
- Gatilhos: Comando "cancelar", opção "4" no menu principal ou estado `SELECT_CANCEL_ID`.
- Lógica Stateless: Re-busca agendamentos no momento da ação para garantir consistência.
