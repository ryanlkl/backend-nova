"""
Docstring for utils.db
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from supabase import create_client
from app_config import (
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_PORT,
    DB_NAME,
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE
)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={
        "connect_timeout": 10,
        "application_name": "nova_app"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

async def get_db():
    """
    Docstring for get_db
    """
    db = None
    try:
        db = SessionLocal()
        yield db
    except Exception as e:
        print(e)
        if db:
            db.rollback()
        raise
    finally:
        if db:
            db.close()
