
from services.supabase_client import supabase
from datetime import datetime

def test_update():
    telefone = "11987654321"
    print(f"Testing manual updated_at for {telefone}...")
    try:
        now_iso = datetime.now().isoformat()
        response = supabase.table("conversas_whatsapp").update({
            "updated_at": now_iso
        }).eq("telefone", telefone).execute()
        print(f"Update response: {response.data}")
    except Exception as e:
        print(f"Update failed (probably column doesn't exist): {e}")

if __name__ == "__main__":
    test_update()
