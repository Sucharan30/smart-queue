import logging
from typing import Generator, Dict, Any, Optional
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

logger = logging.getLogger("smart_queue.database")

# SQLAlchemy declarative base for future models (Checkpoint 2+)
Base = declarative_base()

_engine: Optional[Engine] = None
_SessionLocal = None


def get_engine() -> Optional[Engine]:
    """
    Lazily creates and returns the SQLAlchemy Engine configured for Supabase.
    Applies production-safe connection pooling, timeouts, and pre-ping checks.
    """
    global _engine, _SessionLocal
    if _engine is not None:
        return _engine

    db_url = settings.get_database_url()
    if not db_url:
        logger.warning("No DATABASE_URL configured. Database engine will not be initialized.")
        return None

    try:
        # Connection pooling optimized for Supabase (Session Pooler or Direct)
        _engine = create_engine(
            db_url,
            pool_size=10,
            max_overflow=5,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10}
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        logger.info("SQLAlchemy engine initialized successfully with Psycopg 3.")
        return _engine
    except Exception as exc:
        logger.error(f"Failed to create SQLAlchemy engine: {exc}")
        return None


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        get_engine()
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request
    and ensures proper teardown.
    """
    session_factory = get_session_factory()
    if session_factory is None:
        raise RuntimeError("Database connection is not configured.")
    
    db = session_factory()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> Dict[str, Any]:
    """
    Performs a safe, non-destructive connection check against Supabase PostgreSQL.
    Executes SELECT 1; with low timeout to prevent hanging health checks.
    Sanitizes all responses to prevent credential leaks.
    """
    engine = get_engine()
    if engine is None:
        return {
            "connected": False,
            "message": "DATABASE_URL is not configured. Please supply Supabase connection string."
        }

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1;"))
            result.scalar()
            return {
                "connected": True,
                "message": "Supabase PostgreSQL connection active and responsive."
            }
    except Exception:
        # Never expose database password, connection string, or internal stack trace
        logger.warning("Supabase database health check failed: unable to establish connection.")
        return {
            "connected": False,
            "message": "Database service is unreachable or credentials are unverified."
        }
