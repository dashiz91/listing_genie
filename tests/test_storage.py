"""Tests for Supabase storage service with mocked client."""
import uuid
from io import BytesIO

import pytest
from PIL import Image

from app.config import settings
from app.services.supabase_storage_service import SupabaseStorageService


class FakeBucket:
    def __init__(self, name: str):
        self.name = name
        self.files = {}

    def upload(self, path, file, file_options=None):
        data = file.read() if hasattr(file, "read") else file
        self.files[path] = data
        return {"path": path}

    def update(self, path, file, file_options=None):
        data = file.read() if hasattr(file, "read") else file
        self.files[path] = data
        return {"path": path}

    def download(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)
        return self.files[path]

    def create_signed_url(self, path, expires_in=3600):
        if path not in self.files:
            raise FileNotFoundError(path)
        return {"signedURL": f"https://signed.test/{self.name}/{path}?exp={expires_in}"}

    def remove(self, paths):
        for path in paths:
            self.files.pop(path, None)

    def list(self, prefix=""):
        if not prefix:
            keys = list(self.files.keys())
        else:
            keys = [k for k in self.files if k.startswith(f"{prefix}/")]
        rows = []
        for path in keys:
            if prefix and path.startswith(f"{prefix}/"):
                name = path[len(prefix) + 1:]
            else:
                name = path
            rows.append({"name": name})
        return rows

    def get_public_url(self, path):
        return f"https://public.test/{self.name}/{path}"


class FakeStorageAPI:
    def __init__(self):
        self._buckets = {}

    def from_(self, name):
        if name not in self._buckets:
            self._buckets[name] = FakeBucket(name)
        return self._buckets[name]

    def list_buckets(self):
        return [type("Bucket", (), {"name": name})() for name in self._buckets]


class FakeSupabaseClient:
    def __init__(self):
        self.storage = FakeStorageAPI()


@pytest.fixture
def storage_service(monkeypatch):
    fake_client = FakeSupabaseClient()
    fake_client.storage.from_("uploads")
    fake_client.storage.from_("generated")

    monkeypatch.setattr(
        "app.services.supabase_storage_service.create_client",
        lambda url, key: fake_client,
    )
    monkeypatch.setattr(settings, "supabase_url", "https://example.supabase.co")
    monkeypatch.setattr(settings, "supabase_service_role_key", "service-role-key")
    monkeypatch.setattr(settings, "supabase_anon_key", "anon-key")
    monkeypatch.setattr(settings, "supabase_uploads_bucket", "uploads")
    monkeypatch.setattr(settings, "supabase_generated_bucket", "generated")

    service = SupabaseStorageService()
    return service, fake_client


@pytest.fixture
def test_image_bytes():
    image = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_save_upload_returns_uuid_and_supabase_path(storage_service, test_image_bytes):
    service, fake_client = storage_service
    upload_id, path = service.save_upload(test_image_bytes, "test.png")

    assert uuid.UUID(upload_id)
    assert path == f"supabase://uploads/{upload_id}.png"
    assert f"{upload_id}.png" in fake_client.storage.from_("uploads").files


def test_save_generated_image_versioned_saves_versioned_and_latest(storage_service):
    service, fake_client = storage_service
    image = Image.new("RGB", (200, 200), color="blue")

    path = service.save_generated_image_versioned("session-1", "main", image, version=3)
    generated = fake_client.storage.from_("generated").files

    assert path == "supabase://generated/session-1/main.png"
    assert "session-1/main_v3.png" in generated
    assert "session-1/main.png" in generated


def test_get_file_bytes_downloads_from_supabase(storage_service):
    service, fake_client = storage_service
    fake_client.storage.from_("generated").upload(
        "session-2/main.png",
        b"image-bytes",
        file_options={"content-type": "image/png"},
    )

    content = service.get_file_bytes("supabase://generated/session-2/main.png")
    assert content == b"image-bytes"


def test_get_session_image_count_counts_only_png(storage_service):
    service, fake_client = storage_service
    bucket = fake_client.storage.from_("generated")
    bucket.upload("session-3/main.png", b"x", file_options={"content-type": "image/png"})
    bucket.upload("session-3/notes.txt", b"y", file_options={"content-type": "text/plain"})
    bucket.upload("session-3/infographic_1.png", b"z", file_options={"content-type": "image/png"})

    assert service.get_session_image_count("session-3") == 2


def test_health_check_reports_accessible_when_buckets_exist(storage_service):
    service, _ = storage_service
    result = service.health_check()

    assert result["status"] == "accessible"
    assert result["provider"] == "supabase"
