from datetime import datetime
from zoneinfo import ZoneInfo
import re

SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")
CEP_REGEX = re.compile(r"^\d{5}-?\d{3}$")
from ..states import ConversationState
from ..context import UserContext
from .base import BaseHandler
from services.google_calendar_service import horario_disponivel, criar_evento, listar_horarios_livres
from services.agendamentos_service import salvar_agendamento
from core.logger import get_logger

logger = get_logger(__name__)

# Navegação simplificada: "menu" reinicia, não há mais "voltar" passo a passo

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
            ConversationState.PROVIDE_ZIP,
            ConversationState.CONFIRMATION
        ]

    def handle(self, context: UserContext, message: str) -> str:
        """Processa a mensagem do usuário de acordo com o estado atual."""
        state = context.state
        message_cleaned = message.strip()
        message_lower = message_cleaned.lower()

        # Navegação simplificada: não há mais "voltar", apenas "menu" para reiniciar
        if state == ConversationState.SELECT_SERVICE:
            return self._handle_service(context, message_lower)
        elif state == ConversationState.SELECT_DATE:
            return self._handle_date(context, message_cleaned)
        elif state == ConversationState.SELECT_TIME:
            return self._handle_time(context, message_cleaned)
        elif state == ConversationState.PROVIDE_NAME:
            return self._handle_name(context, message_cleaned)
        elif state == ConversationState.PROVIDE_STREET:
            return self._handle_generic_input(context, message_cleaned, "rua", ConversationState.PROVIDE_NUMBER, "Qual o número?")
        elif state == ConversationState.PROVIDE_NUMBER:
            return self._handle_generic_input(context, message_cleaned, "numero", ConversationState.PROVIDE_NEIGHBORHOOD, "Qual o bairro?")
        elif state == ConversationState.PROVIDE_NEIGHBORHOOD:
            return self._handle_generic_input(context, message_cleaned, "bairro", ConversationState.PROVIDE_CITY, "Qual a sua cidade?")
        elif state == ConversationState.PROVIDE_CITY:
            return self._handle_generic_input(context, message_cleaned, "cidade", ConversationState.PROVIDE_ZIP, "E para finalizar, qual o seu CEP?")
        elif state == ConversationState.PROVIDE_ZIP:
            return self._handle_zip_and_review(context, message_cleaned)
        elif state == ConversationState.CONFIRMATION:
            return self._handle_confirmation(context, message_lower)
        
        return "Desculpe, não entendi. Digite *menu* para recomeçar."

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

    def _formatar_opcao_menu(self, indice: int, texto: str) -> str:
        """
        Formata uma opção de menu com emoji ou numeração simples.
        
        Args:
            indice: Número da opção (começando de 1).
            texto: Texto a ser exibido (ex: '08:00').
        
        Returns:
            String formatada com emoji (1-10) ou numeração simples (11+).
        """
        emoji_keycaps = {
            1: "1️⃣", 2: "2️⃣", 3: "3️⃣", 4: "4️⃣", 5: "5️⃣",
            6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟"
        }
        
        if indice in emoji_keycaps:
            return f"{emoji_keycaps[indice]} {texto}"
        return f"{indice}. {texto}"

    def _handle_service(self, context: UserContext, message: str) -> str:
        if message == "1" or "limpeza" in message:
            servico = "limpeza"
        elif message == "2" or "manuten" in message:
            servico = "manutencao"
        elif message == "3" or "instala" in message:
            servico = "instalacao"
        else:
            # CORREÇÃO: Menu atualizado com emojis e Opção 4
            return (
                "Não entendi 😅\n"
                "Por favor, escolha uma opção válida:\n\n"
                "1️⃣ Limpeza\n"
                "2️⃣ Manutenção\n"
                "3️⃣ Instalação\n"
                "4️⃣ Meus Agendamentos / Cancelar"
            )

        context.data["servico"] = servico
        context.update_state(ConversationState.SELECT_DATE)
        return (
            f"Perfeito! Você escolheu {servico.capitalize()}. Qual data você prefere? (DD/MM/AAAA)\n\n"
            "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
        )

    def _handle_date(self, context: UserContext, message: str) -> str:
        data_limpa = message.replace(",", "/").replace(".", "/").replace("-", "/")
        try:
            data_obj = datetime.strptime(data_limpa, "%d/%m/%Y")
            data_iso = data_obj.strftime("%Y-%m-%d")
            
            # Validation: ensure date is not in the past
            if data_obj.date() < datetime.now(SAO_PAULO_TZ).date():
                return "📅 Essa data já passou. Por favor, escolha uma data futura."

            context.data["data"] = data_iso
            
            # Fetch available slots
            servico = context.data.get("servico")
            horarios = listar_horarios_livres(data_obj.date(), servico)
            
            if not horarios:
                return "📅 Não tenho horários livres para essa data. Por favor, escolha outra."
            
            # Save available slots in context for later use
            context.data["horarios_disponiveis"] = horarios
            
            # Build numbered menu
            data_formatada = data_obj.strftime("%d/%m/%Y")
            menu_linhas = [self._formatar_opcao_menu(i + 1, h) for i, h in enumerate(horarios)]
            menu = "\n".join(menu_linhas)
            
            context.update_state(ConversationState.SELECT_TIME)
            return (
                f"Encontrei estes horários para {data_formatada}:\n\n"
                f"{menu}\n\n"
                "Qual número você prefere?\n"
                "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
            )
        except ValueError:
            return "Data inválida 😕\nPor favor, use o formato Dia/Mês/Ano (ex: 15/01/2026)"

    def _handle_time(self, context: UserContext, message: str) -> str:
        hora_limpa = message.replace(" ", "")
        horarios_disponiveis = context.data.get("horarios_disponiveis", [])
        
        # If horarios_disponiveis is empty (e.g., session reloaded from DB), recalculate
        if not horarios_disponiveis:
            data_iso = context.data.get("data")
            servico = context.data.get("servico")
            if data_iso and servico:
                data_obj = datetime.strptime(data_iso, "%Y-%m-%d").date()
                horarios_disponiveis = listar_horarios_livres(data_obj, servico)
                context.data["horarios_disponiveis"] = horarios_disponiveis
        
        # Helper: remonta o menu de horários para reexibição
        def _remontar_menu() -> str:
            menu_linhas = [self._formatar_opcao_menu(i + 1, h) for i, h in enumerate(horarios_disponiveis)]
            return "\n".join(menu_linhas)
        
        DICA_REINICIAR = "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
        
        # Try to interpret as menu index first
        if hora_limpa.isdigit():
            indice = int(hora_limpa) - 1  # Convert to 0-indexed
            if 0 <= indice < len(horarios_disponiveis):
                hora_selecionada = horarios_disponiveis[indice]
            else:
                return (
                    f"❌ Opção inválida. Escolha um número de 1 a {len(horarios_disponiveis)}.\n\n"
                    f"{_remontar_menu()}\n\n"
                    f"{DICA_REINICIAR}"
                )
        else:
            # Fallback: try direct time format (HH:MM)
            try:
                datetime.strptime(hora_limpa, "%H:%M")
                hora_selecionada = hora_limpa
            except ValueError:
                return (
                    "Horário inválido 😕\n"
                    "Por favor, escolha um número do menu ou digite no formato HH:MM (ex: 14:00)\n\n"
                    f"{_remontar_menu()}\n\n"
                    f"{DICA_REINICIAR}"
                )

        # Race condition check: verify availability one more time
        try:
            data_iso = context.data.get("data")
            servico = context.data.get("servico")
            
            if data_iso and servico:
                data_hora = datetime.strptime(f"{data_iso} {hora_selecionada}", "%Y-%m-%d %H:%M")
                
                if not horario_disponivel(
                    data_hora_inicio=data_hora,
                    servico=servico
                ):
                    return "❌ Esse horário já está ocupado. Por favor, escolha outro."
        except Exception as e:
            logger.error(f"Error checking availability: {e}")

        context.data["hora"] = hora_selecionada
        context.update_state(ConversationState.PROVIDE_NAME)
        return (
            "Perfeito! Qual o seu nome completo?\n\n"
            "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
        )

    def _handle_name(self, context: UserContext, message: str) -> str:
        """Valida e salva o nome do cliente."""
        # Remove espaços extras e verifica se contém letras
        nome = message.strip()
        
        # Validação: nome não pode ser apenas números
        if nome.replace(" ", "").isdigit():
            return (
                "❌ Nome inválido. Por favor, digite seu nome completo (sem números).\n\n"
                "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
            )
        
        # Validação: nome deve ter pelo menos 2 caracteres
        if len(nome) < 2:
            return (
                "❌ Nome muito curto. Por favor, digite seu nome completo.\n\n"
                "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
            )
        
        context.data["nome"] = nome
        context.update_state(ConversationState.PROVIDE_STREET)
        return (
            "Perfeito! Agora, qual o nome da sua rua?\n\n"
            "_(💡 Caso queira mudar algo, escreva 'menu' para reiniciar a conversa)_"
        )

    def _handle_generic_input(self, context: UserContext, message: str, key: str, next_state: ConversationState, response_text: str) -> str:
        context.data[key] = message
        context.update_state(next_state)
        return response_text

    def _handle_zip_and_review(self, context: UserContext, message: str) -> str:
        """Saves the ZIP code and displays a summary for user confirmation."""
        # Validação de CEP: formato 00000-000 ou 00000000
        cep_normalizado = message.strip().replace(" ", "")
        if not CEP_REGEX.match(cep_normalizado):
            return (
                "❌ CEP inválido. Por favor, digite no formato *00000-000* ou *00000000*.\n"
                "_(💡 Dica: Digite 'voltar' para corrigir a cidade)_"
            )
        
        context.data["cep"] = message.strip()
        logger.info(f"CEP received for {context.phone}, preparing confirmation summary")
        
        # Build the full address string
        dados = context.data
        endereco_completo = (
            f"{dados.get('rua', 'N/A')}, {dados.get('numero', 'S/N')}, "
            f"{dados.get('bairro', 'N/A')} - {dados.get('cidade', 'N/A')}, "
            f"CEP: {message}"
        )
        
        # Format date for display
        data_iso = dados.get('data', '')
        try:
            data_formatada = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            data_formatada = data_iso
        
        # Build confirmation summary with emojis and markdown
        resumo = (
            "📋 *RESUMO DO AGENDAMENTO*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🛠 *Serviço:* {dados.get('servico', 'N/A').capitalize()}\n"
            f"📅 *Data:* {data_formatada}\n"
            f"⏰ *Horário:* {dados.get('hora', 'N/A')}\n"
            f"👤 *Nome:* {dados.get('nome', 'N/A')}\n"
            f"🏠 *Endereço:* {endereco_completo}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Os dados estão corretos? (Sim / Não)"
        )
        
        context.update_state(ConversationState.CONFIRMATION)
        return resumo

    def _handle_confirmation(self, context: UserContext, message: str) -> str:
        """Handles user confirmation before finalizing the booking."""
        # Normalize input for matching
        positive_responses = ["sim", "s", "ok", "confirmar", "confirmo", "correto", "yes", "y"]
        negative_responses = ["não", "nao", "n", "corrigir", "errado", "no"]
        
        if message in positive_responses:
            logger.info(f"Booking confirmed by user {context.phone}")
            return self._finalize_booking(context)
        elif message in negative_responses:
            logger.info(f"User {context.phone} rejected booking summary, offering correction options")
            return (
                "Sem problemas! 🔄\n\n"
                "Para corrigir algum campo, digite *voltar* quantas vezes precisar.\n"
                "Para cancelar e recomeçar, digite *menu*.\n\n"
                "_(💡 Dica: Cada 'voltar' retorna uma etapa)_"
            )
        else:
            return (
                "Não entendi 😅\n"
                "Por favor, responda apenas *Sim* para confirmar ou *Não* para corrigir."
            )

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
