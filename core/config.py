from pydantic import HttpUrl, SecretStr, EmailStr, FilePath
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Bot Ar-Condicionado"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Google Calendar
    GOOGLE_CALENDAR_ID: EmailStr
    GOOGLE_CREDENTIALS_PATH: FilePath
    
    # Supabase
    SUPABASE_URL: HttpUrl
    SUPABASE_KEY: SecretStr

    # Whatsapp (Evolution API)
    EVOLUTION_API_URL: Optional[HttpUrl] = None
    EVOLUTION_API_KEY: Optional[SecretStr] = None
    
    # Config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore",
        case_sensitive=True
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
