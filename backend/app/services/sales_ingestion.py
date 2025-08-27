from __future__ import annotations

from datetime import datetime
from typing import Iterable

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.provider import Provider
from app.models.sale import Sale
from app.schemas.sale import SaleCreate
from app.providers.base import SalesProvider


def sync_sales_from_provider(
    *,
    db: Session,
    provider: Provider,
    provider_client: SalesProvider,
    since: datetime | None = None,
    until: datetime | None = None,
) -> int:
    inserted = 0
    for sale_input in provider_client.fetch_sales(since=since, until=until):
        sale: Sale = Sale(
            provider_id=provider.id,
            order_id=sale_input.order_id,
            sku=sale_input.sku,
            quantity=sale_input.quantity,
            price=sale_input.price,
            commission_amount=sale_input.commission_amount,
            shipping_cost=sale_input.shipping_cost,
            created_at=sale_input.created_at or datetime.utcnow(),
        )
        db.add(sale)
        try:
            db.commit()
            inserted += 1
        except IntegrityError:
            db.rollback()
            # duplicate by unique constraint -> skip
            continue
    return inserted
