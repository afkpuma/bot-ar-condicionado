from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone


SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "credentials/bot-ar-condicionado-658014857844.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)


DURACAO_SERVICO = {
    "limpeza": 1,
    "instalacao": 3,
    "manutencao": 1,
}


def horario_disponivel(calendar_id, data_hora_inicio, servico):
    duracao = DURACAO_SERVICO.get(servico)
    if not duracao:
        return False

    inicio = data_hora_inicio.replace(tzinfo=timezone.utc)

    fim = inicio + timedelta(hours=duracao)

    eventos = service.events().list(
        calendarId=calendar_id,
        timeMin=inicio.isoformat(),
        timeMax=fim.isoformat(),
        singleEvents=True
    ).execute()

    return len(eventos.get("items", [])) == 0
