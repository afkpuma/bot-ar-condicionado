"""
Configurações e constantes globais para o bot de ar-condicionado.
"""

from enum import Enum
from typing import Dict

# Dicionário que mapeia cada serviço para sua duração em horas
DURACAO_SERVICO: Dict[str, int] = {
    "limpeza": 1,      # 1 hora
    "instalacao": 3,   # 3 horas
    "manutencao": 1,   # 1 hora (visita técnica)
}

# EtapaConversa removida em favor de bot.states.ConversationState

# Configurações de timeout (em minutos)
TIMEOUT_SESSAO = 5

# Palavras-chave para saudação e ajuda
SAUDACOES = ["oi", "olá", "ola", "opa", "bom dia", "boa tarde", "boa noite", "ajuda", "voltar"]
PALAVRAS_RECOMECAR = ["menu", "recomeçar", "recomecar"]
