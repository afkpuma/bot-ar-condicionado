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
    
    # 4. Select Time
    # Note: validation might fail if slot is taken, but we test the flow
    print("\n[User]: 14:00")
    response = processar_mensagem_whatsapp(phone, "14:00")
    print(f"[Bot]: {response}")
    
    # 5. Name
    print("\n[User]: Teste Silva")
    response = processar_mensagem_whatsapp(phone, "Teste Silva")
    print(f"[Bot]: {response}")
    
    # 6. Street
    print("\n[User]: Rua Teste")
    response = processar_mensagem_whatsapp(phone, "Rua Teste")
    print(f"[Bot]: {response}")
    
    # ... shortcut to finish? No, need all steps.
    
if __name__ == "__main__":
    run_simulation()
