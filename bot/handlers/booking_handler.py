from datetime import datetime
from ..states import ConversationState
from ..context import UserContext
from .base import BaseHandler
from services.google_calendar_service import horario_disponivel, criar_evento
from services.agendamentos_service import salvar_agendamento
from core.logger import get_logger

logger = get_logger(__name__)

PREVIOUS_STATE = {
    ConversationState.SELECT_DATE: ConversationState.SELECT_SERVICE,
    ConversationState.SELECT_TIME: ConversationState.SELECT_DATE,
    ConversationState.PROVIDE_NAME: ConversationState.SELECT_TIME,
    ConversationState.PROVIDE_STREET: ConversationState.PROVIDE_NAME,
    ConversationState.PROVIDE_NUMBER: ConversationState.PROVIDE_STREET,
    ConversationState.PROVIDE_NEIGHBORHOOD: ConversationState.PROVIDE_NUMBER,
    ConversationState.PROVIDE_CITY: ConversationState.PROVIDE_NEIGHBORHOOD,
    ConversationState.PROVIDE_ZIP: ConversationState.PROVIDE_CITY,
}

REPROMPT_MAP = {
    ConversationState.SELECT_SERVICE: "Qual serviço você deseja? 1. Limpeza, 2. Manutenção, 3. Instalação",
    ConversationState.SELECT_DATE: "Qual data você prefere? (DD/MM/AAAA)\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.SELECT_TIME: "Qual horário? (HH:MM)\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_NAME: "Qual o seu nome completo?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_STREET: "Qual o nome da sua rua?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_NUMBER: "Qual o número?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_NEIGHBORHOOD: "Qual o bairro?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_CITY: "Qual a sua cidade?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
    ConversationState.PROVIDE_ZIP: "E para finalizar, qual o seu CEP?\n\n_(💡 Dica: Digite 'voltar' para corrigir a etapa anterior)_",
}

