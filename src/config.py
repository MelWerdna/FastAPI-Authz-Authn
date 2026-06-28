from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class ConfigFile(BaseSettings):
    project_name: str = "FastApi AuthN and AuthZ service"
    DEBUG: bool = Field(default=False, env="DEBUG")

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = ConfigFile()