from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.database import Base

# Create engine
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

    # Add new columns to existing tables (SQLite doesn't support ALTER TABLE IF NOT EXISTS)
    from sqlalchemy import text, inspect
    inspector = inspect(engine)
    columns = [col["name"] for col in inspector.get_columns("generation_sessions")]
    if "aplus_visual_script" not in columns:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE generation_sessions ADD COLUMN aplus_visual_script JSON"))
            conn.commit()

    # Add reference_image_paths to prompt_history
    if "prompt_history" in inspector.get_table_names():
        ph_columns = [col["name"] for col in inspector.get_columns("prompt_history")]
        if "reference_image_paths" not in ph_columns:
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE prompt_history ADD COLUMN reference_image_paths JSON"))
                conn.commit()


def get_db():
    """Dependency injection for database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
