from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import Base

# Create engine
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {"connect_timeout": 10},
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=300,  # Recycle connections every 5 minutes
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

    # Add new columns to existing tables if they don't exist
    # This handles schema migrations for both SQLite and PostgreSQL
    from sqlalchemy import text, inspect
    import logging

    logger = logging.getLogger(__name__)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Only run migrations if tables exist
    if "generation_sessions" in table_names:
        try:
            columns = [col["name"] for col in inspector.get_columns("generation_sessions")]
            if "aplus_visual_script" not in columns:
                with engine.connect() as conn:
                    # PostgreSQL uses JSONB, SQLite uses JSON
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE generation_sessions ADD COLUMN IF NOT EXISTS aplus_visual_script JSONB"))
                    else:
                        conn.execute(text("ALTER TABLE generation_sessions ADD COLUMN aplus_visual_script JSON"))
                    conn.commit()
                    logger.info("Added aplus_visual_script column to generation_sessions")
        except Exception as e:
            logger.warning(f"Could not add aplus_visual_script column: {e}")

    if "prompt_history" in table_names:
        try:
            ph_columns = [col["name"] for col in inspector.get_columns("prompt_history")]
            if "reference_image_paths" not in ph_columns:
                with engine.connect() as conn:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE prompt_history ADD COLUMN IF NOT EXISTS reference_image_paths JSONB"))
                    else:
                        conn.execute(text("ALTER TABLE prompt_history ADD COLUMN reference_image_paths JSON"))
                    conn.commit()
                    logger.info("Added reference_image_paths column to prompt_history")
            if "model_name" not in ph_columns:
                with engine.connect() as conn:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE prompt_history ADD COLUMN IF NOT EXISTS model_name VARCHAR(100)"))
                    else:
                        conn.execute(text("ALTER TABLE prompt_history ADD COLUMN model_name VARCHAR(100)"))
                    conn.commit()
                    logger.info("Added model_name column to prompt_history")
        except Exception as e:
            logger.warning(f"Could not add columns to prompt_history: {e}")


def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
