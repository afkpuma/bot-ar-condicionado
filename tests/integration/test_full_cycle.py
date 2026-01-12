import requests
import json
import sys
import os
import time

# Adiciona raiz ao path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def test_full_cycle():
    url = "http://127.0.0.1:8000/whatsapp?simulacao=false"
    headers = {'Content-Type': 'application/json'}
    telefone = "11977776666" # Número reservado para este teste

    def enviar(mensagem, contexto=""):
        print(f"\n📤 [User]: '{mensagem}' ({contexto})")
        payload = {"telefone": telefone, "mensagem": mensagem}
        try:
            resp = requests.post(url, headers=headers, data=json.dumps(payload))
            texto = resp.json().get('resposta', '')
            print(f"🤖 [Bot]: {texto[:100].replace(chr(10), ' ')}...") 
            return texto
        except Exception as e:
            print(f"❌ Erro de Conexão: {e}")
            return ""

    print(f"--- 🔄 INICIANDO TESTE DE CICLO COMPLETO (AGENDAR + CANCELAR) ---")

    # 1. Reset
    enviar("menu", "Reset Inicial")

    # 2. Agendar (Fluxo Feliz)
    enviar("1", "Serviço: Limpeza")
    enviar("25/12/2026", "Data Futura")
    # Seleciona o primeiro horário disponível dinamicamente
    enviar("1", "Horário: Primeiro disponível do menu") 
    enviar("Tester Full Cycle", "Nome")
    enviar("Rua Integração", "Rua")
    enviar("100", "Número")
    enviar("Bairro QA", "Bairro")
    enviar("Cidade Teste", "Cidade")
    
    # 3. Fase de Confirmação (Fase 3)
    msg_review = enviar("00000-000", "CEP -> Review")
    
    if "confira os dados" not in msg_review.lower() and "estão corretos" not in msg_review.lower():
        print(f"❌ FALHA: O Bot não pediu confirmação. Resposta: {msg_review}")
        return
    else:
        print("✅ Checkpoint: Confirmação solicitada corretamente.")

    enviar("sim", "Confirmar Agendamento")
    
    print("\n--- ⏳ Aguardando persistência... ---")
    time.sleep(2)

    # 4. Fase de Cancelamento (Fase 4)
    msg_cancel = enviar("cancelar", "Comando Cancelar")
    
    if "1." in msg_cancel and "Limpeza" in msg_cancel:
        print("✅ Checkpoint: Agendamento listado corretamente.")
    elif "não possui agendamentos" in msg_cancel.lower():
        print("❌ FALHA: O agendamento não foi encontrado (Erro ao salvar?).")
        return
    else:
        print(f"⚠️ ALERTA: Resposta inesperada: {msg_cancel}")

    # 5. Efetivar Cancelamento
    msg_final = enviar("1", "Selecionar ID para cancelar")
    
    if "cancelado com sucesso" in msg_final.lower():
        print("\n✅✅ SUCESSO TOTAL: Ciclo Agendar -> Cancelar funcionou perfeitamente!")
    else:
        print(f"\n❌ FALHA: O bot não confirmou o cancelamento. Resposta: {msg_final}")

if __name__ == "__main__":
    test_full_cycle()
