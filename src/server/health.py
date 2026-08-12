from datetime import UTC, datetime


def health_check() -> dict:
    return {
        "status": "ok",
        "service": "enterprise-ai-analyst",
        "timestamp": datetime.now(UTC).isoformat(),
    }