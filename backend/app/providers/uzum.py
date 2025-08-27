from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable, Any

import httpx

from app.core.config import settings
from app.schemas.sale import SaleCreate
from .base import SalesProvider


def _to_epoch_ms(dt: datetime) -> int:
    if dt.tzinfo is not None:
        # convert to UTC and drop tzinfo for epoch calc
        dt = dt.astimezone(tz=None).replace(tzinfo=None)
    return int(dt.timestamp() * 1000)


class UzumProvider(SalesProvider):
    name = "uzum"

    def __init__(self) -> None:
        base = settings.uzum_base_url.rstrip("/")
        self._orders_url = f"{base}/finance/orders"
        self._headers = {}
        if settings.uzum_api_key:
            # Try both Authorization and X-API-KEY for compatibility
            if settings.uzum_auth_header and settings.uzum_auth_prefix:
                self._headers[settings.uzum_auth_header] = f"{settings.uzum_auth_prefix} {settings.uzum_api_key}"
            self._headers.setdefault("X-API-KEY", settings.uzum_api_key)

    def fetch_sales(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> Iterable[SaleCreate]:
        params: dict[str, Any] = {}
        shop_ids = settings.uzum_shop_ids
        if shop_ids:
            # Encode as comma-separated to satisfy APIs that expect a single param
            params["shopIds"] = ",".join(str(sid) for sid in shop_ids)
        if since:
            params[settings.uzum_date_from_param] = _to_epoch_ms(since)
        if until:
            params[settings.uzum_date_to_param] = _to_epoch_ms(until)

        headers = {"Accept": "application/json"}
        headers.update(self._headers)

        try:
            with httpx.Client(timeout=30.0, headers=headers) as client:
                resp = client.get(self._orders_url, params=params)
                if resp.status_code != 200:
                    print(f"Uzum API non-200: {resp.status_code} url={resp.request.url} body={resp.text[:500]}")
                    return []
                data = resp.json()
        except Exception as exc:
            print(f"Uzum API request failed: {exc}")
            return []

        items: list[Any] = []
        if isinstance(data, dict):
            # try common wrappers
            for key in ("items", "orders", "data", "result"):
                if key in data and isinstance(data[key], list):
                    items = data[key]
                    break
            if not items and any(k in data for k in ("id", "orderId")):
                items = [data]
        elif isinstance(data, list):
            items = data

        results: list[SaleCreate] = []
        for raw in items:
            sale = self._parse_sale(raw)
            if sale:
                results.append(sale)
        return results

    def _parse_sale(self, raw: dict[str, Any]) -> SaleCreate | None:
        try:
            order_id = str(
                raw.get("orderId")
                or raw.get("order_id")
                or raw.get("id")
            )
            created_ms = (
                raw.get("createdAt")
                or raw.get("created_at")
                or raw.get("timestamp")
                or raw.get("date")
            )
            if isinstance(created_ms, (int, float)):
                created_at = datetime.utcfromtimestamp(float(created_ms) / 1000.0)
            elif isinstance(created_ms, str) and created_ms.isdigit():
                created_at = datetime.utcfromtimestamp(float(created_ms) / 1000.0)
            else:
                created_at = datetime.utcnow()

            # sku and quantity fallbacks
            sku = raw.get("sku") or raw.get("offerId") or raw.get("offer_id") or "UNKNOWN"
            quantity = (
                raw.get("quantity")
                or raw.get("qty")
                or 1
            )

            # price, commission, shipping fallbacks
            price = (
                raw.get("amount")
                or raw.get("price")
                or raw.get("totalPrice")
                or raw.get("sum")
                or 0
            )
            commission = (
                raw.get("commission")
                or raw.get("commissionAmount")
                or raw.get("fee")
                or 0
            )
            shipping = (
                raw.get("deliveryPrice")
                or raw.get("shipping_cost")
                or raw.get("shipping")
                or 0
            )

            return SaleCreate(
                provider_id=0,
                order_id=order_id,
                sku=str(sku),
                quantity=int(quantity),
                price=Decimal(str(price)),
                commission_amount=Decimal(str(commission)) if commission is not None else None,
                shipping_cost=Decimal(str(shipping)) if shipping is not None else None,
                created_at=created_at,
            )
        except Exception:
            return None
