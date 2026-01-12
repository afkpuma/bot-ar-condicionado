from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Bot Ar-Condicionado"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Google Calendar
    GOOGLE_CALENDAR_ID: str
    
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Whatsapp
    WHATSAPP_API_URL: str = "https://example.com/api" # Placeholder
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
