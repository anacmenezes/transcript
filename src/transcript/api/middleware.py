import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.transcript.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)

logger = logging.getLogger("transcript.http")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception:
            logger.exception(
                "Erro ao processar requisicao",
                extra={"request_id": request_id},
            )
            raise
        finally:
            duration = time.perf_counter() - start_time
            route = request.scope.get("route")
            route_name = getattr(route, "path", None) or "unmatched"

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                route=route_name,
                status_code=str(status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                route=route_name,
            ).observe(duration)

            logger.info(
                "Requisicao HTTP concluida",
                extra={"request_id": request_id},
            )