from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "credentials/bot-ar-condicionado-658014857844.json"

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build("calendar", "v3", credentials=credentials)

agora = datetime.now()  # NAIVE de propósito

evento = {
    "summary": "Teste - Limpeza de Ar-Condicionado",
    "description": "Evento criado automaticamente pelo bot",
    "start": {
        "dateTime": (agora + timedelta(hours=0)).strftime("%Y-%m-%dT%H:%M:%S"),
        "timeZone": "America/Sao_Paulo",
    },
    "end": {
        "dateTime": (agora + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S"),
        "timeZone": "America/Sao_Paulo",
    },
}

evento_criado = service.events().insert(
    calendarId="yamyokai@gmail.com",
    body=evento
).execute()

print("Evento criado com sucesso!")
print("Link:", evento_criado.get("htmlLink"))
