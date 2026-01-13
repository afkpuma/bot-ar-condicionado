"""
Serviço de agendamentos.

Gerencia a lógica de negócio relacionada a agendamentos,
incluindo validação e persistência no banco de dados.
"""

from datetime import datetime
from typing import Dict, Any, List
from services.supabase_client import supabase
from postgrest.exceptions import APIError

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


def buscar_agendamentos_futuros(telefone: str) -> List[Dict[str, Any]]:
    """
    Busca agendamentos futuros de um cliente pelo telefone.
    
    Args:
        telefone: Número de telefone do cliente.
    
    Returns:
        Lista de agendamentos futuros com status diferente de 'cancelado'.
        Cada item contém: id, servico, data_hora, calendar_event_id.
    
    Example:
        >>> buscar_agendamentos_futuros("11987654321")
        [{"id": 1, "servico": "limpeza", "data_hora": "2026-01-20T14:00:00", ...}]
    """
    from datetime import datetime
    
    agora = datetime.now().isoformat()
    
    try:
        response = supabase.table("agendamentos") \
            .select("id, servico, data_hora, calendar_event_id, nome_cliente") \
            .eq("telefone", telefone) \
            .neq("status", "cancelado") \
            .gt("data_hora", agora) \
            .order("data_hora", desc=False) \
            .execute()
        
        return response.data or []
    except APIError as e:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"Erro de API Supabase ao buscar agendamentos para {telefone}: {e}")
        return []
    except Exception as e:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.critical(f"Erro inesperado ao buscar agendamentos para {telefone}: {e}")
        return []


def marcar_agendamento_como_cancelado(agendamento_id: int) -> bool:
    """
    Marca um agendamento como cancelado (soft delete).
    
    Args:
        agendamento_id: ID do agendamento na tabela.
    
    Returns:
        True se a atualização foi bem-sucedida, False caso contrário.
    
    Note:
        Segue a regra de Soft Delete do rules.rpi - não deleta o registro,
        apenas atualiza o campo 'status' para 'cancelado'.
    """
    try:
        response = supabase.table("agendamentos") \
            .update({"status": "cancelado"}) \
            .eq("id", agendamento_id) \
            .execute()
        
        return len(response.data) > 0
    except APIError as e:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.error(f"Erro de API Supabase ao cancelar agendamento {agendamento_id}: {e}")
        return False
    except Exception as e:
        from core.logger import get_logger
        logger = get_logger(__name__)
        logger.critical(f"Erro inesperado ao cancelar agendamento {agendamento_id}: {e}")
        return False
