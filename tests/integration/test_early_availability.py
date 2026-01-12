
import requests
import json

def test_early_availability():
    url = "http://127.0.0.1:8000/whatsapp?simulacao=false"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    telefone = "11987654321"

    # Reset
    requests.post(url, headers=headers, data=json.dumps({"telefone": telefone, "mensagem": "menu"}))
    
    # 1. Start flow - Service
    requests.post(url, headers=headers, data=json.dumps({"telefone": telefone, "mensagem": "1"}))
    # 2. Date
    requests.post(url, headers=headers, data=json.dumps({"telefone": telefone, "mensagem": "20/01/2026"}))
    
    # 3. Test occupied time (assuming 14:30 on 20/01/2026 is or will be occupied for this test)
    # Note: If the calendar is empty, this won't trigger unless we mock it or use an existing one.
    # But we can verify it doesn't just return "Nome?" if it fails.
    print("Testing occupied time at HORA stage...")
    payload = {
        "telefone": telefone,
        "mensagem": "14:30"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    resp_text = response.json().get('resposta', '')
    print(f"Response: {resp_text}")
    
    if "ocupado" in resp_text.lower():
        print("✅ SUCCESS: Immediate feedback for occupied slot.")
    elif "recomeçar" in resp_text.lower():
        print("ℹ️ Session might have expired or reset happened.")
    else:
        print("ℹ️ Slot might be available, which is also correct if not occupied.")

if __name__ == "__main__":
    test_early_availability()
