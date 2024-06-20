import os
from pathlib import Path
from typing import Iterator

from dotenv import get_key
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.const import ENV_PATH

DB_PATH = f"postgresql://{get_key(ENV_PATH, "DB_USERNAME") or "postgres"}:{get_key(ENV_PATH, "DB_PASSWORD") or "postgres"}@{get_key(ENV_PATH, "DB_HOST") or "postgres"}:5432/{get_key(ENV_PATH, "DB_NAME") or "postgres"}"


ALEMBIC_INI_PATH = os.path.join(Path(__file__).parent, "alembic", "alembic.ini")


def get_engine():
    engine = create_engine(DB_PATH, echo=False)
    return engine


ENGINE = get_engine()


SessionMaker = sessionmaker(bind=ENGINE, autoflush=False)


def session_local() -> Iterator[Session]:
    with SessionMaker() as session:
        yield session


def run_migrations():
    os.system(f"alembic -c {ALEMBIC_INI_PATH} revision --autogenerate")
    os.system(f"alembic -c {ALEMBIC_INI_PATH} upgrade head")
