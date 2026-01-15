from fastapi import FastAPI, Query, HTTPException, Header
from datetime import datetime
from typing import Dict, Any, Optional

from services.google_calendar_service import horario_disponivel, criar_evento
from services.agendamentos_service import salvar_agendamento
from services.whatsapp_service import processar_mensagem_whatsapp
from models import AgendamentoRequest, MensagemWhatsApp
from core.config import get_settings
from core.logger import get_logger

# Logger
logger = get_logger(__name__)
settings = get_settings()

# =========================
# APP
# =========================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para agendamento de serviços via WhatsApp",
    version=settings.VERSION
)


@app.get("/")
def home() -> Dict[str, str]:
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Dicionário com mensagem de status
    """
    return {"mensagem": "API do bot de ar-condicionado funcionando"}


# =========================
# WHATSAPP (REAL + SIMULAÇÃO)
# =========================

@app.post("/whatsapp")
def receber_mensagem(
    dados: MensagemWhatsApp,
    simulacao: bool = Query(False, description="Se true, retorna dados de teste"),
    apikey: Optional[str] = Header(None, description="Chave de API para autenticação")
) -> Dict[str, Any]:
    """
    Recebe uma mensagem do WhatsApp e retorna a resposta do bot.
    
    A autenticação via apikey é obrigatória quando EVOLUTION_API_KEY está configurada.
    """
    # =========================
    # VALIDAÇÃO DE SEGURANÇA
    # =========================
    expected_key = settings.EVOLUTION_API_KEY
    if expected_key:  # Se a chave está configurada, valida obrigatoriamente
        if not apikey or apikey != expected_key.get_secret_value():
            logger.warning(f"Acesso não autorizado ao webhook de: {dados.telefone}")
            raise HTTPException(
                status_code=403,
                detail={"erro": "Acesso negado. Chave de API inválida."}
            )
    
    try:
        # O BotManager agora cuida de tudo internamente (Contexto, Erros, Logs)
        resposta = processar_mensagem_whatsapp(
            telefone=dados.telefone,
            mensagem=dados.mensagem
        )
    except Exception as e:
        logger.error(f"Erro crítico no endpoint /whatsapp: {e}")
        raise HTTPException(
            status_code=500,
            detail={"erro": "Erro interno do servidor"}
        )

    # Retorna formato de simulação para testes
    if simulacao:
        return {
            "simulacao": True,
            "telefone": dados.telefone,
            "mensagem_enviada": dados.mensagem,
            "resposta_bot": resposta
        }

    # Retorna formato normal
    return {
        "telefone": dados.telefone,
        "resposta": resposta
    }


# =========================
# AGENDAMENTO DIRETO (API)
# =========================

@app.post("/agendar")
def agendar(request: AgendamentoRequest) -> Dict[str, Any]:
    """
    Cria um agendamento diretamente via API.
    
    A validação de data/hora é feita automaticamente pelo Pydantic.
    Se data ou hora forem inválidos, FastAPI retorna 422 automaticamente.
    """
    # data_hora já vem validado pelo model_validator do Pydantic
    data_hora = request.data_hora

    # Verifica se o horário está disponível no Google Calendar
    # Obs: calendar_id é pego automaticamente do settings pelo serviço
    disponivel = horario_disponivel(
        data_hora_inicio=data_hora,
        servico=request.servico
    )

    if not disponivel:
        raise HTTPException(
            status_code=409,  # 409 = Conflict
            detail={
                "status": "indisponivel",
                "mensagem": "Esse horário já está ocupado. Escolha outro."
            }
        )

    # Cria o evento no Google Calendar
    try:
        evento = criar_evento(
            data_hora_inicio=data_hora,
            servico=request.servico,
            cliente=request.cliente.model_dump()
        )
    except Exception as e:
        logger.error(f"Erro ao criar evento no Calendar via API: {e}")
        raise HTTPException(
            status_code=500,
            detail={"erro": "Erro ao criar evento no calendário"}
        )

    # Salva o agendamento no banco de dados Supabase
    try:
        salvar_agendamento(
            nome_cliente=request.cliente.nome,
            telefone=request.cliente.telefone,
            servico=request.servico,
            data_hora=data_hora,
            endereco=request.cliente.endereco.model_dump(),
            calendar_event_id=evento.get("id")
        )
    except Exception as e:
        logger.error(f"Erro ao salvar agendamento via API: {e}")
        raise HTTPException(
            status_code=500,
            detail={"erro": "Erro ao salvar agendamento no banco de dados"}
        )

    return {
        "status": "confirmado",
        "evento_id": evento.get("id"),
        "link": evento.get("htmlLink"),
    }

