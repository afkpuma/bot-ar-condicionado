
import requests
import json
import time

def test_new_resets():
    url = "http://127.0.0.1:8000/whatsapp?simulacao=false"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Test "opa" greeting
    print("Testing 'opa' greeting for reset...")
    payload_opa = {
        "telefone": "11987654321",
        "mensagem": "opa"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload_opa))
    print(f"Response (should be welcome menu): {response.json().get('resposta')[:50]}...")

    # Test "bom dia" greeting
    print("\nTesting 'bom dia' greeting for reset...")
    payload_bom_dia = {
        "telefone": "11987654321",
        "mensagem": "bom dia"
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload_bom_dia))
    print(f"Response (should be welcome menu): {response.json().get('resposta')[:50]}...")

if __name__ == "__main__":
    test_new_resets()
