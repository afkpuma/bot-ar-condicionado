from datetime import datetime
from services.supabase_client import supabase
from services.agendamentos_service import salvar_agendamento
from scripts.calendar_utils import horario_disponivel, criar_evento

# =========================
# FLUXO PRINCIPAL WHATSAPP
# =========================
def processar_mensagem_whatsapp(telefone: str, mensagem: str):
    """
    Processa a mensagem enviada pelo usuário via WhatsApp
    e retorna a resposta do bot.
    """
    mensagem = mensagem.strip().lower()

    # Busca a conversa existente no Supabase
    response = supabase.table("conversas_whatsapp") \
        .select("*") \
        .eq("telefone", telefone) \
        .limit(1) \
        .execute()

    conversa = response.data[0] if response.data else None

    # 1️⃣ INÍCIO DA CONVERSA
    if not conversa:
        supabase.table("conversas_whatsapp").insert({
            "telefone": telefone,
            "etapa": "SERVICO"
        }).execute()

        return (
            "Olá! 👋\n"
            "Qual serviço você deseja?\n\n"
            "🛠 limpeza\n"
            "🔧 instalação\n"
            "⚙️ manutenção"
        )

    # Conversa já existe
    dados = conversa
    etapa = dados.get("etapa")

    # 2️⃣ ESCOLHA DO SERVIÇO
    if etapa == "SERVICO":
        if "limpeza" in mensagem:
            servico = "limpeza"
        elif "instala" in mensagem:
            servico = "instalacao"
        elif "manuten" in mensagem:
            servico = "manutencao"
        else:
            return "Não entendi 😅 Digite: limpeza, instalação ou manutenção."

        supabase.table("conversas_whatsapp").update({
            "servico": servico,
            "etapa": "DATA"
        }).eq("telefone", telefone).execute()

        return "Perfeito! Qual data você prefere? (YYYY-MM-DD)"

    # 3️⃣ DATA
    if etapa == "DATA":
        supabase.table("conversas_whatsapp").update({
            "data": mensagem,
            "etapa": "HORA"
        }).eq("telefone", telefone).execute()

        return "Ótimo! Agora informe o horário (HH:MM)"

    # 4️⃣ HORA
    if etapa == "HORA":
        supabase.table("conversas_whatsapp").update({
            "hora": mensagem,
            "etapa": "NOME"
        }).eq("telefone", telefone).execute()

        return "Perfeito! Qual o seu nome completo?"

    # 5️⃣ NOME
    if etapa == "NOME":
        supabase.table("conversas_whatsapp").update({
            "nome": mensagem,
            "etapa": "ENDERECO"
        }).eq("telefone", telefone).execute()

        return "Agora me informe seu endereço completo.\nFormato: Rua, Número, Bairro, Cidade, CEP"

    # 6️⃣ ENDEREÇO
    if etapa == "ENDERECO":
        # Tenta quebrar a mensagem em partes
        try:
            partes = [p.strip() for p in mensagem.split(",")]
            rua = partes[0]
            numero = partes[1]
            bairro = partes[2]
            cidade = partes[3]
            cep = partes[4]
        except IndexError:
            return "Endereço inválido 😕\nUse o formato: Rua, Número, Bairro, Cidade, CEP"

        supabase.table("conversas_whatsapp").update({
            "rua": rua,
            "numero": numero,
            "bairro": bairro,
            "cidade": cidade,
            "cep": cep,
            "etapa": "FINALIZAR"
        }).eq("telefone", telefone).execute()

        return finalizar_agendamento_whatsapp(telefone)

    return "Algo deu errado 😕 Tente novamente."


# =========================
# FINALIZA AGENDAMENTO
# =========================
def finalizar_agendamento_whatsapp(telefone: str):
    """
    Finaliza o agendamento com os dados da conversa,
    criando evento no Google Calendar e salvando no Supabase.
    """
    response = supabase.table("conversas_whatsapp") \
        .select("*") \
        .eq("telefone", telefone) \
        .single() \
        .execute()

    if not response.data:
        return "Erro ao localizar seus dados. Tente novamente."

    dados = response.data

    # Validação de data e hora
    try:
        data_hora = datetime.strptime(
            f"{dados['data']} {dados['hora']}",
            "%Y-%m-%d %H:%M"
        )
    except (ValueError, KeyError):
        return "Data ou horário inválido 😕"

    # Monta o cliente
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

    # Verifica disponibilidade no Google Calendar
    if not horario_disponivel(
        calendar_id="yamyokai@gmail.com",
        data_hora_inicio=data_hora,
        servico=dados.get("servico")
    ):
        return "❌ Esse horário não está disponível. Escolha outro."

    # Cria evento no Google Calendar
    evento = criar_evento(
        calendar_id="yamyokai@gmail.com",
        data_hora_inicio=data_hora,
        servico=dados.get("servico"),
        cliente=cliente
    )

    # Salva no Supabase
    salvar_agendamento(
        nome_cliente=cliente["nome"],
        telefone=telefone,
        servico=dados.get("servico"),
        data_hora=data_hora,
        endereco=cliente["endereco"],
        calendar_event_id=evento.get("id")
    )

    return (
        "✅ Agendamento confirmado!\n\n"
        f"🛠 Serviço: {dados.get('servico', '').capitalize()}\n"
        f"📅 Data: {dados.get('data')}\n"
        f"⏰ Horário: {dados.get('hora')}\n"
        f"👤 Cliente: {cliente['nome']}\n"
        f"🏠 Endereço: {cliente['endereco']['rua']}, {cliente['endereco']['numero']}, "
        f"{cliente['endereco']['bairro']}, {cliente['endereco']['cidade']}, {cliente['endereco']['cep']}"
    )
