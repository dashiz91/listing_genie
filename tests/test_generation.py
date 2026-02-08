"""
Tests for Image Generation API Endpoints
"""
import asyncio
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image
from urllib.parse import quote

from app.dependencies import get_storage_service
from app.main import app
from app.core.auth import User, get_current_user
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
    app.dependency_overrides[get_current_user] = lambda: User(
        id="user-test-123",
        email="test@example.com",
        role="authenticated",
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_storage_service, None)
        app.dependency_overrides.pop(get_current_user, None)
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

    def test_get_image_prompt_supports_desktop_mobile_tracks(self, client, sample_request):
        """A+ prompt endpoint should return track-scoped versions for desktop/mobile."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request, user_id="user-test-123")
            context = service.create_design_context(session)

            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "Desktop prompt v1")
            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "[MOBILE RECOMPOSE] Mobile prompt v1")
            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "Desktop prompt v2")

            desktop_resp = client.get(
                f"/api/generate/{session.id}/prompts/aplus_3",
                params={"track": "desktop", "version": 2},
            )
            assert desktop_resp.status_code == 200
            desktop_data = desktop_resp.json()
            assert desktop_data["prompt_text"] == "Desktop prompt v2"
            assert desktop_data["version"] == 2

            mobile_resp = client.get(
                f"/api/generate/{session.id}/prompts/aplus_3",
                params={"track": "mobile", "version": 1},
            )
            assert mobile_resp.status_code == 200
            mobile_data = mobile_resp.json()
            assert mobile_data["prompt_text"] == "[MOBILE RECOMPOSE] Mobile prompt v1"
            assert mobile_data["version"] == 1
        finally:
            db.close()


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

    @patch("app.services.vision_service.get_vision_service")
    def test_edit_aplus_uses_versioned_fallback_when_canonical_missing(
        self,
        mock_get_vision_service,
        client,
        sample_request,
    ):
        """Test A+ edit fallback to latest versioned image when canonical key is missing."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        vision = MagicMock()
        vision.plan_edit_instructions = AsyncMock(
            return_value={
                "interpretation": "Increase headline emphasis while preserving layout",
                "changes_made": ["Text emphasis update"],
                "edit_instructions": "Increase headline size and weight; keep all other elements unchanged.",
            }
        )
        mock_get_vision_service.return_value = vision

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
            applied_edit_instructions = gemini.edit_image.await_args.kwargs["edit_instructions"]
            assert source_path.endswith("/aplus_full_image_0_v3.png")
            assert "Increase headline size and weight" in applied_edit_instructions
            vision.plan_edit_instructions.assert_awaited_once()
            assert storage.saved_calls[0]["image_type"] == "aplus_full_image_0"
        finally:
            db.close()

    @patch("app.services.vision_service.get_vision_service")
    def test_regenerate_with_note_fails_when_ai_designer_unavailable(
        self,
        mock_get_vision_service,
        client,
        sample_request,
        mock_pil_image,
    ):
        """Regen with note must fail if AI Designer rewrite is unavailable."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        failing_vision = MagicMock()
        failing_vision.enhance_prompt_with_feedback = AsyncMock(
            side_effect=ValueError("Vision client not initialized")
        )
        mock_get_vision_service.return_value = failing_vision

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            gemini.generate_image = AsyncMock(return_value=mock_pil_image)
            storage = DummyStorageService()
            prompt_engine = MagicMock()
            prompt_engine.build_prompt.return_value = "Focus reference stress-test prompt."
            service = GenerationService(
                db=db,
                gemini=gemini,
                storage=storage,
                prompt_engine=prompt_engine,
            )

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            with pytest.raises(RuntimeError, match="AI Designer could not rewrite"):
                asyncio.run(
                    service.generate_single_image(
                        session=session,
                        image_type=DBImageTypeEnum.MAIN,
                        note="Make the scene brighter and cleaner.",
                    )
                )
            assert gemini.generate_image.await_count == 0
        finally:
            db.close()

    @patch("app.services.vision_service.get_vision_service")
    def test_regenerate_with_note_uses_ai_rewrite_without_raw_injection(
        self,
        mock_get_vision_service,
        client,
        sample_request,
        mock_pil_image,
    ):
        """Regen with feedback should use AI rewrite and avoid raw feedback injection."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        vision = MagicMock()
        vision.enhance_prompt_with_feedback = AsyncMock(
            return_value={
                "interpretation": "Removed banned wording and cleaned copy",
                "changes_made": ["Adjusted headline copy"],
                "enhanced_prompt": (
                    "A refined scene prompt without banned terms.\n\n"
                    "LIGHTING OVERRIDE: Old duplicate block from prior run."
                ),
            }
        )
        mock_get_vision_service.return_value = vision

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            gemini.generate_image = AsyncMock(return_value=mock_pil_image)
            storage = DummyStorageService()
            prompt_engine = MagicMock()
            prompt_engine.build_prompt.return_value = "Focus reference stress-test prompt."
            service = GenerationService(
                db=db,
                gemini=gemini,
                storage=storage,
                prompt_engine=prompt_engine,
            )

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            result = asyncio.run(
                service.generate_single_image(
                    session=session,
                    image_type=DBImageTypeEnum.MAIN,
                    note='Do not use the word "dopamine".',
                )
            )

            assert result.status.value == "complete"
            assert gemini.generate_image.await_count == 1
            sent_prompt = gemini.generate_image.await_args.kwargs["prompt"]
            assert "USER FEEDBACK TO APPLY" not in sent_prompt
            assert sent_prompt.lower().count("lighting override:") == 1

            rewrite_input = vision.enhance_prompt_with_feedback.await_args.kwargs["original_prompt"]
            assert "USER FEEDBACK TO APPLY" not in rewrite_input
            assert "lighting override:" not in rewrite_input.lower()
        finally:
            db.close()

    def test_generate_single_preflight_failure_does_not_mark_processing(self, client, sample_request):
        """If preflight prompt construction fails, image status must not get stuck in processing."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request)

            # Force a preflight failure before processing state is set.
            service.prompt_engine.build_prompt = MagicMock(side_effect=ValueError("preflight prompt failure"))

            with pytest.raises(ValueError, match="preflight prompt failure"):
                asyncio.run(
                    service.generate_single_image(
                        session=session,
                        image_type=DBImageTypeEnum.MAIN,
                        note=None,
                    )
                )

            main_record = next(img for img in session.images if img.image_type == DBImageTypeEnum.MAIN)
            assert main_record.status.value == "pending"
        finally:
            db.close()

    def test_paths_match_handles_encoded_proxy_urls(self):
        """Path matcher should align proxy URLs with raw storage paths."""
        from app.services.generation_service import GenerationService

        raw_path = "supabase://uploads/style-ref-123.png"
        proxy_path = f"/api/images/file?path={quote(raw_path, safe='')}"
        assert GenerationService._paths_match(raw_path, proxy_path)

    def test_generate_single_focus_refs_restores_style_prefix_and_semantic_labels(
        self,
        client,
        sample_request,
        mock_pil_image,
    ):
        """Focus-image generation should still identify style refs and additional product refs."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            gemini.generate_image = AsyncMock(return_value=mock_pil_image)
            storage = DummyStorageService()
            prompt_engine = MagicMock()
            prompt_engine.build_prompt.return_value = "Focus reference stress-test prompt."
            service = GenerationService(
                db=db,
                gemini=gemini,
                storage=storage,
                prompt_engine=prompt_engine,
            )

            payload = dict(sample_request)
            payload["additional_upload_paths"] = [
                "supabase://uploads/additional-a.png",
                "supabase://uploads/additional-b.png",
            ]
            payload["style_reference_path"] = "supabase://uploads/style-reference-main.png"
            payload["logo_path"] = "supabase://uploads/logo.png"
            request = GenerationRequest(**payload)
            session = service.create_session(request, user_id="user-test-123")
            service.create_design_context(session)

            style_proxy = f"/api/images/file?path={quote(session.style_reference_path, safe='')}"
            focus_refs = [
                session.upload_path,
                style_proxy,
                session.additional_upload_paths[0],
            ]

            result = asyncio.run(
                service.generate_single_image(
                    session=session,
                    image_type=DBImageTypeEnum.INFOGRAPHIC_1,
                    reference_image_paths=focus_refs,
                )
            )
            assert result.status.value == "complete"

            context = service.get_design_context(session.id)
            latest = service.get_latest_prompt(context, DBImageTypeEnum.INFOGRAPHIC_1)
            assert latest is not None
            assert "=== STYLE REFERENCE ===" in latest.prompt_text

            labels = [item.get("label") for item in (latest.reference_image_paths or [])]
            assert "STYLE_REFERENCE" in labels
            assert any((label or "").startswith("ADDITIONAL_PRODUCT_") for label in labels)
        finally:
            db.close()

    def test_aplus_prompt_history_can_filter_out_mobile_entries(self, client, sample_request):
        """Desktop prompt track should ignore mobile recomposition entries."""
        from app.services.generation_service import GenerationService
        from app.schemas.generation import GenerationRequest
        from app.models.database import ImageTypeEnum as DBImageTypeEnum

        db = SessionLocal()
        try:
            gemini = MagicMock()
            gemini.model = "gemini-test-model"
            storage = DummyStorageService()
            service = GenerationService(db=db, gemini=gemini, storage=storage)

            request = GenerationRequest(**sample_request)
            session = service.create_session(request, user_id="user-test-123")
            context = service.create_design_context(session)

            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "Desktop prompt v1")
            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "[MOBILE RECOMPOSE] Mobile prompt v1")
            service.store_prompt_in_history(context, DBImageTypeEnum.APLUS_3, "Desktop prompt v2")

            desktop_history = service.get_prompt_history(
                context,
                DBImageTypeEnum.APLUS_3,
                include_mobile=False,
            )
            assert [item.prompt_text for item in desktop_history] == [
                "Desktop prompt v1",
                "Desktop prompt v2",
            ]

            latest_desktop = service.get_latest_prompt(
                context,
                DBImageTypeEnum.APLUS_3,
                include_mobile=False,
            )
            assert latest_desktop is not None
            assert latest_desktop.prompt_text == "Desktop prompt v2"

            version_two_desktop = service.get_prompt_by_version(
                context,
                DBImageTypeEnum.APLUS_3,
                2,
                include_mobile=False,
            )
            assert version_two_desktop is not None
            assert version_two_desktop.prompt_text == "Desktop prompt v2"
        finally:
            db.close()


