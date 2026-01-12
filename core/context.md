# Documentação: Core (`core/`)

O diretório `core/` contém os componentes fundamentais e utilitários globais do sistema.

## Componentes

### `config.py`
Gerenciamento de configurações usando `pydantic-settings`.
- Carrega variáveis de ambiente do `.env`.
- Define valores padrão para configurações críticas.
- Classes: `Settings`

### `logger.py`
Sistema de log centralizado.
- Configura o formato padrão de logs (Timestamp | Nível | Logger | Mensagem).
- Função: `get_logger(name)`

### `constants.py`
Constantes e Enumeradores globais.
- `ConversationState`: Enum para os estados da máquina de estados do bot (START, AGUARDANDO_NOME, etc).
- `TIMEOUT_SESSAO`: Constante de tempo para expiração de sessão (5 min).

### `exceptions.py`
Exceções customizadas da aplicação.
- `BotError`: Classe base para erros do bot.
