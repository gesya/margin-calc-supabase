from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable

from app.schemas.sale import SaleCreate
from .base import SalesProvider


class MockProvider(SalesProvider):
    name = "mock"

    def fetch_sales(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> Iterable[SaleCreate]:
        base_time = since or (datetime.utcnow() - timedelta(days=1))
        for i in range(5):
            yield SaleCreate(
                provider_id=0,  # will be overwritten by service layer
                order_id=f"MOCKORDER-{base_time.strftime('%Y%m%d')}-{i}",
                sku=f"SKU-{1000 + i}",
                quantity=1 + (i % 3),
                price=Decimal("199.90") + Decimal(i),
                commission_amount=Decimal("19.99"),
                shipping_cost=Decimal("5.00"),
                created_at=base_time + timedelta(minutes=i * 5),
            )
