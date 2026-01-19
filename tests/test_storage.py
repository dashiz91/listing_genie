"""Tests for storage service"""
import pytest
import tempfile
import shutil
from pathlib import Path
from PIL import Image
from io import BytesIO
from app.services.storage_service import StorageService


@pytest.fixture
def storage():
    """Create a temporary storage service for testing"""
    temp_dir = tempfile.mkdtemp()
    service = StorageService(storage_path=temp_dir)
    yield service
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_image_bytes():
    """Create test image bytes"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes.read()


def test_storage_creates_directories(storage):
    """Test that storage creates required directories"""
    assert storage.uploads_path.exists()
    assert storage.generated_path.exists()


def test_save_upload(storage, test_image_bytes):
    """Test saving an uploaded file"""
    upload_id, path = storage.save_upload(test_image_bytes, "test.png")

    assert upload_id is not None
    assert len(upload_id) == 36  # UUID length
    assert Path(path).exists()


def test_get_upload_path(storage, test_image_bytes):
    """Test retrieving upload path"""
    upload_id, _ = storage.save_upload(test_image_bytes, "test.png")

    path = storage.get_upload_path(upload_id)
    assert path.exists()
    assert path.suffix == ".png"


def test_get_upload_path_not_found(storage):
    """Test that missing upload raises error"""
    with pytest.raises(FileNotFoundError):
        storage.get_upload_path("nonexistent-id")


def test_save_generated_image(storage):
    """Test saving a generated image"""
    img = Image.new('RGB', (200, 200), color='blue')
    session_id = "test-session-123"

    path = storage.save_generated_image(session_id, "main", img)

    assert Path(path).exists()
    assert session_id in path
    assert "main.png" in path


def test_get_generated_path(storage):
    """Test retrieving generated image path"""
    img = Image.new('RGB', (200, 200), color='blue')
    session_id = "test-session-456"

    storage.save_generated_image(session_id, "lifestyle", img)
    path = storage.get_generated_path(session_id, "lifestyle")

    assert path.exists()


def test_get_generated_path_not_found(storage):
    """Test that missing generated image raises error"""
    with pytest.raises(FileNotFoundError):
        storage.get_generated_path("nonexistent", "main")


def test_delete_upload(storage, test_image_bytes):
    """Test deleting an uploaded file"""
    upload_id, path = storage.save_upload(test_image_bytes, "test.png")
    assert Path(path).exists()

    storage.delete_upload(upload_id)
    assert not Path(path).exists()


def test_delete_upload_idempotent(storage):
    """Test that deleting non-existent upload doesn't raise"""
    # Should not raise
    storage.delete_upload("nonexistent-id")


def test_delete_session_images(storage):
    """Test deleting all session images"""
    session_id = "delete-test-session"
    img = Image.new('RGB', (100, 100), color='green')

    # Create multiple images
    storage.save_generated_image(session_id, "main", img)
    storage.save_generated_image(session_id, "lifestyle", img)

    assert storage.get_session_image_count(session_id) == 2

    storage.delete_session_images(session_id)

    assert storage.get_session_image_count(session_id) == 0


def test_get_session_image_count(storage):
    """Test counting session images"""
    session_id = "count-test-session"
    img = Image.new('RGB', (100, 100), color='yellow')

    assert storage.get_session_image_count(session_id) == 0

    storage.save_generated_image(session_id, "main", img)
    assert storage.get_session_image_count(session_id) == 1

    storage.save_generated_image(session_id, "infographic_1", img)
    storage.save_generated_image(session_id, "infographic_2", img)
    assert storage.get_session_image_count(session_id) == 3


def test_health_check(storage):
    """Test storage health check"""
    result = storage.health_check()

    assert result["status"] == "accessible"
    assert result["writable"] is True


def test_image_reencoding_strips_metadata(storage):
    """Test that uploaded images are re-encoded"""
    # Create image with metadata
    img = Image.new('RGB', (100, 100), color='purple')
    img.info['test_metadata'] = 'should_be_stripped'

    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    upload_id, path = storage.save_upload(img_bytes.read(), "test.png")

    # Load saved image and check metadata is gone
    saved_img = Image.open(path)
    assert 'test_metadata' not in saved_img.info


def test_extension_normalization(storage, test_image_bytes):
    """Test that all extensions are normalized to PNG"""
    for filename in ["test.jpg", "test.jpeg", "test.PNG", "test.unknown"]:
        upload_id, path = storage.save_upload(test_image_bytes, filename)
        assert path.endswith(".png")
        storage.delete_upload(upload_id)
