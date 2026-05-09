from __future__ import annotations

import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from utils.request_context import get_request_id

logger = logging.getLogger("medtech.errors")


def _error_payload(*, detail: str, code: str):
    return {
        "error": {
            "code": code,
            "detail": detail,
            "request_id": get_request_id(),
        }
    }


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(detail=str(exc.detail), code="http_error"),
        headers=getattr(exc, "headers", None),
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=_error_payload(detail="Internal server error", code="internal_error"),
    )

