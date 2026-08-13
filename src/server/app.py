from fastapi import FastAPI

from contextlib import asynccontextmanager
from .server import create_mcp_server


mcp_server = create_mcp_server()
mcp_app = mcp_server.streamable_http_app()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs FastMCP's session-manager task group inside FastAPI's lifespan,
    # so streamable HTTP sessions actually work.
    async with mcp_app.router.lifespan_context(app):
        yield

app = FastAPI(
    title="Enterprise AI Analyst",
    lifespan=lifespan
)


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "enterprise-ai-analyst",
    }


app.mount(
    "/",
    mcp_app,
)