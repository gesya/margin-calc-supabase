from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel


class SaleCreate(BaseModel):
    provider_id: int
    order_id: str
    sku: str
    quantity: int
    price: Decimal
    commission_amount: Decimal | None = None
    shipping_cost: Decimal | None = None
    created_at: datetime | None = None


class SaleRead(BaseModel):
    id: int
    provider_id: int
    order_id: str
    sku: str
    quantity: int
    price: Decimal
    commission_amount: Decimal | None
    shipping_cost: Decimal | None
    created_at: datetime

    class Config:
        from_attributes = True
