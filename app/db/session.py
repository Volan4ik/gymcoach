from __future__ import annotations

import os
from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://app:app@localhost:5432/app")

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

def get_session() -> Session:
    return Session(engine)