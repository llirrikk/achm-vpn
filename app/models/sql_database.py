from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DeclarativeModelBase = declarative_base()


def get_db() -> SessionLocal:  # type: ignore
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
