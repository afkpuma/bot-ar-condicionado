# Contexto - Scripts

Este diretório contém ferramentas utilitárias para manutenção, diagnóstico e testes rápidos do sistema.

## `check_db.py`

Script para consultar rapidamente o estado atual de uma conversa no Supabase via terminal. Utilizado para depurar o fluxo do WhatsApp sem precisar abrir o dashboard do banco.

## `test_db_update.py`

Ferramenta de diagnóstico para validar permissões de escrita e existência de colunas (como `updated_at`) diretamente no Supabase.

## Recomendações
- Novos scripts utilitários devem seguir o padrão de importar o `supabase` de `services.supabase_client`.
- Sempre use `$env:PYTHONPATH="."` ao rodar scripts deste diretório para garantir que os imports de pacotes funcionem corretamente.
