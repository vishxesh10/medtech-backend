from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from utils.request_context import request_id_ctx_var


class RequestIdMiddleware(BaseHTTPMiddleware):
    header_name = "X-Request-Id"

    async def dispatch(self, request: Request, call_next):
        incoming = request.headers.get(self.header_name)
        request_id = incoming or uuid.uuid4().hex

        token = request_id_ctx_var.set(request_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)

        response.headers[self.header_name] = request_id
        response.headers["X-Response-Time-ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"
        return response

