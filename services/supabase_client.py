"""
Cliente do Supabase.

Configura e exporta o cliente do Supabase para uso em todo o sistema.
As credenciais são carregadas de variáveis de ambiente por segurança.
"""


from supabase import create_client, Client
from core.config import get_settings

settings = get_settings()

# Cria e exporta o cliente do Supabase
# Este objeto será importado por outros módulos
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

