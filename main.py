from fastapi import FastAPI, Query, HTTPException
from datetime import datetime
from typing import Dict, Any

from services.google_calendar_service import horario_disponivel, criar_evento, GOOGLE_CALENDAR_ID
from services.agendamentos_service import salvar_agendamento
from services.whatsapp_service import processar_mensagem_whatsapp
from models import AgendamentoRequest, MensagemWhatsApp


# =========================
# APP
# =========================

app = FastAPI(
    title="Bot de Ar-Condicionado",
    description="API para agendamento de serviços via WhatsApp",
    version="1.0.0"
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
    simulacao: bool = Query(False, description="Se true, retorna dados de teste")
) -> Dict[str, Any]:
    """
    Recebe uma mensagem do WhatsApp e retorna a resposta do bot.
    
    Args:
        dados: Objeto com telefone e mensagem do cliente
        simulacao: Se True, retorna formato de teste
    
    Returns:
        Dicionário com a resposta do bot
    
    Raises:
        HTTPException: Se houver erro no processamento
    
    Example:
        POST /whatsapp
        {
            "telefone": "11987654321",
            "mensagem": "Olá"
        }
    """
    try:
        resposta = processar_mensagem_whatsapp(
            telefone=dados.telefone,
            mensagem=dados.mensagem
        )
    except ValueError as e:
        # ValueError = dados inválidos (ex: formato de telefone errado)
        raise HTTPException(
            status_code=400,
            detail={"erro": "Dados inválidos", "detalhes": str(e)}
        )
    except KeyError as e:
        # KeyError = campo obrigatório faltando
        raise HTTPException(
            status_code=400,
            detail={"erro": "Campo obrigatório faltando", "campo": str(e)}
        )
    except Exception as e:
        # Erro inesperado - logar para debug
        print(f"Erro inesperado no WhatsApp: {e}")
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
    
    Verifica disponibilidade, cria evento no Google Calendar
    e salva no banco de dados.
    
    Args:
        request: Dados do agendamento (serviço, data, hora, cliente)
    
    Returns:
        Dicionário com status do agendamento e link do evento
    
    Raises:
        HTTPException: Se houver erro na validação ou criação
    
    Example:
        POST /agendar
        {
            "servico": "limpeza",
            "data": "2026-01-15",
            "hora": "14:30",
            "cliente": {
                "nome": "João Silva",
                "telefone": "11987654321",
                "endereco": {
                    "rua": "Rua das Flores",
                    "numero": "123",
                    "bairro": "Centro",
                    "cidade": "São Paulo",
                    "cep": "01234-567"
                }
            }
        }
    """
    # Tenta converter a data e hora para datetime
    try:
        data_hora = datetime.strptime(
            f"{request.data} {request.hora}",
            "%Y-%m-%d %H:%M"
        )
    except ValueError as e:
        # ValueError = formato de data/hora inválido
        raise HTTPException(
            status_code=400,
            detail={
                "erro": "Data ou hora em formato inválido",
                "formato_esperado": "data: YYYY-MM-DD, hora: HH:MM",
                "detalhes": str(e)
            }
        )

    # Verifica se o horário está disponível no Google Calendar
    disponivel = horario_disponivel(
        calendar_id=GOOGLE_CALENDAR_ID,
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
            calendar_id=GOOGLE_CALENDAR_ID,
            data_hora_inicio=data_hora,
            servico=request.servico,
            cliente=request.cliente.model_dump()
        )
    except Exception as e:
        # Erro ao criar evento no Calendar
        print(f"Erro ao criar evento no Calendar: {e}")
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
        # Erro ao salvar no banco
        print(f"Erro ao salvar agendamento: {e}")
        raise HTTPException(
            status_code=500,
            detail={"erro": "Erro ao salvar agendamento no banco de dados"}
        )

    return {
        "status": "confirmado",
        "evento_id": evento.get("id"),
        "link": evento.get("htmlLink"),
    }

