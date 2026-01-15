from fastapi import FastAPI, Query, HTTPException, Header, Request, Depends
from datetime import datetime
from typing import Dict, Any, Optional

from services.google_calendar_service import horario_disponivel, criar_evento
from services.agendamentos_service import salvar_agendamento
from services.whatsapp_service import processar_mensagem_whatsapp
from models import AgendamentoRequest
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


# =========================
# DEPENDÊNCIAS DE SEGURANÇA
# =========================

async def verificar_api_key(
    apikey_header: Optional[str] = Header(None, alias="apikey"),
    apikey_query: Optional[str] = Query(None, alias="apikey")
):
    """
    Valida a chave de segurança do Webhook.
    Aceita via Header (padrão) OU via URL (query param 'apikey').
    Isso resolve o problema da Evolution não enviar o header corretamente.
    """
    if settings.EVOLUTION_API_KEY:
        expected_key = settings.EVOLUTION_API_KEY.get_secret_value()
        
        # Verifica se veio pelo Header OU pela URL
        received_key = apikey_header or apikey_query
        
        if not received_key or received_key != expected_key:
            logger.warning("⛔ Acesso negado: API Key inválida ou ausente no Webhook")
            raise HTTPException(status_code=403, detail="Acesso negado")


@app.get("/")
def home() -> Dict[str, str]:
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Dicionário com mensagem de status
    """
    return {"mensagem": "API do bot de ar-condicionado funcionando"}


# =========================
# WHATSAPP (HÍBRIDO: Teste + Evolution)
# =========================

@app.post("/whatsapp", dependencies=[Depends(verificar_api_key)])
async def receber_mensagem(
    request: Request,
    simulacao: bool = Query(False, description="Se true, retorna dados de teste")
) -> Dict[str, Any]:
    """
    Endpoint Híbrido para receber mensagens do WhatsApp.
    
    1. Aceita JSON simples (Testes Manuais): {"telefone": "...", "mensagem": "..."}
    2. Aceita Webhook Complexo (Evolution API): {"data": {"key": {...}, "message": {...}}}
    """
    try:
        body = await request.json()
        
        # === MODO 1: Teste Manual (JSON Simples) ===
        if "telefone" in body and "mensagem" in body:
            telefone = body["telefone"]
            mensagem = body["mensagem"]
            logger.info(f"📩 Teste Manual recebido de {telefone}: {mensagem}")
            
            resposta = processar_mensagem_whatsapp(telefone, mensagem)
            
            if simulacao:
                return {
                    "simulacao": True,
                    "telefone": telefone,
                    "mensagem_enviada": mensagem,
                    "resposta_bot": resposta
                }
            return {"status": "processado", "resposta": resposta}

        # === MODO 2: Webhook Evolution API (Parser) ===
        data = body.get("data", {})
        key = data.get("key", {})
        
        # Ignora mensagens enviadas pelo próprio bot (Loop Infinito Prevention)
        if key.get("fromMe", False):
            logger.debug("🔄 Ignorando mensagem fromMe (próprio bot)")
            return {"status": "ignored", "reason": "from_me"}
            
        # Extrai telefone (remove sufixo @s.whatsapp.net)
        remote_jid = key.get("remoteJid", "")
        telefone = remote_jid.split("@")[0]
        
        # Extrai mensagem de texto (Conversation ou ExtendedTextMessage)
        message_content = data.get("message", {})
        mensagem = message_content.get("conversation")
        
        if not mensagem:
            extended = message_content.get("extendedTextMessage", {})
            mensagem = extended.get("text")
            
        if not telefone or not mensagem:
            logger.debug(f"📭 Webhook sem texto extraível: {body.get('event', 'unknown')}")
            return {"status": "ignored", "reason": "no_text_found"}
            
        logger.info(f"📩 Webhook Evolution recebido de {telefone}: {mensagem}")
        
        # Processa e dispara o envio da resposta
        processar_mensagem_whatsapp(telefone, mensagem)
        
        return {"status": "processado"}

    except Exception as e:
        logger.error(f"🔥 Erro crítico no webhook: {e}")
        # Retornamos 200 para evitar que a Evolution fique reenviando a msg com erro
        return {"status": "error", "detail": str(e)}


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

