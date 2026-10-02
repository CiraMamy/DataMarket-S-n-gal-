import os
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def create_db_engine(database_url: Optional[str] = None):
    url = database_url or os.getenv("DATAMARKET_DATABASE_URL", "sqlite:///datamarket.db")
    return create_engine(url, future=True, echo=False)


def get_session_factory(engine=None):
    if engine is None:
        engine = create_db_engine()
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_database(engine=None):
    if engine is None:
        engine = create_db_engine()
    Base.metadata.create_all(bind=engine)
    return engine


__all__ = ["Base", "Session", "create_db_engine", "get_session_factory", "init_database"]
