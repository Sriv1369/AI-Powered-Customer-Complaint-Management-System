import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv(find_dotenv())

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./complaints.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db_session():
    """Context manager or helper for acquiring a database session."""
    session = SessionLocal()
    try:
        return session
    except Exception:
        session.close()
        raise


def init_db():
    """Initializes all database tables defined in models."""
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
