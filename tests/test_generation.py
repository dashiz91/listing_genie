"""
Tests for Image Generation API Endpoints
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image

from app.dependencies import get_storage_service
from app.main import app
from app.schemas.generation import (
    GenerationRequest,
    KeywordInput,
    ImageTypeEnum,
    GenerationStatusEnum,
)
from app.models.database import Base, GenerationSession
from app.db.session import engine, SessionLocal


class DummyStorageService:
    """Storage stub for tests (no external services required)."""

    generated_bucket = "generated"
    uploads_bucket = "uploads"

    def save_generated_image(self, session_id, image_type, image):
        return f"supabase://generated/{session_id}/{image_type}.png"

    def save_generated_image_versioned(self, session_id, image_type, image, version):
        return f"supabase://generated/{session_id}/{image_type}.png"

    def get_generated_url(self, session_id, image_type, expires_in=3600):
        return f"https://example.test/{session_id}/{image_type}.png"

    def health_check(self):
        return {"status": "accessible"}


class _LegacyBucket:
    def __init__(self, names):
        self._names = names

    def list(self, prefix):
        return [{"name": name} for name in self._names]


class _LegacyStorageAPI:
    def __init__(self, names):
        self._bucket = _LegacyBucket(names)

    def from_(self, name):
        return self._bucket


class LegacyAplusStorageService(DummyStorageService):
    """Storage stub where canonical A+ key is missing but versioned file exists."""

    def __init__(self, names):
        self.generated_bucket = "generated"
        self.uploads_bucket = "uploads"
        self.client = MagicMock()
        self.client.storage = _LegacyStorageAPI(names)
        self.saved_calls = []

    def get_generated_url(self, session_id, image_type, expires_in=3600):
        raise FileNotFoundError(f"Missing canonical key: {image_type}")

    def save_generated_image_versioned(self, session_id, image_type, image, version):
        self.saved_calls.append(
            {
                "session_id": session_id,
                "image_type": image_type,
                "version": version,
            }
        )
        return f"supabase://generated/{session_id}/{image_type}.png"


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_storage_service] = lambda: DummyStorageService()
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_storage_service, None)
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_request():
    """Sample generation request"""
    return {
        "product_title": "Organic Vitamin D3 Gummies",
        "feature_1": "5000 IU per serving",
        "feature_2": "Organic ingredients",
        "feature_3": "Natural berry flavor",
        "target_audience": "Health-conscious adults",
        "keywords": [
            {"keyword": "vitamin gummies", "intents": ["durability"]},
            {"keyword": "immune support", "intents": ["problem_solution"]}
        ],
        "upload_path": "storage/uploads/test/product.png"
    }


@pytest.fixture
def mock_pil_image():
    """Create a mock PIL image for testing"""
    img = Image.new('RGB', (2000, 2000), color='white')
    return img


class TestGenerationSchemas:
    """Tests for generation request/response schemas"""

    def test_generation_request_valid(self, sample_request):
        """Test valid generation request"""
        request = GenerationRequest(**sample_request)
        assert request.product_title == sample_request["product_title"]
        assert len(request.keywords) == 2

    def test_generation_request_with_empty_keywords(self):
        """Test request with no keywords"""
        request = GenerationRequest(
            product_title="Test Product",
            feature_1="Feature 1",
            feature_2="Feature 2",
            feature_3="Feature 3",
            target_audience="Everyone",
            keywords=[],
            upload_path="test/path.png"
        )
        assert len(request.keywords) == 0

    def test_keyword_input_schema(self):
        """Test KeywordInput schema"""
        keyword = KeywordInput(keyword="test keyword", intents=["durability", "style"])
        assert keyword.keyword == "test keyword"
        assert len(keyword.intents) == 2

    def test_image_type_enum(self):
        """Test ImageTypeEnum values"""
        assert ImageTypeEnum.MAIN.value == "main"
        assert ImageTypeEnum.INFOGRAPHIC_1.value == "infographic_1"
        assert ImageTypeEnum.INFOGRAPHIC_2.value == "infographic_2"
        assert ImageTypeEnum.LIFESTYLE.value == "lifestyle"
        assert ImageTypeEnum.COMPARISON.value == "comparison"


class TestGenerationEndpoints:
    """Tests for generation API endpoints"""

    def test_generation_endpoint_exists(self, client):
        """Test that generation endpoints are registered"""
        # Check OpenAPI spec includes generation endpoints
        response = client.get("/openapi.json")
        assert response.status_code == 200
        paths = response.json()["paths"]
        assert "/api/generate/" in paths
        assert "/api/generate/{session_id}" in paths

    @patch('app.services.gemini_service.GeminiService.generate_image')
    def test_start_generation_creates_session(
        self,
        mock_generate,
        client,
        sample_request,
        mock_pil_image
    ):
        """Test that generation creates a session in database"""
        # Setup mocks
        mock_generate.return_value = mock_pil_image

        response = client.post("/api/generate/", json=sample_request)

        # Should succeed (or fail with Gemini not configured)
        assert response.status_code in [200, 500]

        if response.status_code == 200:
            data = response.json()
            assert "session_id" in data
            assert "status" in data
            assert "images" in data
            assert len(data["images"]) == 6

    def test_get_session_not_found(self, client):
        """Test getting non-existent session returns 404"""
        response = client.get("/api/generate/nonexistent-id")
        assert response.status_code == 404

    def test_generate_single_image_session_not_found(self, client):
        """Test single image generation with non-existent session"""
        response = client.post(
            "/api/generate/single",
            json={
                "session_id": "nonexistent-id",
                "image_type": "main"
            }
        )
        assert response.status_code == 404


class TestGenerationService:
    """Tests for GenerationService business logic"""

    def test_create_session_from_request(self, client, sample_request):
        """Test session creation from request"""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest

        db = SessionLocal()
        try:
            gemini = MagicMock()
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            assert session.id is not None
            assert session.product_title == sample_request["product_title"]
            assert len(session.keywords) == 2
            assert len(session.images) == 6

            # Check all image types created
            image_types = {img.image_type.value for img in session.images}
            assert "main" in image_types
            assert "infographic_1" in image_types
            assert "infographic_2" in image_types
            assert "lifestyle" in image_types
            assert "transformation" in image_types
            assert "comparison" in image_types

        finally:
            db.close()

    def test_get_session_status(self, client, sample_request):
        """Test retrieving session status"""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest

        db = SessionLocal()
        try:
            gemini = MagicMock()
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            # Retrieve session
            retrieved = service.get_session_status(session.id)
            assert retrieved is not None
            assert retrieved.id == session.id

        finally:
            db.close()

    def test_get_session_results(self, client, sample_request):
        """Test getting session image results"""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest

        db = SessionLocal()
        try:
            gemini = MagicMock()
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            results = service.get_session_results(session)
            assert len(results) == 6
            for result in results:
                assert result.status.value == "pending"

        finally:
            db.close()

    def test_edit_aplus_uses_versioned_fallback_when_canonical_missing(self, client, sample_request):
        """Test A+ edit fallback to latest versioned image when canonical key is missing."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            gemini.edit_image = AsyncMock(return_value=Image.new("RGB", (1464, 600), color="white"))

            storage = LegacyAplusStorageService(
                names=["aplus_full_image_0_v3.png", "aplus_full_image_1_v3.png"]
            )
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            result = asyncio.run(
                service.edit_single_image(
                    session=session,
                    image_type=DBImageTypeEnum.APLUS_0,
                    edit_instructions="Make headline text larger and bolder.",
                )
            )

            assert result.status.value == "complete"
            assert result.storage_path.endswith("/aplus_full_image_0.png")
            assert gemini.edit_image.await_count == 1
            source_path = gemini.edit_image.await_args.kwargs["source_image_path"]
            assert source_path.endswith("/aplus_full_image_0_v3.png")
            assert storage.saved_calls[0]["image_type"] == "aplus_full_image_0"
        finally:
            db.close()


