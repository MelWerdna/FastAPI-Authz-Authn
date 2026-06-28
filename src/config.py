from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigFile(BaseSettings):
    projectName: str = "FastApi AuthN and AuthZ service"
    DEBUG: bool = True

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    modelConfig = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = ConfigFile()