from typing import Iterator

from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine
from app.core.config import settings

load_dotenv()

DATABASE_URL = settings.DATABASE_URL

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not set. Configure it in your environment (Supabase direct connection string)."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=5)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


