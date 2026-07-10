from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool, StaticPool
from app.config import settings
from app.models import Base
import logging

logger = logging.getLogger(__name__)

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create engine with appropriate pool configuration
if _is_sqlite:
    # SQLite: use StaticPool with check_same_thread=False for dev/testing
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG,
    )
elif settings.ENVIRONMENT == "production":
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=settings.DEBUG,
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


async def async_init_db():
    """Async database initialization."""
    init_db()


def verify_db_connection():
    """Verify database connection is working."""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection verified.")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


if not _is_sqlite:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Listen for database connections."""
        if settings.ENVIRONMENT == "production":
            dbapi_conn.isolation_level = None
