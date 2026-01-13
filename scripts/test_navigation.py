import sys
import os
import random

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.whatsapp_service import processar_mensagem_whatsapp

def test_navigation():
    phone = f"55119{random.randint(10000000, 99999999)}"
    print(f"--- Testing New Navigation (Menu Reset) for {phone} ---")
    
    # 1. Start -> Select Service
    print("\n[User]: menu")
    resp = processar_mensagem_whatsapp(phone, 'menu')
    print(f"[Bot]: {resp}")
    
    # 2. Select Service -> Select Date
    print("\n[User]: 1")
    resp = processar_mensagem_whatsapp(phone, '1')
    print(f"[Bot]: {resp}")
    
    if "Qual data" in resp:
        print("✅ SUCCESS: Advanced to Date selection.")
    
    # 3. Test "Menu" Reset from middle of flow (Interrupting Date Selection)
    print("\n[User]: menu (Testing Reset)")
    resp = processar_mensagem_whatsapp(phone, 'menu')
    print(f"[Bot]: {resp}")
    
    # Check if we are back to Main Menu
    if "1" in resp and "Limpeza" in resp and "4" in resp:
        print("✅ SUCCESS: 'menu' command reset the flow to Main Menu correctly.")
    else:
        print(f"❌ FAIL: 'menu' did not reset flow. Got: {resp}")

    # 4. Test Invalid Input Behavior
    # Select service again to get to date input
    processar_mensagem_whatsapp(phone, '1')
    
    print("\n[User]: batata (Testing Invalid Input Hint)")
    resp = processar_mensagem_whatsapp(phone, 'batata')
    print(f"[Bot]: {resp}")
    
    if "menu" in resp.lower() and "reiniciar" in resp.lower():
         print("✅ SUCCESS: Error message contains the 'menu' hint.")
    else:
         print(f"❌ FAIL: Error message missing hint. Got: {resp}")

if __name__ == "__main__":
    test_navigation()
