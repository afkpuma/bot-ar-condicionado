"""
Serviço de integração com Google Calendar API.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
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
    except Exception as e:
        logger.error(f"Erro ao listar eventos: {e}")
        return True

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

    evento: Dict[str, Any] = {
        "summary": f"{servico.capitalize()} - {cliente['nome']}",
        "description": f"""
    Cliente: {cliente['nome']}
    Telefone: {cliente['telefone']}

    Endereço:
    {cliente['endereco']['rua']}, {cliente['endereco']['numero']}
    {cliente['endereco']['bairro']} - {cliente['endereco']['cidade']}
    CEP: {cliente['endereco']['cep']}
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
    except Exception as e:
        logger.error(f"ERRO ao criar evento no Google Calendar: {str(e)}")
        raise e


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

