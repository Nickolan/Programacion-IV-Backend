import os
from typing import Generator
from dotenv import load_dotenv

from sqlmodel import Session, create_engine

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://postgre:nickolan@localhost:5432/db_food_store"
)

engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session