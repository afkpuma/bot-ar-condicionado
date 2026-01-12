# Contexto - Testes

Este diretório contém a estrutura necessária para garantir a qualidade e a resiliência do bot através de testes automatizados.

## Estrutura de Pastas

- **`unit/`**: Testes de funções isoladas que não dependem de rede ou banco de dados (ex: validação de data, parsing de endereço, lógica de menus). Devem ser rápidos e frequentes.
- **`integration/`**: Testes que verificam a comunicação entre componentes (ex: salvar no Supabase, criar evento no Google Calendar). Podem exigir credenciais de teste ou ambiente de stage.

## Execução

Utilizamos o framework `pytest`. Para rodar os testes:

```powershell
# Rodar todos os testes
python -m pytest

# Rodar apenas testes unitários
python -m pytest tests/unit
```

## Estratégia de Teste

1. **Decoupling**: Usamos a modularização para "mockar" (simular) o Google Calendar e o Supabase, permitindo testar a lógica do bot sem internet.
2. **Handlers**: Cada função no `services/state_handlers.py` deve ter um teste unitário correspondente que cubra caminhos felizes e casos de erro.
3. **Regressão**: Sempre que um bug for encontrado, um teste deve ser criado para garantir que ele não volte a ocorrer.
