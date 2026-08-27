from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    AnomalyPoint,
    ForecastResponse,
    HistoricalPoint,
)
from src.api.service import ForecastService, ServiceNotReadyError
from src.utils.config import MAX_FORECAST_HORIZON


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.forecast_service = ForecastService()
    yield
    del app.state.forecast_service


app = FastAPI(
    title="CO2 Forecast Lab API",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def get_service(request: Request) -> ForecastService:
    return request.app.state.forecast_service


@app.exception_handler(ServiceNotReadyError)
def service_not_ready(
    _request: Request,
    _exc: ServiceNotReadyError,
) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Governed forecast artifacts are unavailable or invalid.",
            "code": "artifact_not_ready",
        },
    )


@app.get("/health")
def health(request: Request) -> dict[str, object]:
    service = get_service(request)
    return {
        "status": "ok",
        "ready": service.ready,
        "readiness_code": service.readiness_code,
        "model_loaded": bool(service.forecast_artifact) and service.ready,
        "history_rows": len(service.history),
    }


@app.get("/ready")
def readiness(request: Request) -> JSONResponse:
    service = get_service(request)
    status_code = 200 if service.ready else 503
    return JSONResponse(
        status_code=status_code,
        content={"ready": service.ready, "code": service.readiness_code},
    )


@app.get("/model-info")
def model_info(request: Request) -> dict[str, object]:
    return get_service(request).model_info()


@app.get("/historical-data", response_model=list[HistoricalPoint])
def historical_data(request: Request) -> list[dict[str, object]]:
    return get_service(request).historical_records()


@app.get("/forecast", response_model=ForecastResponse)
def forecast(
    request: Request,
    horizon_months: Annotated[
        int,
        Query(ge=1, le=MAX_FORECAST_HORIZON),
    ] = 24,
) -> ForecastResponse:
    return get_service(request).forecast(horizon_months)


@app.get("/anomalies", response_model=list[AnomalyPoint])
def anomalies(request: Request) -> list[dict[str, object]]:
    return get_service(request).anomalies()
