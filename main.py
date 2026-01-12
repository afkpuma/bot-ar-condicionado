from fastapi import FastAPI, Query
from pydantic import BaseModel
from datetime import datetime

from scripts.calendar_utils import horario_disponivel, criar_evento
from services.agendamentos_service import salvar_agendamento
from services.whatsapp_service import processar_mensagem_whatsapp


# =========================
# MODELOS
# =========================

class Endereco(BaseModel):
    rua: str
    numero: str
    bairro: str
    cidade: str
    cep: str


class Cliente(BaseModel):
    nome: str
    telefone: str
    endereco: Endereco


class AgendamentoRequest(BaseModel):
    servico: str
    data: str
    hora: str
    cliente: Cliente


class MensagemWhatsApp(BaseModel):
    telefone: str
    mensagem: str


# =========================
# APP
# =========================

app = FastAPI(title="Bot de Ar-Condicionado")


@app.get("/")
def home():
    return {"mensagem": "API do bot de ar-condicionado funcionando"}


# =========================
# WHATSAPP (REAL + SIMULAÇÃO)
# =========================

@app.post("/whatsapp")
def receber_mensagem(
    dados: MensagemWhatsApp,
    simulacao: bool = Query(False, description="Se true, retorna dados de teste")
):
    """
    Recebe uma mensagem do WhatsApp e retorna a resposta do bot.
    Para teste, use ?simulacao=true
    """
    try:
        resposta = processar_mensagem_whatsapp(
            telefone=dados.telefone,
            mensagem=dados.mensagem
        )
    except Exception as e:
        return {"erro": str(e)}

    if simulacao:
        return {
            "simulacao": True,
            "telefone": dados.telefone,
            "mensagem_enviada": dados.mensagem,
            "resposta_bot": resposta
        }

    return {
        "telefone": dados.telefone,
        "resposta": resposta
    }


# =========================
# AGENDAMENTO DIRETO (API)
# =========================

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
        servico=request.servico,
        cliente=request.cliente.model_dump()
    )

    salvar_agendamento(
        nome_cliente=request.cliente.nome,
        telefone=request.cliente.telefone,
        servico=request.servico,
        data_hora=data_hora,
        endereco=request.cliente.endereco.model_dump(),
        calendar_event_id=evento.get("id")
    )

    return {
        "status": "confirmado",
        "evento_id": evento.get("id"),
        "link": evento.get("htmlLink"),
    }
