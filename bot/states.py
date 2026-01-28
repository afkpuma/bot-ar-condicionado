from enum import StrEnum

class ConversationState(StrEnum):
    """
    Estados da conversa do bot na arquitetura V2 Hybrid.
    
    O fluxo de booking completo (data, hora, endereço) foi migrado
    para o Frontend Streamlit. O bot agora gerencia apenas:
    - Seleção inicial de serviço
    - Redirecionamento para o formulário web
    - Fluxo de cancelamento via WhatsApp
    """
    # Initial
    START = "START"
    
    # Service Selection (redireciona para Frontend)
    SELECT_SERVICE = "SELECT_SERVICE"
    
    # Aguardando preenchimento do formulário web
    WAITING_FORM = "WAITING_FORM"
    
    # Cancellation Flow (mantido no WhatsApp)
    SELECT_CANCEL_ID = "SELECT_CANCEL_ID"
    
    # Final
    FINISHED = "FINISHED"
