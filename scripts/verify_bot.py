import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.whatsapp_service import processar_mensagem_whatsapp

import random

def run_simulation():
    phone = f"55119{random.randint(10000000, 99999999)}" # Random Test number
    
    print(f"--- Starting Simulation for {phone} ---")
    
    # 1. Start/Reset
    print("\n[User]: menu")
    response = processar_mensagem_whatsapp(phone, "menu")
    print(f"[Bot]: {response}")
    
    # 2. Select Service
    print("\n[User]: 1")
    response = processar_mensagem_whatsapp(phone, "1")
    print(f"[Bot]: {response}")
    
    # 3. Select Date
    print("\n[User]: 20/01/2026")
    response = processar_mensagem_whatsapp(phone, "20/01/2026")
    print(f"[Bot]: {response}")
    
    # 4. Select Time (using menu index)
    # The bot now shows a numbered menu, so we select "1" for the first option
    print("\n[User]: 1")
    response = processar_mensagem_whatsapp(phone, "1")
    print(f"[Bot]: {response}")
    
    # 5. Name
    print("\n[User]: Teste Silva")
    response = processar_mensagem_whatsapp(phone, "Teste Silva")
    print(f"[Bot]: {response}")
    
    # 6. Street
    print("\n[User]: Rua Teste")
    response = processar_mensagem_whatsapp(phone, "Rua Teste")
    print(f"[Bot]: {response}")

    # 7. Number
    print("\n[User]: 123")
    response = processar_mensagem_whatsapp(phone, "123")
    print(f"[Bot]: {response}")

    # 8. Neighborhood
    print("\n[User]: Centro")
    response = processar_mensagem_whatsapp(phone, "Centro")
    print(f"[Bot]: {response}")

    # 9. City
    print("\n[User]: São Paulo")
    response = processar_mensagem_whatsapp(phone, "São Paulo")
    print(f"[Bot]: {response}")

    # 10. CEP
    print("\n[User]: 01000-000")
    response = processar_mensagem_whatsapp(phone, "01000-000")
    print(f"[Bot]: {response}")
    
if __name__ == "__main__":
    run_simulation()
