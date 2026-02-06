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

    # Add TRANSFORMATION to imagetypeenum (PostgreSQL only)
    # Note: SQLAlchemy stores enum NAMES (uppercase) not VALUES (lowercase) in PostgreSQL
    if "postgresql" in SQLALCHEMY_DATABASE_URL:
        try:
            with engine.connect() as conn:
                # Check if TRANSFORMATION already exists in the enum (uppercase, matching enum name)
                result = conn.execute(text(
                    "SELECT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'TRANSFORMATION' "
                    "AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'imagetypeenum'))"
                ))
                exists = result.scalar()
                if not exists:
                    conn.execute(text("ALTER TYPE imagetypeenum ADD VALUE IF NOT EXISTS 'TRANSFORMATION'"))
                    conn.commit()
                    logger.info("Added 'TRANSFORMATION' to imagetypeenum")
        except Exception as e:
            logger.warning(f"Could not add TRANSFORMATION to imagetypeenum: {e}")

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

    # Widen feature columns from VARCHAR(100) to VARCHAR(500) for ASIN-imported long features
    if "generation_sessions" in table_names and "postgresql" in SQLALCHEMY_DATABASE_URL:
        try:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE generation_sessions ALTER COLUMN feature_1 TYPE VARCHAR(500)"))
                conn.execute(text("ALTER TABLE generation_sessions ALTER COLUMN feature_2 TYPE VARCHAR(500)"))
                conn.execute(text("ALTER TABLE generation_sessions ALTER COLUMN feature_3 TYPE VARCHAR(500)"))
                conn.commit()
                logger.info("Widened feature_1/2/3 columns to VARCHAR(500)")
        except Exception as e:
            logger.warning(f"Could not widen feature columns (may already be correct): {e}")

    # Add email column to user_settings (for admin lookup by email)
    if "user_settings" in table_names:
        try:
            us_columns = [col["name"] for col in inspector.get_columns("user_settings")]
            if "email" not in us_columns:
                with engine.connect() as conn:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS email VARCHAR(255)"))
                        # Create index for email lookup
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_settings_email ON user_settings(email)"))
                    else:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN email VARCHAR(255)"))
                        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_user_settings_email ON user_settings(email)"))
                    conn.commit()
                    logger.info("Added email column to user_settings")
        except Exception as e:
            logger.warning(f"Could not add email column to user_settings: {e}")

        # Amazon SP-API connection columns.
        try:
            us_columns = [col["name"] for col in inspector.get_columns("user_settings")]
            with engine.connect() as conn:
                if "amazon_refresh_token_encrypted" not in us_columns:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS amazon_refresh_token_encrypted TEXT"))
                    else:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN amazon_refresh_token_encrypted TEXT"))
                    logger.info("Added amazon_refresh_token_encrypted column to user_settings")
                if "amazon_seller_id" not in us_columns:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS amazon_seller_id VARCHAR(64)"))
                    else:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN amazon_seller_id VARCHAR(64)"))
                    logger.info("Added amazon_seller_id column to user_settings")
                if "amazon_marketplace_id" not in us_columns:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS amazon_marketplace_id VARCHAR(32)"))
                    else:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN amazon_marketplace_id VARCHAR(32)"))
                    logger.info("Added amazon_marketplace_id column to user_settings")
                if "amazon_connected_at" not in us_columns:
                    if "postgresql" in SQLALCHEMY_DATABASE_URL:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS amazon_connected_at TIMESTAMP"))
                    else:
                        conn.execute(text("ALTER TABLE user_settings ADD COLUMN amazon_connected_at DATETIME"))
                    logger.info("Added amazon_connected_at column to user_settings")
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not add Amazon columns to user_settings: {e}")


def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
