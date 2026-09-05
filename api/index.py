"""Vercel entrypoint mounting the existing FastAPI app under /api."""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.api.main import app as core_app


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    async with core_app.router.lifespan_context(core_app):
        yield


app = FastAPI(title="CO2 Forecast Lab Vercel API", lifespan=lifespan)
app.mount("/api", core_app)
