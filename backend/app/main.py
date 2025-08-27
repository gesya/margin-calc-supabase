from __future__ import annotations

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import engine
from app.models.base import Base
from app.api.routes import router


def create_app() -> FastAPI:
    application = FastAPI(title=settings.app_name)

    @application.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)

    application.include_router(router, prefix="/api")

    @application.get("/health")
    def health():
        return {"status": "ok"}

    return application


app = create_app()
