from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.provider import Provider
from app.providers.uzum import UzumProvider
from app.services.sales_ingestion import sync_sales_from_provider


scheduler: Optional[BackgroundScheduler] = None


def start_scheduler() -> None:
    global scheduler
    if scheduler is not None:
        return
    scheduler = BackgroundScheduler()

    def job_sync_uzum():
        db = SessionLocal()
        try:
            try:
                provider = db.query(Provider).filter(Provider.name == UzumProvider.name).first()
                if not provider:
                    provider = Provider(name=UzumProvider.name)
                    db.add(provider)
                    db.commit()
                    db.refresh(provider)
                client = UzumProvider()
                # fetch last 30 minutes to be safe; unique constraint prevents dupes
                since = datetime.utcnow() - timedelta(minutes=max(15, settings.uzum_sync_interval_minutes) * 2)
                sync_sales_from_provider(db=db, provider=provider, provider_client=client, since=since)
            except Exception as exc:
                print(f"Scheduler Uzum sync failed: {exc}")
        finally:
            db.close()

    scheduler.add_job(job_sync_uzum, "interval", minutes=settings.uzum_sync_interval_minutes, id="uzum_sync", replace_existing=True)
    scheduler.start()


def stop_scheduler() -> None:
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
