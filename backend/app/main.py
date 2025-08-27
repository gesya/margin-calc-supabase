from __future__ import annotations

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.api.routes import router
from app.api.uzum_routes import router as uzum_router
from app.core.scheduler import start_scheduler, stop_scheduler


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)

    @application.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        start_scheduler()

    application.include_router(router, prefix="/api")

    @application.get("/health")
    def health():
        return {"status": "ok"}

    application.include_router(uzum_router, prefix="/api")

    return application


app = create_app()
