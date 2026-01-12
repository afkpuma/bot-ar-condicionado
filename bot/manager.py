from datetime import datetime, timedelta, timezone
from typing import Optional
from services.supabase_client import supabase
from core.logger import get_logger
from core.constants import TIMEOUT_SESSAO
from .states import ConversationState
from .context import UserContext
from .handlers.base import BaseHandler
from .handlers.info_handler import InfoHandler
from .handlers.cancellation_handler import CancellationHandler
from .handlers.booking_handler import BookingHandler

logger = get_logger(__name__)

class BotManager:
    def __init__(self):
        self.handlers: list[BaseHandler] = []
        # Register handlers in priority order:
        # 1. CancellationHandler: handles "cancelar" command (Highest Priority)
        # 2. InfoHandler: handles "menu" and START/FINISHED state
        # 3. BookingHandler: handles the booking flow
        self.register_handler(CancellationHandler())
        self.register_handler(InfoHandler())
        self.register_handler(BookingHandler())

    def register_handler(self, handler: BaseHandler):
        self.handlers.append(handler)

    def get_or_create_context(self, phone: str) -> UserContext:
        """Fetches conversation context from Supabase or creates a new one."""
        try:
            response = supabase.table("conversas_whatsapp") \
                .select("*") \
                .eq("telefone", phone) \
                .limit(1) \
                .execute()
            
            data = response.data[0] if response.data else None
            
            if data:
                updated_at_str = data.get("updated_at") or data.get("created_at")
                # Handle simplified ISO format mostly found in logs/DB
                if updated_at_str:
                     updated_at_str = updated_at_str.replace("Z", "+00:00")
                else:
                    # Fallback if no timestamp is found, use current time in UTC
                    updated_at_str = datetime.now(timezone.utc).isoformat()
                
                updated_at = datetime.fromisoformat(updated_at_str)
                
                # Ensure updated_at is aware if possible, or fallback
                if updated_at.tzinfo is None:
                    updated_at = updated_at.replace(tzinfo=timezone.utc)

                # Check for timeout
                if (datetime.now(timezone.utc) - updated_at).total_seconds() / 60 > TIMEOUT_SESSAO:
                     logger.info(f"Session timeout for {phone}")
                     return UserContext(phone=phone, state=ConversationState.START, data={}, updated_at=datetime.now(timezone.utc))

                return UserContext(
                    phone=phone,
                    state=ConversationState(data.get("etapa", ConversationState.START)),
                    data={k: v for k, v in data.items() if k not in ["telefone", "etapa", "created_at", "updated_at"]},
                    updated_at=updated_at
                )
            else:
                return UserContext(
                    phone=phone,
                    state=ConversationState.START
                )
                
        except Exception as e:
            logger.error(f"Error fetching context for {phone}: {e}")
            return UserContext(phone=phone, state=ConversationState.START)

    def save_context(self, context: UserContext):
        """Saves conversation state to Supabase."""
        try:
            payload = {
                "telefone": context.phone,
                "etapa": context.state.value,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            # Merge context data into payload (flattened for DB)
            # Note: This assumes DB columns match context.data keys. 
            # Transient keys that shouldn't be persisted:
            TRANSIENT_KEYS = {"horarios_disponiveis"}
            filtered_data = {k: v for k, v in context.data.items() if k not in TRANSIENT_KEYS}
            payload.update(filtered_data)

            supabase.table("conversas_whatsapp").upsert(
                payload, on_conflict="telefone"
            ).execute()
        except Exception as e:
            logger.error(f"Error saving context for {context.phone}: {e}")

    def process_message(self, phone: str, message: str) -> str:
        context = self.get_or_create_context(phone)
        
        # Normalize message
        message = message.strip()
        
        # Find handler
        for handler in self.handlers:
            if handler.should_handle(context, message):
                try:
                    response = handler.handle(context, message)
                    self.save_context(context)
                    return response
                except Exception as e:
                    logger.error(f"Error in handler {handler.__class__.__name__}: {e}")
                    return "Desculpe, ocorreu um erro interno. Tente novamente mais tarde."
        
        # Default fallback if no handler matches (shouldn't happen if we have a default handler)
        return "Olá! Não entendi. Digite 'menu' para começar."
