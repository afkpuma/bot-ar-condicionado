
import requests
import json

def test_time_validation():
    url = "http://127.0.0.1:8000/whatsapp?simulacao=false"
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Step 1: Ensure we are at HORA stage for the test number
    # (Assuming the previous tests left it in a clean state or we reset it)
    print("Pre-setting state to HORA...")
    # Normally we'd do a full flow, but for speed we can just hit the endpoint 
    # if we know the state. To be sure, let's reset and reach HORA.
    
    # Reset
    requests.post(url, headers=headers, data=json.dumps({"telefone": "11987654321", "mensagem": "oi"}))
    # Select service
    requests.post(url, headers=headers, data=json.dumps({"telefone": "11987654321", "mensagem": "1"}))
    # Select date
    requests.post(url, headers=headers, data=json.dumps({"telefone": "11987654321", "mensagem": "15/01/2026"}))

    # Test invalid time
    payload_invalid = {
        "telefone": "11987654321",
        "mensagem": "14:99"
    }
    print("Testing invalid time: 14:99")
    response = requests.post(url, headers=headers, data=json.dumps(payload_invalid))
    print(f"Response: {response.json().get('resposta')}")

    # Test valid time
    payload_valid = {
        "telefone": "11987654321",
        "mensagem": "14:30"
    }
    print("Testing valid time: 14:30")
    response = requests.post(url, headers=headers, data=json.dumps(payload_valid))
    print(f"Response: {response.json().get('resposta')}")

if __name__ == "__main__":
    test_time_validation()
