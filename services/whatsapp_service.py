"""
Serviço de processamento de mensagens do WhatsApp.

Atua como um adaptador para o BotManager, mantendo a compatibilidade
com a interface existente esperada pelo main.py.
"""

from bot.manager import BotManager

# Singleton instance to persist handlers state (if needed in future)
_manager = BotManager()

def processar_mensagem_whatsapp(telefone: str, mensagem: str) -> str:
    """
    Processa a mensagem enviada pelo usuário via WhatsApp
    delegando para o BotManager.
    
    Args:
        telefone: Número de telefone do cliente
        mensagem: Mensagem enviada pelo cliente
    
    Returns:
        Resposta do bot para o cliente
    """
    return _manager.process_message(telefone, mensagem)
