from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from .api.routes import agent, bookings, countries, health, tours
from .core.config import settings
from .core.db import engine, init_db
from .services.seeder import seed_tours


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        seed_tours(session)
    yield


app = FastAPI(
    title="Selling Tours API",
    version="0.1.0",
    description="Tours platform backend: list/filter tours, view details, create and list bookings.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_STATUS_CODE_LABELS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "unprocessable_entity",
    500: "internal_error",
}


def _envelope(code: str, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details or {}}}


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        code = str(exc.detail.get("code", "error"))
        message = str(exc.detail.get("message", "Error"))
        details = exc.detail.get("details", {}) or {}
    else:
        code = _STATUS_CODE_LABELS.get(exc.status_code, "error")
        message = str(exc.detail) if exc.detail else "Error"
        details = {}
    return JSONResponse(status_code=exc.status_code, content=_envelope(code, message, details))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_envelope(
            "validation_error",
            "Invalid request",
            {"errors": jsonable_encoder(exc.errors())},
        ),
    )


app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(tours.router, prefix="/api", tags=["tours"])
app.include_router(countries.router, prefix="/api", tags=["countries"])
app.include_router(bookings.router, prefix="/api", tags=["bookings"])
app.include_router(agent.router, prefix="/api", tags=["agent"])

_static_dir = os.getenv("STATIC_DIR", "").strip()
if _static_dir and Path(_static_dir).is_dir():
    app.mount(
        "/",
        StaticFiles(directory=_static_dir, html=True),
        name="spa",
    )
