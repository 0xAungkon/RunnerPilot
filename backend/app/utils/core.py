import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from sqlalchemy.exc import IntegrityError
import emails  # type: ignore
import jwt
from jinja2 import Template
from jwt.exceptions import InvalidTokenError

from app.core import security
from app.core.config import settings
from app.core.logging import logger

def on_startup():
    logger.info(f"[{settings.ENVIRONMENT}] Starting up `{settings.PROJECT_NAME}`")

def on_shutdown():
    logger.info(f"[{settings.ENVIRONMENT}] Shutting down `{settings.PROJECT_NAME}` in {settings.ENVIRONMENT} mode" )


def parse_integrity_error(exc: IntegrityError):
    msg = str(exc.orig)
    if 'Key (' in msg and ')=' in msg:
        try:
            field = msg.split('Key (')[1].split(')=')[0]
            value = msg.split('DETAIL:  ')
            return [{
                "loc": ["body", field],
                "msg": value[1],
                "type": value[0]
            }]
        except Exception:
            pass
    return [{
        "loc": ["body", "__root__"],
        "msg": "A unique constraint was violated.",
        "type": "value_error.unique"
    }]