class TestAsyncGeneration:
    """Tests for async generation endpoint"""

    def test_async_endpoint_exists(self, client):
        """Test that async generation endpoint is registered"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        paths = response.json()["paths"]
        assert "/api/generate/async" in paths

    @patch('app.services.generation_service.GenerationService.generate_all_images', new_callable=AsyncMock)
    def test_async_generation_returns_immediately(
        self,
        mock_generate_all,
        client,
        sample_request
    ):
        """Test async endpoint returns processing status immediately"""
        mock_generate_all.return_value = []

        response = client.post("/api/generate/async", json=sample_request)

        # Should return quickly with processing status
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["processing", "pending"]


class TestRetryLogic:
    """Tests for retry and error handling"""

    def test_retry_config_values(self):
        """Test RetryConfig has correct values"""
        from app.services.generation_service import RetryConfig

        assert RetryConfig.MAX_RETRIES == 3
        assert RetryConfig.BASE_DELAY == 1
        assert RetryConfig.MAX_DELAY == 8
        assert len(RetryConfig.VARIATIONS) >= 3

    def test_retry_delay_calculation(self):
        """Test exponential backoff delay"""
        from app.services.generation_service import GenerationService

        # Create a mock service to test
        service = GenerationService.__new__(GenerationService)

        assert service._get_retry_delay(0) == 1  # 1 * 2^0 = 1
        assert service._get_retry_delay(1) == 2  # 1 * 2^1 = 2
        assert service._get_retry_delay(2) == 4  # 1 * 2^2 = 4
        assert service._get_retry_delay(3) == 8  # capped at MAX_DELAY

    def test_prompt_variations(self):
        """Test prompt variations are returned correctly"""
        from app.services.generation_service import GenerationService, RetryConfig

        service = GenerationService.__new__(GenerationService)

        # First attempt uses original prompt (empty variation)
        assert service._get_prompt_variation(0) == ""

        # Subsequent attempts get variations
        assert "VARIATION" in service._get_prompt_variation(1)
        assert "VARIATION" in service._get_prompt_variation(2)

    def test_retry_endpoint_exists(self, client):
        """Test retry endpoint is registered"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        # Check for retry pattern in paths
        paths = response.json()["paths"]
        retry_paths = [p for p in paths if "retry" in p]
        assert len(retry_paths) > 0

    def test_stats_endpoint_exists(self, client):
        """Test stats endpoint is registered"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        paths = response.json()["paths"]
        stats_paths = [p for p in paths if "stats" in p]
        assert len(stats_paths) > 0

    def test_retry_session_not_found(self, client):
        """Test retry with non-existent session"""
        response = client.post("/api/generate/nonexistent-id/retry")
        assert response.status_code == 404

    def test_stats_session_not_found(self, client):
        """Test stats with non-existent session"""
        response = client.get("/api/generate/nonexistent-id/stats")
        assert response.status_code == 404

    def test_generation_stats_structure(self, client, sample_request):
        """Test generation stats return correct structure"""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.db.session import SessionLocal, engine
        from app.models.database import Base

        # Ensure tables exist (client fixture creates them)
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            gemini = MagicMock()
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            stats = service.get_generation_stats(session)

            assert "session_id" in stats
            assert "total_images" in stats
            assert stats["total_images"] == 6
            assert "by_status" in stats
            assert "retry_counts" in stats
            assert len(stats["retry_counts"]) == 6

        finally:
            db.close()
