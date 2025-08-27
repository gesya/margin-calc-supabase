from datetime import datetime
from decimal import Decimal

from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Sale(Base):
    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "order_id",
            "sku",
            "created_at",
            name="uq_sale_provider_order_sku_created",
        ),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("provider.id"), index=True)
    order_id: Mapped[str] = mapped_column(String(128), index=True)
    sku: Mapped[str] = mapped_column(String(128), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    commission_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    shipping_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    provider = relationship("Provider")
