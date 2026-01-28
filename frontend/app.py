"""
Frontend V2 - Interface Visual para Agendamento Rápido (Hybrid Architecture).

Este módulo fornece uma interface web responsiva usando Streamlit para
agendamento de serviços de ar-condicionado, reutilizando 100% da lógica
de backend existente em services/.

Uso:
    streamlit run frontend/app.py
"""

import sys
from pathlib import Path
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any

# =============================================================================
# CONFIGURAÇÃO DO PYTHON PATH
# =============================================================================
# Adiciona a raiz do projeto ao path para permitir imports dos services
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# IMPORTS DOS SERVICES (Reutilização 100%)
# =============================================================================
from services.google_calendar_service import (
    listar_horarios_livres,
    criar_evento,
    horario_disponivel
)
from services.agendamentos_service import salvar_agendamento
from core.logger import get_logger
from core.constants import DURACAO_SERVICO

# =============================================================================
# STREAMLIT IMPORT
# =============================================================================
import streamlit as st

# Logger
logger = get_logger(__name__)

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="❄️ Agendamento - Ar-Condicionado",
    page_icon="❄️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# ESTILOS CUSTOMIZADOS
# =============================================================================
st.markdown("""
    <style>
        /* Header customizado */
        .main-header {
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }
        
        /* Esconde o menu hamburger e footer padrão */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Estilo para labels */
        .stTextInput label, .stSelectbox label, .stDateInput label {
            font-weight: 600;
            color: #1f4e79;
        }
        
        /* Botão de submit */
        .stButton > button {
            width: 100%;
            background-color: #1f77b4;
            color: white;
            font-size: 1.1rem;
            padding: 0.75rem;
            border-radius: 8px;
        }
        
        /* Cards de informação */
        .info-card {
            background-color: #f0f8ff;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #1f77b4;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# CONSTANTES DO FORMULÁRIO
# =============================================================================
SERVICOS_DISPONIVEIS: Dict[str, str] = {
    "Limpeza": "limpeza",
    "Manutenção": "manutencao",
    "Instalação": "instalacao"
}


def get_horarios_para_data(data_selecionada: date, servico: str) -> List[str]:
    """
    Obtém a lista de horários disponíveis para uma data e serviço.
    
    Args:
        data_selecionada: Data para verificar disponibilidade.
        servico: Tipo de serviço (limpeza, manutencao, instalacao).
    
    Returns:
        Lista de horários no formato "HH:MM".
    """
    try:
        horarios = listar_horarios_livres(data_selecionada, servico)
        return horarios
    except Exception as e:
        logger.error(f"Erro ao buscar horários livres: {e}")
        return []


def processar_agendamento(
    nome: str,
    telefone: str,
    servico: str,
    data_hora: datetime,
    endereco: Dict[str, str]
) -> bool:
    """
    Processa o agendamento completo: Google Calendar + Supabase.
    
    Args:
        nome: Nome do cliente.
        telefone: Telefone do cliente (WhatsApp).
        servico: Tipo de serviço (chave interna: limpeza, manutencao, instalacao).
        data_hora: Data e hora do agendamento.
        endereco: Dicionário com rua, numero, bairro, cidade, cep.
    
    Returns:
        True se o agendamento foi criado com sucesso, False caso contrário.
    
    Raises:
        Exception: Re-levanta exceções após logar para exibição no frontend.
    """
    try:
        # 1. Cria evento no Google Calendar
        cliente = {
            "nome": nome,
            "telefone": telefone,
            "endereco": endereco
        }
        
        logger.info(f"Criando evento no Calendar para {nome} em {data_hora}")
        evento = criar_evento(data_hora, servico, cliente)
        
        if not evento or "id" not in evento:
            raise ValueError("Falha ao criar evento no Google Calendar")
        
        event_id = evento["id"]
        logger.info(f"Evento criado com ID: {event_id}")
        
        # 2. Salva no Supabase
        logger.info(f"Salvando agendamento no Supabase para {nome}")
        salvar_agendamento(
            nome_cliente=nome,
            telefone=telefone,
            servico=servico,
            data_hora=data_hora,
            endereco=endereco,
            calendar_event_id=event_id
        )
        
        logger.info(f"Agendamento concluído com sucesso para {nome}")
        return True
        
    except ValueError as e:
        logger.error(f"Erro de validação ao processar agendamento: {e}")
        raise
    except Exception as e:
        logger.critical(f"Erro inesperado ao processar agendamento: {e}")
        raise


def validar_campos(
    nome: str,
    telefone: str,
    rua: str,
    numero: str,
    bairro: str,
    cidade: str,
    cep: str,
    horario: Optional[str]
) -> Optional[str]:
    """
    Valida se todos os campos obrigatórios estão preenchidos.
    
    Args:
        nome: Nome do cliente.
        telefone: Telefone do cliente.
        rua: Rua do endereço.
        numero: Número do endereço.
        bairro: Bairro.
        cidade: Cidade.
        cep: CEP.
        horario: Horário selecionado.
    
    Returns:
        Mensagem de erro se houver campos inválidos, None se tudo OK.
    """
    campos_faltando = []
    
    if not nome or not nome.strip():
        campos_faltando.append("Nome")
    if not telefone or not telefone.strip():
        campos_faltando.append("Telefone")
    if not rua or not rua.strip():
        campos_faltando.append("Rua")
    if not numero or not numero.strip():
        campos_faltando.append("Número")
    if not bairro or not bairro.strip():
        campos_faltando.append("Bairro")
    if not cidade or not cidade.strip():
        campos_faltando.append("Cidade")
    if not cep or not cep.strip():
        campos_faltando.append("CEP")
    if not horario or horario == "Nenhum horário disponível":
        campos_faltando.append("Horário")
    
    if campos_faltando:
        return f"Por favor, preencha: {', '.join(campos_faltando)}"
    
    return None


# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================
def main() -> None:
    """Renderiza a interface principal do aplicativo."""
    
    # Header
    st.markdown("""
        <div class="main-header">
            <h1>❄️ Agendamento de Serviços</h1>
            <p style="color: #666;">Ar-Condicionado • Rápido e Fácil</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulário de Agendamento
    with st.form("form_agendamento", clear_on_submit=False):
        
        # =====================================================================
        # SEÇÃO 1: DADOS DO CLIENTE
        # =====================================================================
        st.subheader("👤 Seus Dados")
        
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input(
                "Nome Completo *",
                placeholder="Ex: João Silva"
            )
        with col2:
            telefone = st.text_input(
                "WhatsApp *",
                placeholder="Ex: 11987654321"
            )
        
        # =====================================================================
        # SEÇÃO 2: SERVIÇO
        # =====================================================================
        st.subheader("🔧 Serviço Desejado")
        
        servico_display = st.selectbox(
            "Tipo de Serviço *",
            options=list(SERVICOS_DISPONIVEIS.keys()),
            index=0
        )
        servico_key = SERVICOS_DISPONIVEIS[servico_display]
        
        # Info sobre duração
        duracao = DURACAO_SERVICO.get(servico_key, 1)
        st.info(f"⏱️ Duração estimada: {duracao} hora(s)")
        
        # =====================================================================
        # SEÇÃO 3: ENDEREÇO
        # =====================================================================
        st.subheader("📍 Endereço do Serviço")
        
        col_rua, col_num = st.columns([3, 1])
        with col_rua:
            rua = st.text_input("Rua *", placeholder="Ex: Rua das Flores")
        with col_num:
            numero = st.text_input("Número *", placeholder="123")
        
        col_bairro, col_cidade = st.columns(2)
        with col_bairro:
            bairro = st.text_input("Bairro *", placeholder="Ex: Centro")
        with col_cidade:
            cidade = st.text_input("Cidade *", placeholder="Ex: São Paulo")
        
        col_cep, col_compl = st.columns(2)
        with col_cep:
            cep = st.text_input("CEP *", placeholder="Ex: 01310-100")
        with col_compl:
            complemento = st.text_input("Complemento", placeholder="Apto 101 (opcional)")
        
        # =====================================================================
        # SEÇÃO 4: DATA E HORA
        # =====================================================================
        st.subheader("📅 Data e Horário")
        
        # Data mínima: amanhã (evita agendamentos para hoje com pouco tempo)
        data_minima = date.today() + timedelta(days=1)
        data_maxima = date.today() + timedelta(days=30)  # Limite de 30 dias
        
        col_data, col_hora = st.columns(2)
        
        with col_data:
            data_selecionada = st.date_input(
                "Data do Agendamento *",
                value=data_minima,
                min_value=data_minima,
                max_value=data_maxima,
                format="DD/MM/YYYY"
            )
        
        # Busca horários disponíveis para a data
        horarios = get_horarios_para_data(data_selecionada, servico_key)
        
        with col_hora:
            if horarios:
                horario_selecionado = st.selectbox(
                    "Horário Disponível *",
                    options=horarios,
                    index=0
                )
            else:
                horario_selecionado = st.selectbox(
                    "Horário Disponível *",
                    options=["Nenhum horário disponível"],
                    index=0
                )
                st.warning("⚠️ Sem horários para esta data. Tente outra.")
        
        # =====================================================================
        # BOTÃO DE SUBMIT
        # =====================================================================
        st.divider()
        submitted = st.form_submit_button(
            "✅ Confirmar Agendamento",
            use_container_width=True
        )
        
        # =====================================================================
        # PROCESSAMENTO DO FORMULÁRIO
        # =====================================================================
        if submitted:
            # Validação
            erro = validar_campos(
                nome, telefone, rua, numero, bairro, cidade, cep, horario_selecionado
            )
            
            if erro:
                st.error(f"❌ {erro}")
            else:
                # Combina data + hora
                hora_obj = datetime.strptime(horario_selecionado, "%H:%M").time()
                data_hora_agendamento = datetime.combine(data_selecionada, hora_obj)
                
                # Monta endereço
                endereco = {
                    "rua": rua.strip(),
                    "numero": numero.strip(),
                    "bairro": bairro.strip(),
                    "cidade": cidade.strip(),
                    "cep": cep.strip(),
                    "complemento": complemento.strip() if complemento else None
                }
                
                # Verifica disponibilidade uma última vez (double-check)
                if not horario_disponivel(data_hora_agendamento, servico_key):
                    st.error(
                        "❌ Este horário foi ocupado agora. "
                        "Por favor, selecione outro horário."
                    )
                else:
                    try:
                        with st.spinner("Processando seu agendamento..."):
                            sucesso = processar_agendamento(
                                nome=nome.strip(),
                                telefone=telefone.strip(),
                                servico=servico_key,
                                data_hora=data_hora_agendamento,
                                endereco=endereco
                            )
                        
                        if sucesso:
                            st.success(
                                f"✅ Agendamento confirmado!\n\n"
                                f"**Serviço:** {servico_display}\n\n"
                                f"**Data:** {data_selecionada.strftime('%d/%m/%Y')}\n\n"
                                f"**Horário:** {horario_selecionado}\n\n"
                                f"Você receberá uma confirmação no WhatsApp."
                            )
                            st.balloons()
                            
                    except ValueError as e:
                        st.error(f"❌ Erro de validação: {e}")
                        logger.error(f"ValueError no agendamento: {e}")
                    except Exception as e:
                        st.error(
                            "❌ Ocorreu um erro ao processar seu agendamento. "
                            "Por favor, tente novamente ou entre em contato por WhatsApp."
                        )
                        logger.critical(f"Erro crítico no agendamento: {e}")
    
    # Footer
    st.divider()
    st.markdown(
        "<p style='text-align: center; color: #888; font-size: 0.85rem;'>"
        "Dúvidas? Entre em contato pelo WhatsApp"
        "</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
