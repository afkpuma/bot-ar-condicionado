"""
Serviço de integração com Google Calendar API.
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from core.constants import DURACAO_SERVICO

# Carrega as variáveis de ambiente
load_dotenv()

# ID do calendário (seu email do Google)
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

if not GOOGLE_CALENDAR_ID:
    print("⚠️ AVISO: GOOGLE_CALENDAR_ID não configurado no .env!")

# Timezone do Brasil (São Paulo)
TIMEZONE_BR = ZoneInfo("America/Sao_Paulo")

# Escopos de permissão necessários
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Caminho para o arquivo de credenciais
# Mantendo o caminho original para não quebrar a aplicação
SERVICE_ACCOUNT_FILE = "credentials/bot-ar-condicionado-658014857844.json"

# Inicialização do serviço ( Singleton-like para o módulo )
try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("calendar", "v3", credentials=credentials)
except Exception as e:
    print(f"⚠️ Erro ao inicializar Google Calendar: {e}")
    service = None

def horario_disponivel(
    calendar_id: str,
    data_hora_inicio: datetime,
    servico: str
) -> bool:
    """
    Verifica se um horário está disponível no Google Calendar.
    """
    if not service:
        return True # Fallback para não travar se a API falhar

    duracao = DURACAO_SERVICO.get(servico)
    if not duracao:
        return False

    inicio = data_hora_inicio.replace(tzinfo=TIMEZONE_BR)
    fim = inicio + timedelta(hours=duracao)

    try:
        eventos = service.events().list(
            calendarId=calendar_id,
            timeMin=inicio.isoformat(),
            timeMax=fim.isoformat(),
            singleEvents=True
        ).execute()

        return len(eventos.get("items", [])) == 0
    except Exception as e:
        print(f"Erro ao listar eventos: {e}")
        return True

def criar_evento(
    calendar_id: str,
    data_hora_inicio: datetime,
    servico: str,
    cliente: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Cria um evento no Google Calendar.
    """
    if not service:
        raise Exception("Serviço Google Calendar não inicializado.")

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
            calendarId=calendar_id,
            body=evento
        ).execute()
        return evento_criado
    except Exception as e:
        print(f"ERRO ao criar evento no Google Calendar: {str(e)}")
        raise e