class TestEffectiveBrandResolution:
    """Tests for effective brand name resolution in A+ prompt generation."""

    def test_prefers_explicit_session_brand_when_not_product_title(self):
        from app.api.endpoints.generation import _resolve_effective_brand_name

        session = MagicMock()
        session.brand_name = "Nebula Colors"
        session.product_title = "Hanging Moon Planter"
        session.user_id = "user-1"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        resolved = _resolve_effective_brand_name(session, db, "user-1")
        assert resolved == "Nebula Colors"

    def test_uses_default_brand_when_session_brand_matches_product_title(self):
        from app.api.endpoints.generation import _resolve_effective_brand_name

        session = MagicMock()
        session.brand_name = "Hanging Moon Planter"
        session.product_title = "Hanging Moon Planter"
        session.user_id = "user-1"

        settings = MagicMock()
        settings.default_brand_name = "Nebula Colors"
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = settings

        resolved = _resolve_effective_brand_name(session, db, "user-1")
        assert resolved == "Nebula Colors"

    def test_treats_brand_as_unspecified_when_it_only_repeats_product_title(self):
        from app.api.endpoints.generation import _resolve_effective_brand_name

        session = MagicMock()
        session.brand_name = "Hanging Moon Planter"
        session.product_title = "Hanging Moon Planter"
        session.user_id = "user-1"

        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None

        resolved = _resolve_effective_brand_name(session, db, "user-1")
        assert resolved == ""


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
