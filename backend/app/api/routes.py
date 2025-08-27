from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.provider import Provider
from app.models.sale import Sale
from app.schemas.provider import ProviderCreate, ProviderRead
from app.schemas.sale import SaleRead
from app.providers.mock import MockProvider
from app.services.sales_ingestion import sync_sales_from_provider


router = APIRouter()


@router.post("/providers", response_model=ProviderRead)
def register_provider(payload: ProviderCreate, db: Session = Depends(get_db_session)):
    existing = db.query(Provider).filter(Provider.name == payload.name).first()
    if existing:
        return existing
    provider = Provider(name=payload.name, api_key=payload.api_key, base_url=payload.base_url)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@router.post("/sync/mock", response_model=int)
def sync_mock(since: datetime | None = None, until: datetime | None = None, db: Session = Depends(get_db_session)):
    provider = db.query(Provider).filter(Provider.name == MockProvider.name).first()
    if not provider:
        provider = Provider(name=MockProvider.name)
        db.add(provider)
        db.commit()
        db.refresh(provider)
    client = MockProvider()
    count = sync_sales_from_provider(db=db, provider=provider, provider_client=client, since=since, until=until)
    return count


@router.get("/sales", response_model=list[SaleRead])
def list_sales(limit: int = 100, db: Session = Depends(get_db_session)):
    rows = db.query(Sale).order_by(Sale.created_at.desc()).limit(limit).all()
    return rows
