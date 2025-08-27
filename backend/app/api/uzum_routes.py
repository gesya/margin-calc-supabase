from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.models.provider import Provider
from app.providers.uzum import UzumProvider
from app.services.sales_ingestion import sync_sales_from_provider


router = APIRouter()


@router.post("/sync/uzum", response_model=int)
def sync_uzum(since: datetime | None = None, until: datetime | None = None, db: Session = Depends(get_db_session)):
    provider = db.query(Provider).filter(Provider.name == UzumProvider.name).first()
    if not provider:
        provider = Provider(name=UzumProvider.name)
        db.add(provider)
        db.commit()
        db.refresh(provider)
    client = UzumProvider()
    count = sync_sales_from_provider(db=db, provider=provider, provider_client=client, since=since, until=until)
    return count
