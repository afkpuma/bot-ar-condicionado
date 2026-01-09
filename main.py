from fastapi import FastAPI
from pydantic import BaseModel

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
        resposta = (
            "Perfeito 😊\n"
            "O serviço de *Limpeza de Ar-Condicionado* custa R$ 150,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "instala" in texto:
        resposta = (
            "Ótima escolha 😊\n"
            "O serviço de *Instalação de Ar-Condicionado* custa R$ 350,00.\n"
            "Qual dia e horário você prefere?"
        )

    elif "manutenção" in texto:
        resposta = (
            "Entendido 👍\n"
            "Para *Manutenção*, realizamos uma visita técnica para avaliação.\n"
            "Qual dia e horário você prefere para a visita?"
        )

    else:
        resposta = (
            "Olá! 👋\n"
            "Trabalhamos com os seguintes serviços:\n"
            "- Limpeza\n"
            "- Instalação\n"
            "- Manutenção\n\n"
            "Qual serviço você deseja?"
        )

    return {
        "telefone": dados.telefone,
        "resposta": resposta
    }

