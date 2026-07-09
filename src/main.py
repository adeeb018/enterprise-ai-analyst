from sqlalchemy import text

from src.config.database import engine


def main():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()

    print(version)


if __name__ == "__main__":
    main()