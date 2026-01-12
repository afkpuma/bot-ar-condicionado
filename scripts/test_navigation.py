import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.whatsapp_service import processar_mensagem_whatsapp
import random

def test_navigation():
    phone = f"55119{random.randint(10000000, 99999999)}"
    print(f"--- Testing Navigation for {phone} ---")
    
    # 1. Start -> Select Service
    print("\n[User]: menu")
    print(f"[Bot]: {processar_mensagem_whatsapp(phone, 'menu')}")
    
    # 2. Select Service -> Select Date
    print("\n[User]: 1")
    print(f"[Bot]: {processar_mensagem_whatsapp(phone, '1')}")
    
    # 3. Select Date -> Select Time
    print("\n[User]: 20/01/2026")
    msg_date = processar_mensagem_whatsapp(phone, '20/01/2026')
    print(f"[Bot]: {msg_date}")
    
    # 4. TEST BACK: FROM TIME TO DATE
    print("\n[User]: voltar")
    msg_back = processar_mensagem_whatsapp(phone, 'voltar')
    print(f"[Bot]: {msg_back}")
    
    if "Qual data você prefere" in msg_back and "Dica: Digite 'voltar'" in msg_back:
        print("✅ SUCCESS: Bot went back to Date Selection with Tip.")
    else:
        print(f"❌ FAIL: Bot did not go back correctly or missing tip. Got: {msg_back}")
        
    # 5. TEST BACK: FROM DATE TO SERVICE
    # First we need to go back to Date (we are already there)
    # Now go back further
    print("\n[User]: voltar")
    msg_back_2 = processar_mensagem_whatsapp(phone, 'voltar')
    print(f"[Bot]: {msg_back_2}")
    
    if "Qual serviço você deseja" in msg_back_2:
         print("✅ SUCCESS: Bot went back to Service Selection.")
    else:
         print(f"❌ FAIL: Bot did not go back to Service. Got: {msg_back_2}")
         
    # 6. TEST INVALID BACK (From Start)
    # We are at Service. Go back -> Start/Menu? No, Service IS the first step after menu?
    # Actually state is SELECT_SERVICE. PREVIOUS is None or START?
    # PREVIOUS_STATE for SELECT_SERVICE is not defined in map (it's the first step).
    # So it should say "Não é possível voltar..."
    print("\n[User]: voltar")
    msg_back_3 = processar_mensagem_whatsapp(phone, 'voltar')
    print(f"[Bot]: {msg_back_3}")
    
    if "Não é possível voltar" in msg_back_3 or "menu" in msg_back_3:
        print("✅ SUCCESS: Bot handled invalid back correctly.")
    else:
        print(f"❌ FAIL: Bot handled invalid back incorrectly. Got: {msg_back_3}")

if __name__ == "__main__":
    test_navigation()
