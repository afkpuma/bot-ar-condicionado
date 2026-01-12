
import requests
import json

def test_whatsapp_reset():
    url = "http://127.0.0.1:8000/whatsapp?simulacao=false"
    payload = {
        "telefone": "11987654321",
        "mensagem": "oi"
    }
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_whatsapp_reset()
