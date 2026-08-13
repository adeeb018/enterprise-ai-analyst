from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.config.settings import settings


class MCPAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        # Keep health endpoint public.
        if request.url.path == "/health":
            return await call_next(request)

        authorization = request.headers.get(
            "Authorization"
        )

        expected = (
            f"Bearer {settings.mcp_api_key}"
        )

        if authorization != expected:

            return JSONResponse(
                {
                    "error": "Unauthorized",
                },
                status_code=401,
            )

        return await call_next(request)