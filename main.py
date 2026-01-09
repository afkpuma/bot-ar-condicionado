from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from scripts.calendar_utils import horario_disponivel, criar_evento
from services.agendamentos_service import salvar_agendamento

class AgendamentoRequest(BaseModel):
    servico: str
    data: str   # YYYY-MM-DD
    hora: str   # HH:MM

class MensagemWhatsApp(BaseModel):
    telefone: str
    mensagem: str

app = FastAPI()

@app.get("/")
def home():
    return {"mensagem": "API do bot de ar-condicionado funcionando"}

@app.post("/whatsapp")
def receber_mensagem(dados: MensagemWhatsApp):
    texto = dados.mensagem.lower()

    if "limpeza" in texto:
        servico = "limpeza"
        resposta = (
            "Perfeito 😊\n"
            "O serviço de *Limpeza de Ar-Condicionado* custa R$ 150,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "instala" in texto:
        servico = "instalacao"
        resposta = (
            "Ótima escolha 😊\n"
            "O serviço de *Instalação de Ar-Condicionado* custa R$ 350,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "manuten" in texto:
        servico = "manutencao"
        resposta = (
            "Entendido 👍\n"
            "Para *Manutenção*, realizamos uma visita técnica.\n"
            "Qual dia e horário você prefere?"
        )

    else:
        servico = None
        resposta = (
            "Olá! 👋\n"
            "Trabalhamos com os seguintes serviços:\n"
            "- Limpeza\n"
            "- Instalação\n"
            "- Manutenção\n\n"
            "Qual serviço você deseja?"
        )

    

    return {
        "telefone": dados.telefone,
        "resposta": resposta
    }

@app.post("/agendar")
def agendar(request: AgendamentoRequest):
    try:
        data_hora = datetime.strptime(
            f"{request.data} {request.hora}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError:
        return {"erro": "Data ou hora em formato inválido"}

    disponivel = horario_disponivel(
        calendar_id="yamyokai@gmail.com",
        data_hora_inicio=data_hora,
        servico=request.servico
    )

    if not disponivel:
        return {"status": "indisponivel"}

    evento = criar_evento(
        calendar_id="yamyokai@gmail.com",
        data_hora_inicio=data_hora,
        servico=request.servico
    )
    endereco = {
    "rua": "Rua Exemplo",
    "numero": "123",
    "bairro": "Centro",
    "cidade": "São Paulo",
    "cep": "00000-000",
}

    salvar_agendamento(
    nome_cliente="Cliente WhatsApp",
    telefone="000000000",
    servico=request.servico,
    data_hora=data_hora,
    endereco=endereco,
    calendar_event_id=evento.get("id")
)


    return {
        "status": "confirmado",
        "evento_id": evento.get("id"),
        "link": evento.get("htmlLink"),
    }




