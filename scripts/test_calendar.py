from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]

SERVICE_ACCOUNT_FILE = "credentials/bot-ar-condicionado-658014857844.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)

evento = {
    "summary": "Teste - Limpeza de Ar-Condicionado",
    "description": "Evento criado automaticamente pelo bot",
    "start": {
        "dateTime": (datetime.now() + timedelta(hours=1)).isoformat(),
        "timeZone": "America/Sao_Paulo",
    },
    "end": {
        "dateTime": (datetime.now() + timedelta(hours=2)).isoformat(),
        "timeZone": "America/Sao_Paulo",
    },
}

evento_criado = service.events().insert(
    calendarId="yamyokai@gmail.com",
    body=evento
).execute()

print("Evento criado com sucesso!")
print("Link:", evento_criado.get("htmlLink"))
