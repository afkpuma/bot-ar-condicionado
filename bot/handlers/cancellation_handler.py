"""
Handler para fluxo de cancelamento de agendamentos.

Permite que usuários visualizem e cancelem seus agendamentos futuros,
removendo-os do Google Calendar e atualizando o status no banco.
"""

from datetime import datetime
from typing import List, Dict, Any
from ..states import ConversationState
from ..context import UserContext
from .base import BaseHandler
from services.google_calendar_service import cancelar_evento
from services.agendamentos_service import (
    buscar_agendamentos_futuros,
    marcar_agendamento_como_cancelado
)
from core.logger import get_logger

logger = get_logger(__name__)


class CancellationHandler(BaseHandler):
    """Handler dedicado para o fluxo de cancelamento de agendamentos."""
    
    def should_handle(self, context: UserContext, message: str) -> bool:
        """
        Retorna True se:
        - O usuário digitou 'cancelar' (qualquer estado)
        - O estado atual é SELECT_CANCEL_ID (selecionando qual cancelar)
        - O usuário digitou '4' no menu principal (START/FINISHED)
        """
        message_lower = message.lower().strip()
        
        # Comando "cancelar" intercepta qualquer fluxo
        if "cancelar" in message_lower:
            return True
        
        # Ou se já está no fluxo de cancelamento
        if context.state == ConversationState.SELECT_CANCEL_ID:
            return True

        # Ou se escolheu a opção 4 no menu principal (START, FINISHED ou SELECT_SERVICE)
        if message_lower == "4" and context.state in [
            ConversationState.START, 
            ConversationState.FINISHED,
            ConversationState.SELECT_SERVICE  # Permite "4" também no menu de serviços
        ]:
            return True
            
        return False
    
    def handle(self, context: UserContext, message: str) -> str:
        """Processa a mensagem e retorna a resposta apropriada."""
        message_lower = message.lower().strip()
        
        # Se o usuário digitou "cancelar" OU escolheu a opção 4
        if "cancelar" in message_lower or message_lower == "4":
            return self._iniciar_cancelamento(context)
        
        # Se já está selecionando o ID para cancelar
        if context.state == ConversationState.SELECT_CANCEL_ID:
            return self._processar_selecao(context, message_lower)
        
        return "Não entendi. Digite 'menu' para ver as opções."
    
    def _iniciar_cancelamento(self, context: UserContext) -> str:
        """
        Busca agendamentos futuros e exibe lista numerada.
        """
        telefone = context.phone
        logger.info(f"Iniciando fluxo de cancelamento para {telefone}")
        
        agendamentos = buscar_agendamentos_futuros(telefone)
        
        if not agendamentos:
            logger.info(f"Nenhum agendamento futuro encontrado para {telefone}")
            # Reset para o início se o usuário estava em outro fluxo
            context.update_state(ConversationState.START)
            return (
                "📭 Você não possui agendamentos futuros.\n\n"
                "Digite *menu* para ver as opções disponíveis."
            )
        
        # Decisão Arquitetural: Não salvamos a lista complexa no context.data
        # para evitar erros de serialização no Supabase.
        context.update_state(ConversationState.SELECT_CANCEL_ID)
        
        # Monta a lista numerada
        menu_linhas = self._formatar_lista_agendamentos(agendamentos)
        
        logger.info(f"Exibindo {len(agendamentos)} agendamento(s) para cancelamento")
        
        return (
            "📋 *Seus Agendamentos Futuros:*\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{menu_linhas}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "Digite o *número* do agendamento que deseja cancelar.\n"
            "_(💡 Dica: Digite 'menu' para voltar ao início)_"
        )
    
    def _formatar_lista_agendamentos(self, agendamentos: List[Dict[str, Any]]) -> str:
        """Formata a lista de agendamentos para exibição."""
        linhas = []
        
        for i, ag in enumerate(agendamentos, 1):
            # Parse da data para formato legível
            data_hora_str = ag.get("data_hora", "")
            try:
                data_hora = datetime.fromisoformat(data_hora_str.replace("Z", "+00:00"))
                data_formatada = data_hora.strftime("%d/%m/%Y às %H:%M")
            except (ValueError, AttributeError):
                data_formatada = data_hora_str
            
            servico = ag.get("servico", "Serviço").capitalize()
            
            linhas.append(f"{i}️⃣ *{servico}* - {data_formatada}")
        
        return "\n".join(linhas)
    
    def _processar_selecao(self, context: UserContext, message: str) -> str:
        """
        Processa a seleção do usuário e executa o cancelamento.
        Re-busca os agendamentos para garantir que a lista está atualizada.
        """
        # Re-busca a lista (Stateless approach)
        agendamentos = buscar_agendamentos_futuros(context.phone)
        
        if not agendamentos:
            context.update_state(ConversationState.START)
            return (
                "❌ A lista de agendamentos mudou ou expirou.\n"
                "Digite *cancelar* para ver seus agendamentos novamente."
            )
        
        # Valida se é um número
        if not message.isdigit():
            return (
                "❌ Por favor, digite apenas o *número* do agendamento.\n"
                "_(💡 Dica: Digite 'menu' para cancelar a operação)_"
            )
        
        indice = int(message) - 1  # Converte para 0-indexed
        
        if not (0 <= indice < len(agendamentos)):
            return (
                f"❌ Opção inválida. Escolha um número de 1 a {len(agendamentos)}.\n"
                "_(💡 Dica: Digite 'menu' para cancelar a operação)_"
            )
        
        # Recupera o agendamento selecionado
        agendamento = agendamentos[indice]
        agendamento_id = agendamento.get("id")
        calendar_event_id = agendamento.get("calendar_event_id")
        servico = agendamento.get("servico", "Serviço").capitalize()
        
        logger.info(f"Cancelando agendamento {agendamento_id} para {context.phone}")
        
        # 1. Tenta cancelar no Google Calendar (resiliente a falhas)
        if calendar_event_id:
            calendar_success = cancelar_evento(calendar_event_id)
            if not calendar_success:
                logger.warning(
                    f"Falha ao cancelar evento {calendar_event_id} no Calendar, "
                    f"prosseguindo com cancelamento no banco."
                )
        
        # 2. Marca como cancelado no banco (soft delete)
        db_success = marcar_agendamento_como_cancelado(agendamento_id)
        
        if not db_success:
            logger.error(f"Falha crítica ao cancelar agendamento {agendamento_id} no banco")
            return (
                "❌ Ocorreu um erro ao cancelar seu agendamento.\n"
                "Por favor, tente novamente ou contate o suporte."
            )
        
        # Sucesso
        context.update_state(ConversationState.START)
        
        logger.info(f"Agendamento {agendamento_id} ({servico}) cancelado com sucesso")
        
        return (
            f"✅ *Agendamento cancelado com sucesso!*\n\n"
            f"🗑️ Serviço: {servico}\n\n"
            "Obrigado por nos informar. Esperamos atendê-lo em breve!\n\n"
            "Digite *menu* para ver as opções disponíveis."
        )
