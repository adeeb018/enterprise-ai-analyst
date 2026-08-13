import os
import uvicorn

from src.server.app import app


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8001"))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
    )