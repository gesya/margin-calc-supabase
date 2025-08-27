from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Marketplace Sales"
    database_url: str = Field(default="sqlite:///./sales.db", alias="DATABASE_URL")
    environment: str = Field(default="dev", alias="ENV")
    secret_key: str = Field(default="dev-secret", alias="SECRET_KEY")

    # Uzum provider configuration
    uzum_base_url: str = Field(default="https://api-seller.uzum.uz/api/seller-openapi/v1", alias="UZUM_BASE_URL")
    uzum_api_key: str | None = Field(default=None, alias="UZUM_API_KEY")
    uzum_shop_ids: list[int] = Field(default_factory=list, alias="UZUM_SHOP_IDS")
    uzum_auth_header: str = Field(default="Authorization", alias="UZUM_AUTH_HEADER")
    uzum_auth_prefix: str = Field(default="Bearer", alias="UZUM_AUTH_PREFIX")
    uzum_date_from_param: str = Field(default="from", alias="UZUM_DATE_FROM_PARAM")
    uzum_date_to_param: str = Field(default="to", alias="UZUM_DATE_TO_PARAM")
    uzum_sync_interval_minutes: int = Field(default=15, alias="UZUM_SYNC_INTERVAL_MINUTES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
