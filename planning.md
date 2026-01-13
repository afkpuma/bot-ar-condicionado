# 📅 PLANNING.md

> **Status:** Em Desenvolvimento Ativo
> **Última Atualização:** 2026-01-XX
> **Objetivo:** Documento vivo para rastreamento de decisões arquiteturais, roadmap de funcionalidades e dívidas técnicas.

---

## 🧠 Contexto e Diretrizes (Córtex do Projeto)

Este arquivo complementa o `context.md` e o `rules.rpi`. Enquanto eles definem "o que é" e "como fazer", este define "o que faremos" e "por que decidimos assim".

### Decisões Arquiteturais (Decision Log)
| Data | Decisão | Motivação (O Porquê) | Status |
| :--- | :--- | :--- | :--- |
| **Início** | **Clean Architecture (Core/Bot/Services)** | Desacoplar a lógica do bot das ferramentas externas (Google/Supabase) para facilitar testes e manutenção. | ✅ Implementado |
| **Início** | **Pydantic para Modelos** | Garantir a integridade dos dados na entrada e saída, evitando "type errors" silenciosos em runtime. | ✅ Implementado |
| **Início** | **Supabase como Backend** | Solução "BaaS" que agiliza o setup de banco de dados e autenticação (futura) sem complexidade de infra. | ✅ Implementado |
| **2026-01** | **Máquina de Estados (FSM) no Banco** | Persistir o estado da conversa (`etapa`) no banco permite que o bot não "esqueça" o usuário se o servidor reiniciar. | ✅ Implementado |
| **2026-01** | **UX Fluida (Planejado)** | Mudar de "Input Rígido" para "Seleção Guiada" (ex: listar horários em vez de pedir input manual) para reduzir fricção. | 🚧 Em Andamento |
| **2026-01** | **Handlers Stateless para Listas** | Não persistir listas complexas (horários/agendamentos) no contexto do banco para evitar erros de schema. Re-buscar dados na ação. | ✅ Implementado |
| **2026-01** | **TRANSIENT_KEYS no Manager** | Dupla proteção: mesmo que um handler salve dados transientes, o `BotManager.save_context()` filtra automaticamente antes do upsert. | ✅ Implementado |
| **2026-01** | **Consistência de Menu e Reset** | Padronizar menus de erro com emojis e permitir reset via saudações (excluindo 'voltar') para recuperar fluxos perdidos. | ✅ Implementado |
| **2026-01** | **Menu Explícito (Cancelar)** | Tornar a opção 'Cancelar' visível (Opção 4) para melhorar a descoberta e UX, evitando comandos ocultos. | ✅ Implementado |

### 📝 Detalhamento: Stateless Pattern

**Problema Original:** O `CancellationHandler` salvava `agendamentos_para_cancelar` (lista de dicts) no `context.data`, que era persistido no Supabase. A tabela `conversas_whatsapp` não possui colunas para listas complexas, causando erros de schema.

**Solução em 3 Camadas:**
1. **Handler Layer**: `CancellationHandler` não salva listas no contexto. Re-busca `buscar_agendamentos_futuros()` no momento da seleção.
2. **Manager Layer**: `TRANSIENT_KEYS = {"horarios_disponiveis", "agendamentos_para_cancelar"}` filtra dados antes do `upsert`.
3. **Benefit**: Atomicidade garantida + proteção dupla contra vazamento de dados transientes.

---

## 🗺️ Roadmap de Desenvolvimento

O foco atual é transformar a prova de conceito (PoC) em um produto com UX robusta.

### 📌 Fase 1: Resiliência e Navegação (UX Basics)
*Objetivo: Permitir que o usuário erre e corrija sem frustração.*

- [x] **1.1. Mapeamento Reverso de Estados**
  - **Arquivo:** `bot/handlers/booking_handler.py`
  - **Tarefa:** Criar dicionário constante `PREVIOUS_STATE` mapeando cada estado para seu anterior lógico (ex: `PROVIDE_NUMBER` -> `PROVIDE_STREET`).
  
