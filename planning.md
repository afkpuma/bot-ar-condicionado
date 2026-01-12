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

---

## 🗺️ Roadmap de Desenvolvimento

O foco atual é transformar a prova de conceito (PoC) em um produto com UX robusta.

### 📌 Fase 1: Resiliência e Navegação (UX Basics)
*Objetivo: Permitir que o usuário erre e corrija sem frustração.*

- [ ] **1.1. Mapeamento Reverso de Estados**
  - **Arquivo:** `bot/handlers/booking_handler.py`
  - **Tarefa:** Criar dicionário constante `PREVIOUS_STATE` mapeando cada estado para seu anterior lógico (ex: `PROVIDE_NUMBER` -> `PROVIDE_STREET`).
  
- [ ] **1.2. Comando Universal "Voltar"**
  - **Arquivo:** `bot/handlers/booking_handler.py` (método `handle`)
  - **Tarefa:** Interceptar comandos como "voltar", "corrigir", "anterior". Usar o mapa reverso para restaurar o estado e perguntar novamente.
  
- [ ] **1.3. Testes de Navegação**
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

- [ ] **3.1. Estado de Confirmação**
  - **Arquivo:** `bot/states.py`
  - **Tarefa:** Adicionar `CONFIRMATION` ao Enum `ConversationState`.

- [ ] **3.2. Fluxo de Review**
  - **Arquivo:** `bot/handlers/booking_handler.py`
  - **Tarefa:** Antes de salvar:
    1. Exibir resumo completo (Serviço, Data/Hora, Endereço).
    2. Perguntar "Confirma? (Sim/Não)".
    3. Se "Não", oferecer menu de edição rápida.

### 📌 Fase 4: Gestão Completa (Cancelamento)
*Objetivo: Ciclo de vida completo do agendamento.*

- [ ] **4.1. Busca de Agendamentos**
  - **Arquivo:** `services/agendamentos_service.py`
  - **Tarefa:** `buscar_agendamentos_futuros(telefone)`.

- [ ] **4.2. CancellationHandler**
  - **Arquivo:** `bot/handlers/cancellation_handler.py`
  - **Tarefa:** Criar handler dedicado para o fluxo de cancelamento.
  - **Lógica:** Listar agendamentos -> Confirmar -> Deletar no Calendar -> Atualizar no Supabase.

---

## 🧹 Dívida Técnica & Melhorias Futuras

- **Testes Unitários:** Aumentar cobertura dos handlers (atualmente focado em integração).
- **Tratamento de Fuso Horário:** Revisar `zoneinfo` para garantir robustez em horário de verão/mudanças.
- **Webhook Evolution API:** Implementar validação de assinatura/token do webhook para segurança.
- **Filas:** (Futuro) Processar criação de eventos em background task para não travar a resposta HTTP do webhook.

---

> **Nota para a IA:** Ao sugerir código, verifique sempre este arquivo para garantir que a sugestão está alinhada com a fase atual e com as decisões arquiteturais já tomadas.