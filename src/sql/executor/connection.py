from sqlalchemy import create_engine

from src.config.settings import settings

from sqlalchemy.orm import declarative_base, sessionmaker


_engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)


def get_engine():
    return _engine


# Session factory for context managers used by the conversation manager
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,
)

# Base class for SQLAlchemy ORM models
Base = declarative_base()


def init_db() -> None:
    """Create all database tables if they don't already exist."""
    from src.conversation.database import ConversationDB, ConversationTurnDB  # noqa: F401

    Base.metadata.create_all(bind=_engine)