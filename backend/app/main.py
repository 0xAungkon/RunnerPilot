from __future__ import annotations
import os
from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from app.utils.core import parse_integrity_error

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.main import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.middlewares.AuthMiddleware import HeadersAuthMiddleware, JWTAuthMiddleware
from app.utils.core import on_startup, on_shutdown
from app.admin import setup_admin
from loguru import logger
setup_logging()

def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    on_startup()
    yield
    on_shutdown()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan
)


if settings.IS_DEV:
    # Initialize SQLAdmin using the modular setup
    setup_admin(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.success("⚙️  Running in DEVELOPMENT mode — CORS is disabled (allowing all origins).")

else:
    origins = settings.all_cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.success("🔒 Running in PRODUCTION mode — CORS restrictions are active.")


app.add_middleware(JWTAuthMiddleware)

app.add_middleware(HeadersAuthMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={"detail": parse_integrity_error(exc)}
    )