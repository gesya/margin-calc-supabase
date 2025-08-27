from pydantic import BaseModel, Field


class ProviderCreate(BaseModel):
    name: str = Field(..., max_length=100)
    api_key: str | None = None
    base_url: str | None = None


class ProviderRead(BaseModel):
    id: int
    name: str
    is_active: bool

    class Config:
        from_attributes = True
