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
    return {
        "telefone": dados.telefone,
        "resposta": f"Recebi sua mensagem: {dados.mensagem}"
    }
