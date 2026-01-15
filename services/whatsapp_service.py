"""
Serviço de processamento de mensagens do WhatsApp.

Atua como adaptador para o BotManager e implementa o envio
de respostas via Evolution API.
"""

import requests
from bot.manager import BotManager
from core.config import get_settings
from core.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Singleton do BotManager
_manager = BotManager()

# Nome da instância configurada na Evolution API
INSTANCE_NAME = "bot-principal"


def enviar_resposta_evolution(telefone: str, mensagem: str) -> bool:
    """
    Envia a resposta de volta para o usuário via Evolution API.
    
    Args:
        telefone: Número do destinatário (formato: 5511999999999)
        mensagem: Texto da resposta do bot
    
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
        logger.warning("⚠️ Evolution API não configurada. Resposta não enviada.")
        return False

    # Monta a URL de envio de texto
    base_url = str(settings.EVOLUTION_API_URL).rstrip("/")
    url = f"{base_url}/message/sendText/{INSTANCE_NAME}"
    
    headers = {
        "apikey": settings.EVOLUTION_API_KEY.get_secret_value(),
        "Content-Type": "application/json"
    }
    
    payload = {
        "number": telefone,
        "options": {
            "delay": 1200,        # Simula "digitando..." (1.2s)
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": mensagem
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 201:
            logger.info(f"✅ Resposta enviada para {telefone}")
            return True
        else:
            logger.error(f"❌ Falha ao enviar msg: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"❌ Timeout ao enviar resposta para {telefone}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro de conexão com Evolution API: {e}")
        return False


def processar_mensagem_whatsapp(telefone: str, mensagem: str) -> str:
    """
    Processa a mensagem do usuário e envia a resposta via Evolution API.
    
    Args:
        telefone: Número de telefone do cliente
        mensagem: Mensagem enviada pelo cliente
    
    Returns:
        Resposta do bot (texto)
    """
    # 1. Gera a resposta lógica (Cérebro do Bot)
    resposta_texto = _manager.process_message(telefone, mensagem)
    
    # 2. Envia a resposta para o WhatsApp do usuário (Ação Real)
    enviar_resposta_evolution(telefone, resposta_texto)
    
    return resposta_texto

