from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"mensagem": "API do bot de ar-condicionado funcionando"}
