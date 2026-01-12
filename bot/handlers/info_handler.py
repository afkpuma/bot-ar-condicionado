from ..states import ConversationState
from ..context import UserContext
from .base import BaseHandler
from core.constants import SAUDACOES, PALAVRAS_RECOMECAR

class InfoHandler(BaseHandler):
    def should_handle(self, context: UserContext, message: str) -> bool:
        msg_lower = message.lower()
        
        # Check for global reset commands
        if any(cmd in msg_lower for cmd in PALAVRAS_RECOMECAR):
            return True
            
        # Check for start state
        if context.state == ConversationState.START:
            return True
        
        # Check for finished state (restarting)
        if context.state == ConversationState.FINISHED:
             return True
             
        # Fallback if unhandled?
        return False

    def handle(self, context: UserContext, message: str) -> str:
        # If user said something unrelated but we are in START/FINISHED, or if they said 'menu' -> reset.
        
        # Reset state to SELECT_SERVICE to start booking flow
        context.update_state(ConversationState.SELECT_SERVICE)
        
        return (
            "Olá! 👋\n"
            "Qual serviço você deseja? Digite o número ou o nome:\n\n"
            "1️⃣ Limpeza\n"
            "2️⃣ Manutenção\n"
            "3️⃣ Instalação"
        )
