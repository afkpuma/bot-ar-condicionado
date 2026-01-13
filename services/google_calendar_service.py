"""
Serviço de integração com Google Calendar API.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta, date, time
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional, List

from core.constants import DURACAO_SERVICO
from core.config import get_settings
from core.logger import get_logger

# Logger
logger = get_logger(__name__)

# Configuração Centralizada
settings = get_settings()
GOOGLE_CALENDAR_ID = settings.GOOGLE_CALENDAR_ID
# Convert FilePath to str if needed, though pydantic usually handles it.
CREDENTIALS_PATH = str(settings.GOOGLE_CREDENTIALS_PATH)

# Timezone do Brasil (São Paulo)
TIMEZONE_BR = ZoneInfo("America/Sao_Paulo")

# Escopos de permissão necessários
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_calendar_service():
    """Autentica e retorna o serviço do Google Calendar"""
    if not os.path.exists(CREDENTIALS_PATH):
        logger.error(f"Arquivo de credenciais não encontrado: {CREDENTIALS_PATH}")
        return None
        
    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=creds)
        logger.debug("Google Calendar API inicializada com sucesso.")
        return service
    except Exception as e:
        logger.error(f"Erro ao inicializar Google Calendar: {e}")
        return None

# Inicialização Lazy do serviço para evitar travamento na importação se falhar
service = get_calendar_service()

def horario_disponivel(
    data_hora_inicio: datetime,
    servico: str,
    calendar_id: Optional[str] = None
) -> bool:
    """
    Verifica se um horário está disponível no Google Calendar.
    Se calendar_id não for fornecido, usa o padrão das configurações.
    """
    if not service:
        logger.warning("Serviço de calendário indisponível. Assumindo horário livre para teste.")
        return True # Fallback

    target_calendar_id = calendar_id or GOOGLE_CALENDAR_ID

    duracao = DURACAO_SERVICO.get(servico)
    if not duracao:
        return False

    inicio = data_hora_inicio.replace(tzinfo=TIMEZONE_BR)
    fim = inicio + timedelta(hours=duracao)

    try:
        eventos = service.events().list(
            calendarId=target_calendar_id,
            timeMin=inicio.isoformat(),
            timeMax=fim.isoformat(),
            singleEvents=True
        ).execute()

        return len(eventos.get("items", [])) == 0
    except HttpError as e:
        logger.error(f"Erro de API do Google Calendar ao listar eventos: {e}")
        # Em caso de erro de API, assumir ocupado para segurança
        return False
    except Exception as e:
        logger.critical(f"Erro inesperado ao verificar disponibilidade: {e}")
        raise

def criar_evento(
    data_hora_inicio: datetime,
    servico: str,
    cliente: Dict[str, Any],
    calendar_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Cria um evento no Google Calendar.
    """
    if not service:
        raise Exception("Serviço Google Calendar não inicializado.")

    target_calendar_id = calendar_id or GOOGLE_CALENDAR_ID

    duracao = DURACAO_SERVICO.get(servico)
    if not duracao:
        return None

    inicio = data_hora_inicio.replace(tzinfo=TIMEZONE_BR)
    fim = inicio + timedelta(hours=duracao)

    # Monta endereço completo para o link do Google Maps
    endereco = cliente.get('endereco', {})
    endereco_completo = (
        f"{endereco.get('rua', '')}, {endereco.get('numero', '')}, "
        f"{endereco.get('bairro', '')} - {endereco.get('cidade', '')}, "
        f"CEP {endereco.get('cep', '')}"
    )
    
    # URL encode para o Maps
    from urllib.parse import quote
    maps_url = f"https://www.google.com/maps/search/?api=1&query={quote(endereco_completo)}"

    evento: Dict[str, Any] = {
        "summary": f"{servico.capitalize()} - {cliente['nome']}",
        "description": f"""Cliente: {cliente['nome']}
Telefone: {cliente['telefone']}

Endereço:
{endereco.get('rua', 'N/A')}, {endereco.get('numero', 'S/N')}
{endereco.get('bairro', 'N/A')} - {endereco.get('cidade', 'N/A')}
CEP: {endereco.get('cep', 'N/A')}

📍 Ver no Mapa:
{maps_url}
""",
        "start": {
            "dateTime": inicio.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Sao_Paulo",
        },
        "end": {
            "dateTime": fim.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": "America/Sao_Paulo",
        },
    }

    try:
        evento_criado = service.events().insert(
            calendarId=target_calendar_id,
            body=evento
        ).execute()
        logger.info(f"Evento criado: {evento_criado.get('htmlLink')}")
        return evento_criado
    except HttpError as e:
        logger.error(f"Erro de API do Google Calendar ao criar evento: {e}")
        raise
    except Exception as e:
        logger.critical(f"Erro inesperado ao criar evento: {e}")
        raise


def listar_horarios_livres(data: date, servico: str) -> List[str]:
    """
    Lista os horários livres para um determinado dia e serviço.

    Args:
        data: A data para verificar disponibilidade.
        servico: O tipo de serviço (para cálculo de duração).

    Returns:
        Lista de strings com horários disponíveis no formato "HH:MM".
    """
    horarios_livres: List[str] = []

    # Horário comercial: 08:00 às 18:00
    hora_inicio = 8
    hora_fim = 18

    # Se a data for hoje, filtra horários que já passaram
    agora = datetime.now(TIMEZONE_BR)
    eh_hoje = data == agora.date()

    for hora in range(hora_inicio, hora_fim):
        hora_slot = time(hour=hora, minute=0)
        data_hora_inicio = datetime.combine(data, hora_slot)

        # Se for hoje e o horário já passou, pula
        if eh_hoje and data_hora_inicio.replace(tzinfo=TIMEZONE_BR) <= agora:
            continue

        # Verifica disponibilidade usando a função existente
        if horario_disponivel(data_hora_inicio, servico):
            horarios_livres.append(f"{hora:02d}:00")

    return horarios_livres


def cancelar_evento(event_id: str, calendar_id: Optional[str] = None) -> bool:
    """
    Remove um evento do Google Calendar.
    
    Args:
        event_id: ID do evento a ser cancelado.
        calendar_id: ID do calendário (opcional, usa o padrão se não fornecido).
    
    Returns:
        True se o evento foi cancelado ou já não existia.
        False apenas em casos de erro crítico de conexão.
    
    Note:
        Esta função é resiliente: se o evento já foi deletado manualmente,
        retorna True para não bloquear o fluxo de cancelamento no banco.
    """
    if not service:
        logger.warning("Serviço de calendário indisponível. Cancelamento no Calendar ignorado.")
        return True  # Permite continuar com cancelamento no banco
    
    target_calendar_id = calendar_id or GOOGLE_CALENDAR_ID
    
    try:
        service.events().delete(
            calendarId=target_calendar_id,
            eventId=event_id
        ).execute()
        logger.info(f"Evento {event_id} cancelado com sucesso no Google Calendar.")
        return True
    except HttpError as e:
        # HttpError 404 = evento já foi deletado, o que é aceitável
        if e.resp.status == 404:
            logger.warning(f"Evento {event_id} não encontrado no Calendar (já deletado?).")
            return True
        
        # Outros erros de API (permissão, quota, etc.)
        logger.error(f"Erro de API do Google Calendar ao cancelar evento {event_id}: {e}")
        return False
    except Exception as e:
        logger.critical(f"Erro inesperado ao cancelar evento {event_id}: {e}")
        return False
