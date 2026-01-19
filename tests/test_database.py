"""Tests for database models and session management"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import (
    Base,
    GenerationSession,
    SessionKeyword,
    ImageRecord,
    GenerationStatusEnum,
    ImageTypeEnum,
    IntentTypeEnum
)


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_generation_session(db):
    """Test creating a generation session"""
    session = GenerationSession(
        upload_path="/test/path.png",
        product_title="Test Product",
        feature_1="Feature 1",
        feature_2="Feature 2",
        feature_3="Feature 3",
        target_audience="Test Audience"
    )
    db.add(session)
    db.commit()

    # Query back
    result = db.query(GenerationSession).first()
    assert result is not None
    assert result.product_title == "Test Product"
    assert result.status == GenerationStatusEnum.PENDING
    assert result.id is not None
    assert len(result.id) == 36  # UUID length


def test_session_keyword_relationship(db):
    """Test keywords are linked to session"""
    session = GenerationSession(
        upload_path="/test/path.png",
        product_title="Test Product",
        feature_1="Feature 1",
        feature_2="Feature 2",
        feature_3="Feature 3",
        target_audience="Test Audience"
    )
    db.add(session)
    db.commit()

    # Add keywords
    keyword1 = SessionKeyword(
        session_id=session.id,
        keyword="sleep gummies",
        intent_types=["problem_solution", "durability"]
    )
    keyword2 = SessionKeyword(
        session_id=session.id,
        keyword="natural sleep aid",
        intent_types=["use_case"]
    )
    db.add_all([keyword1, keyword2])
    db.commit()

    # Query and check relationship
    result = db.query(GenerationSession).first()
    assert len(result.keywords) == 2
    assert result.keywords[0].keyword == "sleep gummies"


def test_image_record_relationship(db):
    """Test image records are linked to session"""
    session = GenerationSession(
        upload_path="/test/path.png",
        product_title="Test Product",
        feature_1="Feature 1",
        feature_2="Feature 2",
        feature_3="Feature 3",
        target_audience="Test Audience"
    )
    db.add(session)
    db.commit()

    # Add image records
    for image_type in ImageTypeEnum:
        record = ImageRecord(
            session_id=session.id,
            image_type=image_type
        )
        db.add(record)
    db.commit()

    # Query and check relationship
    result = db.query(GenerationSession).first()
    assert len(result.images) == len(ImageTypeEnum)  # All image types including STYLE_PREVIEW
    assert result.images[0].status == GenerationStatusEnum.PENDING


def test_cascade_delete(db):
    """Test that deleting session deletes related records"""
    session = GenerationSession(
        upload_path="/test/path.png",
        product_title="Test Product",
        feature_1="Feature 1",
        feature_2="Feature 2",
        feature_3="Feature 3",
        target_audience="Test Audience"
    )
    db.add(session)
    db.commit()

    # Add keyword and image
    keyword = SessionKeyword(session_id=session.id, keyword="test")
    image = ImageRecord(session_id=session.id, image_type=ImageTypeEnum.MAIN)
    db.add_all([keyword, image])
    db.commit()

    # Delete session
    db.delete(session)
    db.commit()

    # Verify cascade
    assert db.query(SessionKeyword).count() == 0
    assert db.query(ImageRecord).count() == 0


def test_status_enum_values(db):
    """Test that status enum values work correctly"""
    session = GenerationSession(
        upload_path="/test/path.png",
        product_title="Test Product",
        feature_1="Feature 1",
        feature_2="Feature 2",
        feature_3="Feature 3",
        target_audience="Test Audience"
    )
    db.add(session)
    db.commit()

    # Update status
    session.status = GenerationStatusEnum.PROCESSING
    db.commit()

    result = db.query(GenerationSession).first()
    assert result.status == GenerationStatusEnum.PROCESSING

    # Complete it
    session.status = GenerationStatusEnum.COMPLETE
    db.commit()

    result = db.query(GenerationSession).first()
    assert result.status == GenerationStatusEnum.COMPLETE
