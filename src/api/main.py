from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.diagnostics import emit_event
from src.api.schemas import (
    AnomalyPoint,
    ForecastResponse,
    HistoricalPoint,
)
from scripts.install_serving_bundle import BundleInstallError, resolve_serving_root
from src.api.service import ForecastService, ServiceNotReadyError
from src.utils.config import MAX_FORECAST_HORIZON, PROJECT_ROOT


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    service = create_forecast_service()
    app.state.forecast_service = service
    emit_event(
        "api_startup",
        component="lifecycle",
        ready=getattr(service, "ready", True),
        readiness_code=getattr(service, "readiness_code", "not_applicable"),
        failure_category=getattr(service, "readiness_failure_category", None),
        history_rows=len(getattr(service, "history", [])),
        model_loaded=bool(getattr(service, "forecast_artifact", {})),
    )
    try:
        yield
    finally:
        emit_event("api_shutdown", component="lifecycle")
        del app.state.forecast_service


def create_forecast_service() -> ForecastService:
    """Create a service from the local root or an explicitly pinned bundle."""

    try:
        root = resolve_serving_root()
    except BundleInstallError as exc:
        emit_event(
            "serving_bundle_install_failed",
            level="ERROR",
            component="artifact_loader",
            failure_category="serving_bundle_install_error",
            error_type=type(exc).__name__,
            readiness_code="artifact_validation_failed",
        )
        root = PROJECT_ROOT / "__unavailable_serving_bundle__"
    if root == PROJECT_ROOT:
        return ForecastService()
    return ForecastService(root=root)


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


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return str(path) if path else "<unmatched>"


@app.middleware("http")
async def request_diagnostics(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = uuid4().hex
    request.state.request_id = request_id
    started = perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        emit_event(
            "api_request_failed",
            level="ERROR",
            component="request",
            request_id=request_id,
            method=request.method,
            route=_route_template(request),
            error_type=type(exc).__name__,
            duration_ms=round((perf_counter() - started) * 1000, 3),
        )
        raise
    response.headers["X-Request-ID"] = request_id
    emit_event(
        "api_request_completed",
        component="request",
        request_id=request_id,
        method=request.method,
        route=_route_template(request),
        status_code=response.status_code,
        duration_ms=round((perf_counter() - started) * 1000, 3),
    )
    return response


def get_service(request: Request) -> ForecastService:
    return request.app.state.forecast_service


@app.exception_handler(ServiceNotReadyError)
def service_not_ready(
    request: Request,
    _exc: ServiceNotReadyError,
) -> JSONResponse:
    service = get_service(request)
    emit_event(
        "api_service_not_ready",
        level="WARNING",
        component="readiness",
        request_id=getattr(request.state, "request_id", None),
        route=_route_template(request),
        readiness_code=getattr(service, "readiness_code", "artifact_validation_failed"),
        failure_category=getattr(service, "readiness_failure_category", None),
    )
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
    if not service.ready:
        emit_event(
            "api_readiness_failed",
            level="WARNING",
            component="readiness",
            request_id=getattr(request.state, "request_id", None),
            route=_route_template(request),
            readiness_code=service.readiness_code,
            failure_category=service.readiness_failure_category,
        )
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
