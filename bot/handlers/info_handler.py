from ..states import ConversationState
from ..context import UserContext
from .base import BaseHandler
from core.constants import SAUDACOES, PALAVRAS_RECOMECAR

class InfoHandler(BaseHandler):
    def should_handle(self, context: UserContext, message: str) -> bool:
        msg_lower = message.lower().strip()
        
        # Check for global reset commands
        if any(cmd in msg_lower for cmd in PALAVRAS_RECOMECAR):
            return True

        # NOVA LÓGICA: Se for saudação, também reseta!
        if any(saudacao in msg_lower for saudacao in SAUDACOES):
            return True
        
        # CORREÇÃO: Se já é um comando de serviço válido no START, transiciona e deixa BookingHandler tratar
        comandos_servico = ["1", "2", "3", "limpeza", "manutencao", "manutenção", "instalacao", "instalação"]
        if context.state == ConversationState.START:
            # Verifica se o input é um comando de serviço
            if msg_lower in comandos_servico or any(cmd in msg_lower for cmd in ["limpeza", "manuten", "instala"]):
                context.update_state(ConversationState.SELECT_SERVICE)
                return False  # Passa para o BookingHandler
            return True  # Input genérico, mostra menu
        
        # Check for finished state (restarting)
        if context.state == ConversationState.FINISHED:
             return True
             
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
            "3️⃣ Instalação\n"
            "4️⃣ Meus Agendamentos / Cancelar"
        )
