"""
Serviço de agendamentos.

Gerencia a lógica de negócio relacionada a agendamentos,
incluindo validação e persistência no banco de dados.
"""

from datetime import datetime
from typing import Dict, Any, List
from services.supabase_client import supabase

from core.constants import DURACAO_SERVICO


def salvar_agendamento(
    nome_cliente: str,
    telefone: str,
    servico: str,
    data_hora: datetime,
    endereco: Dict[str, str],
    calendar_event_id: str
) -> List[Dict[str, Any]]:
    """
    Salva um agendamento no banco de dados Supabase.
    
    Args:
        nome_cliente: Nome completo do cliente
        telefone: Telefone com DDD (apenas números)
        servico: Tipo de serviço (limpeza, instalacao, manutencao)
        data_hora: Data e hora do agendamento
        endereco: Dicionário com rua, numero, bairro, cidade, cep
        calendar_event_id: ID do evento criado no Google Calendar
    
    Returns:
        Lista com os dados do agendamento salvo
    
    Raises:
        ValueError: Se o serviço for inválido
    
    Example:
        >>> salvar_agendamento(
        ...     nome_cliente="João Silva",
        ...     telefone="11987654321",
        ...     servico="limpeza",
        ...     data_hora=datetime(2026, 1, 15, 14, 30),
        ...     endereco={"rua": "Rua A", "numero": "123", ...},
        ...     calendar_event_id="abc123"
        ... )
    """
    # Busca a duração do serviço no dicionário
    duracao = DURACAO_SERVICO.get(servico)

    if not duracao:
        raise ValueError(f"Serviço inválido: {servico}. Use: limpeza, instalacao ou manutencao")

    # Monta o objeto de dados para inserir no banco
    data: Dict[str, Any] = {
        "nome_cliente": nome_cliente,
        "telefone": telefone,
        "servico": servico,
        "data_hora": data_hora.isoformat(),  # Converte datetime para string ISO
        "duracao_horas": duracao,

        # Campos de endereço
        "rua": endereco["rua"],
        "numero": endereco["numero"],
        "bairro": endereco["bairro"],
        "cidade": endereco["cidade"],
        "cep": endereco["cep"],
        "complemento": endereco.get("complemento"),  # Opcional

        # Referência ao evento do Google Calendar
        "calendar_event_id": calendar_event_id,
        
        # Status inicial do agendamento
        "status": "confirmado"
    }

    # Insere no banco de dados Supabase
    response = supabase.table("agendamentos").insert(data).execute()
    return response.data

