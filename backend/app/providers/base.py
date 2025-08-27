from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable

from app.schemas.sale import SaleCreate


class SalesProvider(ABC):
    name: str

    @abstractmethod
    def fetch_sales(
        self,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> Iterable[SaleCreate]:
        raise NotImplementedError
