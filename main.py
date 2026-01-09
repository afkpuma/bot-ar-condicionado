import os
from dotenv import load_dotenv
from supabase import create_client
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


class MensagemWhatsApp(BaseModel):
    telefone: str
    mensagem: str

app = FastAPI()

@app.get("/")
def home():
    return {"mensagem": "API do bot de ar-condicionado funcionando"}

@app.post("/whatsapp")
def receber_mensagem(dados: MensagemWhatsApp):
    texto = dados.mensagem.lower()

    if "limpeza" in texto:
        servico = "limpeza"
        resposta = (
            "Perfeito 😊\n"
            "O serviço de *Limpeza de Ar-Condicionado* custa R$ 150,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "instala" in texto:
        servico = "instalacao"
        resposta = (
            "Ótima escolha 😊\n"
            "O serviço de *Instalação de Ar-Condicionado* custa R$ 350,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "manuten" in texto:
        servico = "manutencao"
        resposta = (
            "Entendido 👍\n"
            "Para *Manutenção*, realizamos uma visita técnica.\n"
            "Qual dia e horário você prefere?"
        )

    else:
        servico = None
        resposta = (
            "Olá! 👋\n"
            "Trabalhamos com os seguintes serviços:\n"
            "- Limpeza\n"
            "- Instalação\n"
            "- Manutenção\n\n"
            "Qual serviço você deseja?"
        )

    if servico:
        supabase.table("atendimentos").insert({
            "telefone": dados.telefone,
            "servico": servico,
            "mensagem": dados.mensagem,
            "status": "em_atendimento"
        }).execute()

    return {
        "telefone": dados.telefone,
        "resposta": resposta
    }


