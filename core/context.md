# Contexto - Core

Este diretório contém definições globais, constantes e tipos compartilhados que garantem a consistência de todo o sistema.

## `constants.py`

Centraliza dados que antes ficavam espalhados ou duplicados:

### Configurações de Negócio
- **`DURACAO_SERVICO`**: Mapeamento de tipo de serviço para tempo estimado (horas).
- **`SAUDACOES`**: Lista de palavras que iniciam o contato.
- **`PALAVRAS_RECOMECAR`**: Comandos que forçam o reset do fluxo.

### Gestão de Estados
- **`EtapaConversa (Enum)`**: Define rigorosamente todos os estados possíveis da máquina de estados do WhatsApp (SERVICO, DATA, HORA, NOME, RUA, NUMERO, BAIRRO, CIDADE, CEP, FINALIZAR).

### Configurações Técnicas
- **`TIMEOUT_SESSAO`**: Tempo limite de inatividade (5 minutos).

## Por que usar Core?
1. **DRY (Don't Repeat Yourself)**: Evita duplicação de lógicas de negócio.
2. **Tipo Seguro**: O uso de `Enums` evita erros de digitação em strings de estado.
3. **Facilidade de Mudança**: Mudar a duração de um serviço ou o tempo de timeout requer alteração em apenas um arquivo.
