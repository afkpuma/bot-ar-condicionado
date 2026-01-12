
from services.supabase_client import supabase

def check_conversa(telefone):
    print(f"Checking conversation for {telefone}...")
    try:
        response = supabase.table("conversas_whatsapp") \
            .select("*") \
            .eq("telefone", telefone) \
            .execute()
        
        if response.data:
            print(f"Found conversation: {response.data}")
        else:
            print("No conversation found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_conversa("11987654321")