- [x] **1.2. Comando Universal "Voltar"**
  - **Arquivo:** `bot/handlers/booking_handler.py` (método `handle`)
  - **Tarefa:** Interceptar comandos como "voltar", "corrigir", "anterior". Usar o mapa reverso para restaurar o estado e perguntar novamente.
  
- [x] **1.3. Testes de Navegação**
  - **Arquivo:** `tests/integration/test_navigation.py`
  - **Tarefa:** Simular fluxo onde usuário avança 3 passos, volta 1 e conclui.

### 📌 Fase 2: Inteligência de Agenda (Smart Scheduling)
*Objetivo: Acabar com a "adivinhação" de horários.*

- [x] **2.1. Lógica de Slots Disponíveis**
  - **Arquivo:** `services/google_calendar_service.py`
  - **Tarefa:** Implementar `listar_horarios_livres(data: date, servico: str) -> List[str]`.
  - **Regra:** Iterar horário comercial (08-18h), checar duração do serviço e conflitos. Retornar apenas horários livres.

- [x] **2.2. Apresentação de Horários**
  - **Arquivo:** `bot/handlers/booking_handler.py` (`_handle_date`)
  - **Tarefa:** Ao receber uma data válida, não perguntar "Qual horário?". Em vez disso, listar os slots: "Tenho estes horários: 1) 09:00, 2) 14:00...".

- [x] **2.3. Seleção Facilitada**
  - **Arquivo:** `bot/handlers/booking_handler.py` (`_handle_time`)
  - **Tarefa:** Aceitar input numérico (opção do menu) ou string direta ("14:00").

### 📌 Fase 3: Segurança e Confirmação
*Objetivo: Garantir precisão antes da persistência.*

- [x] **3.1. Estado de Confirmação**
  - **Arquivo:** `bot/states.py`
  - **Tarefa:** Adicionar `CONFIRMATION` ao Enum `ConversationState`.

- [x] **3.2. Fluxo de Review**
  - **Arquivo:** `bot/handlers/booking_handler.py`
  - **Tarefa:** Antes de salvar:
    1. Exibir resumo completo (Serviço, Data/Hora, Endereço).
    2. Perguntar "Confirma? (Sim/Não)".
    3. Se "Não", oferecer menu de edição rápida.

### 📌 Fase 4: Gestão Completa (Cancelamento)
*Objetivo: Ciclo de vida completo do agendamento.*

- [x] **4.1. Busca de Agendamentos**
  - **Arquivo:** `services/agendamentos_service.py`
  - **Tarefa:** `buscar_agendamentos_futuros(telefone)`.

- [x] **4.2. CancellationHandler Stateless**
  - **Arquivo:** `bot/handlers/cancellation_handler.py`
  - **Tarefa:** Criar handler dedicado para o fluxo de cancelamento.
  - **Lógica:** Listar agendamentos -> Confirmar (rebuscando dados) -> Deletar no Calendar -> Atualizar no Supabase.

- [x] **4.3. UX: Cancelamento no Menu Principal**
  - **Arquivo:** `bot/handlers/info_handler.py` e `cancellation_handler.py`
  - **Tarefa:** Adicionar opção "4. Meus Agendamentos / Cancelar" no menu inicial.

---

## 🧹 Dívida Técnica & Melhorias Futuras

- **Testes Unitários:** Aumentar cobertura dos handlers (atualmente focado em integração).
- **Tratamento de Fuso Horário:** Revisar `zoneinfo` para garantir robustez em horário de verão/mudanças.
- **Webhook Evolution API:** Implementar validação de assinatura/token do webhook para segurança.
- **Filas:** (Futuro) Processar criação de eventos em background task para não travar a resposta HTTP do webhook.

---

> **Nota para a IA:** Ao sugerir código, verifique sempre este arquivo para garantir que a sugestão está alinhada com a fase atual e com as decisões arquiteturais já tomadas.