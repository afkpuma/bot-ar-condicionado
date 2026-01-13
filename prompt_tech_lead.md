# Contexto e Persona
Atue como um Especialista em Python e Tech Lead. Vamos iniciar a fase de **Research (Pesquisa)** para a correção e evolução deste bot.

## Passo 1: Análise e Pesquisa
1. **Analise a estrutura atual** de arquivos e pastas do projeto, com foco especial nos Handlers (`bot/handlers/`) e no Gerenciador (`bot/manager.py`).
2. **Identifique lacunas de Lógica:** Verifique por que comandos de saudação (ex: "oi", "olá") não estão resetando o fluxo quando o usuário já está em um estado avançado (ex: `SELECT_SERVICE`). Analise o arquivo `bot/handlers/info_handler.py` e sua relação com `core/constants.py`.
3. **Verifique padrões:** Existem arquivos que não estão seguindo a estrutura modular adequada ou onde a responsabilidade está misturada (ex: mensagens de erro hardcoded no `BookingHandler` que não refletem as opções reais do menu)?

4. **Foco em UX:** Certifique-se de que todas as mensagens de erro ou prompts orientem o usuário a reiniciar (`menu`) em vez de oferecer comandos complexos de navegação.

5. **Segurança de Tipos:** Verifique se novos inputs (como CEP ou Data) possuem validação rigorosa antes de serem processados.

**NÃO gere código ainda.** Apenas liste suas descobertas, explique a causa raiz dos bugs encontrados (especialmente o fluxo de "Olá" falhando) e sugira quais arquivos precisam ser refatorados.

---

## Passo 2: Plano de Implementação (Aguarde meu OK para gerar)
*Nota: Após sua resposta de pesquisa, eu solicitarei este plano com o seguinte prompt (já deixo registrado aqui para contexto):*

"Com base na sua análise de Research, gere um **Plano de Implementação** detalhado em formato Markdown. O plano deve conter:

1. **Lista de Arquivos:** Quais arquivos exatos serão criados, movidos ou atualizados.
2. **Correções Lógicas:** Explique como corrigiremos o `InfoHandler` para aceitar `SAUDACOES` e como padronizar o menu de erro no `BookingHandler`.
3. **Passo a Passo:** Quebre as mudanças em tarefas pequenas e lógicas (ex: 'Passo 1: Atualizar InfoHandler', 'Passo 2: Refatorar mensagens de erro').
4. **Critérios de Validação:** Para cada passo, o que devo rodar para garantir que funciona (ex: comando de teste ou input esperado no bot).

5. **Arquivos Afetados:** Lista clara de onde tocaremos.

6. **Mudanças Lógicas:** Explicação do "porquê" e do "como".

7. **Passo a Passo:** Tarefas atômicas.

8. **Validação:** Como testar (comando curl ou input do bot) para garantir que não houve regressão (ex: testar agendamento completo e cancelamento)."

Gere apenas o plano/documento. Não implemente o código agora."