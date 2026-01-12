from services.supabase_client import supabase

DURACAO_SERVICO = {
    "limpeza": 1,
    "instalacao": 3,
    "manutencao": 1,
}

def salvar_agendamento(
    nome_cliente,
    telefone,
    servico,
    data_hora,
    endereco,
    calendar_event_id
):
    duracao = DURACAO_SERVICO.get(servico)

    if not duracao:
        raise ValueError("Serviço inválido")

    data = {
        "nome_cliente": nome_cliente,
        "telefone": telefone,
        "servico": servico,
        "data_hora": data_hora.isoformat(),
        "duracao_horas": duracao,

        "rua": endereco["rua"],
        "numero": endereco["numero"],
        "bairro": endereco["bairro"],
        "cidade": endereco["cidade"],
        "cep": endereco["cep"],
        "complemento": endereco.get("complemento"),

        "calendar_event_id": calendar_event_id,
        "status": "confirmado"
    }

    response = supabase.table("agendamentos").insert(data).execute()
    return response.data
