from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Marketplace Sales"
    database_url: str = Field(default="sqlite:///./sales.db", alias="DATABASE_URL")
    environment: str = Field(default="dev", alias="ENV")
    secret_key: str = Field(default="dev-secret", alias="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