class BookingHandler(BaseHandler):
    def should_handle(self, context: UserContext, message: str) -> bool:
        return context.state in [
            ConversationState.SELECT_SERVICE,
            ConversationState.SELECT_DATE,
            ConversationState.SELECT_TIME,
            ConversationState.PROVIDE_NAME,
            ConversationState.PROVIDE_STREET,
            ConversationState.PROVIDE_NUMBER,
            ConversationState.PROVIDE_NEIGHBORHOOD,
            ConversationState.PROVIDE_CITY,
            ConversationState.PROVIDE_ZIP
        ]

    def handle(self, context: UserContext, message: str) -> str:
        state = context.state
        message_cleaned = message.strip()
        message_lower = message_cleaned.lower()

        if message_lower in ["voltar", "corrigir", "anterior", "back"]:
            return self._handle_back(context)

        if state == ConversationState.SELECT_SERVICE:
            return self._handle_service(context, message_lower)
        elif state == ConversationState.SELECT_DATE:
            return self._handle_date(context, message_cleaned)
        elif state == ConversationState.SELECT_TIME:
            return self._handle_time(context, message_cleaned)
        elif state == ConversationState.PROVIDE_NAME:
            return self._handle_generic_input(context, message_cleaned, "nome", ConversationState.PROVIDE_STREET, "Perfeito! Agora, qual o nome da sua rua?")
        elif state == ConversationState.PROVIDE_STREET:
            return self._handle_generic_input(context, message_cleaned, "rua", ConversationState.PROVIDE_NUMBER, "Qual o número?")
        elif state == ConversationState.PROVIDE_NUMBER:
            return self._handle_generic_input(context, message_cleaned, "numero", ConversationState.PROVIDE_NEIGHBORHOOD, "Qual o bairro?")
        elif state == ConversationState.PROVIDE_NEIGHBORHOOD:
            return self._handle_generic_input(context, message_cleaned, "bairro", ConversationState.PROVIDE_CITY, "Qual a sua cidade?")
        elif state == ConversationState.PROVIDE_CITY:
            return self._handle_generic_input(context, message_cleaned, "cidade", ConversationState.PROVIDE_ZIP, "E para finalizar, qual o seu CEP?")
        elif state == ConversationState.PROVIDE_ZIP:
            return self._handle_zip_and_finish(context, message_cleaned)
        
        return "Desculpe, não entendi. Tente novamente."

    def _handle_back(self, context: UserContext) -> str:
        current_state = context.state
        previous = PREVIOUS_STATE.get(current_state)

        if not previous:
            return "Não é possível voltar a partir daqui. Digite 'menu' para reiniciar."
        
        # Using context.update_state as requested to ensure updated_at is refreshed
        context.update_state(previous)
        
        # Clean current state data? Maybe not strictly necessary if overwriting, but good for cleanliness.
        # However, keeping it might be a feature (preserving filled info). Let's keep it simple.
        
        return f"🔙 Voltando...\n{REPROMPT_MAP.get(previous, 'O que você deseja?')}"

    def _handle_service(self, context: UserContext, message: str) -> str:
        if message == "1" or "limpeza" in message:
            servico = "limpeza"
        elif message == "2" or "manuten" in message:
            servico = "manutencao"
        elif message == "3" or "instala" in message:
            servico = "instalacao"
        else:
            return (
                "Não entendi 😅\n"
                "Por favor, escolha uma opção:\n"
                "1. Limpeza\n"
                "2. Manutenção\n"
                "3. Instalação"
            )

        context.data["servico"] = servico
        context.update_state(ConversationState.SELECT_DATE)
        return f"Perfeito! Você escolheu {servico.capitalize()}. Qual data você prefere? (DD/MM/AAAA)"

    def _handle_date(self, context: UserContext, message: str) -> str:
        data_limpa = message.replace(",", "/").replace(".", "/").replace("-", "/")
        try:
            data_obj = datetime.strptime(data_limpa, "%d/%m/%Y")
            data_iso = data_obj.strftime("%Y-%m-%d")
            
            # Basic validation: ensure date is not in the past
            # if data_obj.date() < datetime.now().date():
            #     return "A data deve ser futura. Por favor, escolha outra data."

            context.data["data"] = data_iso
            context.update_state(ConversationState.SELECT_TIME)
            return "Ótimo! Agora informe o horário (HH:MM)"
        except ValueError:
            return "Data inválida 😕\nPor favor, use o formato Dia/Mês/Ano (ex: 15/01/2026)"

    def _handle_time(self, context: UserContext, message: str) -> str:
        hora_limpa = message.replace(" ", "")
        try:
            datetime.strptime(hora_limpa, "%H:%M")
        except ValueError:
            return "Horário inválido 😕\nPor favor, use o formato Hora:Minuto (ex: 14:30)"

        # Check availability
        try:
            data_iso = context.data.get("data")
            servico = context.data.get("servico")
            
            if data_iso and servico:
                data_hora = datetime.strptime(f"{data_iso} {hora_limpa}", "%Y-%m-%d %H:%M")
                
                if not horario_disponivel(
                    data_hora_inicio=data_hora,
                    servico=servico
                ):
                    return "❌ Esse horário já está ocupado. Por favor, escolha outro."
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            # Fail open or closed? Let's warn but proceed or ask again? 
            # Current logic: allow user to retry if error, but if API fails maybe let them pass?
            # Safe approach: let them pass but log it. Implementation choice: fail if we are sure it's occupied.

        context.data["hora"] = hora_limpa
        context.update_state(ConversationState.PROVIDE_NAME)
        return "Perfeito! Qual o seu nome completo?"

    def _handle_generic_input(self, context: UserContext, message: str, key: str, next_state: ConversationState, response_text: str) -> str:
        context.data[key] = message
        context.update_state(next_state)
        return response_text

    def _handle_zip_and_finish(self, context: UserContext, message: str) -> str:
        context.data["cep"] = message
        # We don't update state to FINISHED yet because we might fail to save.
        # But logically we are done.
        
        return self._finalize_booking(context)

    def _finalize_booking(self, context: UserContext) -> str:
        try:
            dados = context.data
            telefone = context.phone
            
            # Reconstruct datetime
            data_hora = datetime.strptime(
                f"{dados['data']} {dados['hora']}",
                "%Y-%m-%d %H:%M"
            )
            
            cliente = {
                "nome": dados.get("nome", "Cliente WhatsApp"),
                "telefone": telefone,
                "endereco": {
                    "rua": dados.get("rua", "Não informado"),
                    "numero": dados.get("numero", "S/N"),
                    "bairro": dados.get("bairro", "Não informado"),
                    "cidade": dados.get("cidade", "Não informado"),
                    "cep": dados.get("cep", "00000-000")
                }
            }

            # Final availability check
            if not horario_disponivel(
                data_hora_inicio=data_hora,
                servico=dados.get("servico")
            ):
                 # Rollback state to Time selection
                context.update_state(ConversationState.SELECT_TIME)
                return "❌ Desculpe, enquanto preenchíamos os dados, esse horário foi ocupado. Por favor, escolha outro horário."

            # Create event
            evento = criar_evento(
                data_hora_inicio=data_hora,
                servico=dados.get("servico"),
                cliente=cliente
            )

            # Save to DB (agendamentos table, separate from conversation state)
            salvar_agendamento(
                nome_cliente=cliente["nome"],
                telefone=telefone,
                servico=dados.get("servico"),
                data_hora=data_hora,
                endereco=cliente["endereco"],
                calendar_event_id=evento.get("id")
            )
            
            context.update_state(ConversationState.FINISHED)
            
            # Clear data for next time? Or keep history?
            # Ideally we mark this conversation as 'closed'. 
            # For now just confirming.
            
            return (
                "✅ Agendamento confirmado!\n\n"
                f"🛠 Serviço: {dados.get('servico', '').capitalize()}\n"
                f"📅 Data: {dados.get('data')}\n"
                f"⏰ Horário: {dados.get('hora')}\n"
                f"👤 Cliente: {cliente['nome']}\n"
                f"🏠 Endereço: {cliente['endereco']['rua']}, {cliente['endereco']['numero']}, "
                f"{cliente['endereco']['bairro']}, {cliente['endereco']['cidade']}, {cliente['endereco']['cep']}"
            )

        except Exception as e:
            logger.error(f"Error finalizing booking: {e}")
            return "Ocorreu um erro ao finalizar seu agendamento. Por favor, tente novamente ou contate o suporte."
