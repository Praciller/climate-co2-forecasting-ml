"""Vercel entrypoint serving the dashboard and existing FastAPI app."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from pathlib import Path

from fastapi import FastAPI

from src.api.main import app as core_app


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with core_app.router.lifespan_context(core_app):
        yield


FRONTEND_DIRECTORY = Path(__file__).resolve().parent / "frontend_dist"


def create_app(frontend_directory: Path = FRONTEND_DIRECTORY) -> FastAPI:
    app = FastAPI(title="CO2 Forecast Lab Vercel API", lifespan=lifespan)
    app.mount("/api", core_app)
    app.frontend(
        "/",
        directory=str(frontend_directory),
        fallback="index.html",
        check_dir=False,
    )
    return app


app = create_app()
