"""
Integration tests for the batch generation worker.

These tests verify the two critical bugs that caused batch generation to fail:
1. DB SESSION LIFECYCLE: The worker must create its own DB session because
   FastAPI's get_db() yield closes the request-scoped session after the
   response is sent — before the background worker even starts.
2. SEQUENTIAL EXECUTION: Images must generate sequentially because synchronous
   _load_image_from_path calls block the event loop, causing Railway health
   check failures and process kills when run concurrently.
3. STATUS TRANSITIONS: Images must start as PROCESSING (not PENDING) so the
   first poll shows spinners, and always reach a terminal state so polling stops.
"""
import asyncio
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image

from app.db.session import engine, SessionLocal
from app.models.database import (
    Base,
    GenerationSession,
    ImageRecord,
    GenerationStatusEnum as DBStatus,
    ImageTypeEnum as DBImageType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db():
    """Fresh in-memory database for each test."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def mock_pil_image():
    return Image.new("RGB", (1024, 1024), color="white")


def _create_test_session(db, image_types=None, status=DBStatus.PROCESSING):
    """Helper: create a GenerationSession with ImageRecords in the DB."""
    if image_types is None:
        image_types = [
            DBImageType.MAIN,
            DBImageType.INFOGRAPHIC_1,
            DBImageType.INFOGRAPHIC_2,
            DBImageType.LIFESTYLE,
            DBImageType.TRANSFORMATION,
            DBImageType.COMPARISON,
        ]

    session = GenerationSession(
        id=str(uuid.uuid4()),
        user_id="user-test-batch",
        status=status,
        upload_path="supabase://uploads/test/product.png",
        product_title="Test Batch Product",
    )
    db.add(session)

    for img_type in image_types:
        db.add(ImageRecord(
            session_id=session.id,
            image_type=img_type,
            status=DBStatus.PROCESSING,
        ))
    db.commit()
    return session


# ---------------------------------------------------------------------------
# Test 1: DB session lifecycle — worker must survive after request DB closes
# ---------------------------------------------------------------------------

class TestBatchWorkerDBLifecycle:
    """The batch worker creates its own DB session, not the request-scoped one."""

    def test_worker_creates_own_db_session(self, db, mock_pil_image):
        """
        Simulate what FastAPI does: close the request DB session, then run
        the worker. If the worker relies on the closed session, it will crash.
        """
        session = _create_test_session(db)
        session_id = session.id
        image_types = [DBImageType.MAIN]

        # Close the request-scoped DB (simulates FastAPI's yield cleanup)
        db.close()

        # Mock the Gemini API so we don't make real calls
        mock_gemini = MagicMock()
        mock_gemini.model = "gemini-test"
        mock_gemini.generate_image = AsyncMock(return_value=mock_pil_image)

        mock_storage = MagicMock()
        mock_storage.save_generated_image = MagicMock(
            return_value="supabase://generated/test/main.png"
        )
        mock_storage.save_generated_image_versioned = MagicMock(
            return_value="supabase://generated/test/main.png"
        )

        with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
             patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
            from app.api.endpoints.generation import _batch_generate_worker
            asyncio.run(_batch_generate_worker(
                session_id=session_id,
                image_types=image_types,
                image_model="gemini-test",
                user_id="user-test-batch",
                user_email="test@test.com",
            ))

        # Verify: open a fresh DB session and check the session reached terminal state
        check_db = SessionLocal()
        try:
            result_session = check_db.query(GenerationSession).filter(
                GenerationSession.id == session_id
            ).first()
            assert result_session is not None, "Session should exist in DB"
            assert result_session.status != DBStatus.PROCESSING, \
                f"Session should not be stuck in PROCESSING, got {result_session.status}"
            assert result_session.status in (DBStatus.COMPLETE, DBStatus.PARTIAL, DBStatus.FAILED), \
                f"Session should reach terminal state, got {result_session.status}"
        finally:
            check_db.close()

    def test_worker_handles_missing_session(self):
        """Worker should log error and return cleanly if session doesn't exist."""
        Base.metadata.create_all(bind=engine)
        try:
            from app.api.endpoints.generation import _batch_generate_worker

            mock_gemini = MagicMock()
            mock_storage = MagicMock()

            with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
                 patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
                # Should not raise — just log and return
                asyncio.run(_batch_generate_worker(
                    session_id="nonexistent-session-id",
                    image_types=[DBImageType.MAIN],
                    image_model=None,
                    user_id="test",
                    user_email=None,
                ))
        finally:
            Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Test 2: Status transitions — all images must reach terminal state
# ---------------------------------------------------------------------------

class TestBatchStatusTransitions:
    """Images must always end in a terminal state so polling can stop."""

    def test_successful_generation_sets_complete(self, db, mock_pil_image):
        """When all images succeed, session status = COMPLETE."""
        image_types = [DBImageType.MAIN, DBImageType.INFOGRAPHIC_1]
        session = _create_test_session(db, image_types=image_types)
        session_id = session.id
        db.close()

        mock_gemini = MagicMock()
        mock_gemini.model = "gemini-test"
        mock_gemini.generate_image = AsyncMock(return_value=mock_pil_image)

        mock_storage = MagicMock()
        mock_storage.save_generated_image = MagicMock(
            return_value="supabase://generated/test/img.png"
        )
        mock_storage.save_generated_image_versioned = MagicMock(
            return_value="supabase://generated/test/img.png"
        )

        with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
             patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
            from app.api.endpoints.generation import _batch_generate_worker
            asyncio.run(_batch_generate_worker(
                session_id=session_id,
                image_types=image_types,
                image_model="gemini-test",
                user_id="user-test-batch",
                user_email="test@test.com",
            ))

        check_db = SessionLocal()
        try:
            result = check_db.query(GenerationSession).get(session_id)
            assert result.status == DBStatus.COMPLETE, \
                f"All images succeeded → session should be COMPLETE, got {result.status}"

            for img in result.images:
                assert img.status == DBStatus.COMPLETE, \
                    f"Image {img.image_type} should be COMPLETE, got {img.status}"
        finally:
            check_db.close()

    def test_failed_generation_reaches_terminal(self, db):
        """When generation fails, images get FAILED and session reaches terminal."""
        image_types = [DBImageType.MAIN, DBImageType.LIFESTYLE]
        session = _create_test_session(db, image_types=image_types)
        session_id = session.id
        db.close()

        mock_gemini = MagicMock()
        mock_gemini.model = "gemini-test"
        # Simulate Gemini API failure
        mock_gemini.generate_image = AsyncMock(side_effect=RuntimeError("API error"))

        mock_storage = MagicMock()

        with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
             patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
            from app.api.endpoints.generation import _batch_generate_worker
            asyncio.run(_batch_generate_worker(
                session_id=session_id,
                image_types=image_types,
                image_model=None,
                user_id="user-test-batch",
                user_email=None,
            ))

        check_db = SessionLocal()
        try:
            result = check_db.query(GenerationSession).get(session_id)
            assert result.status in (DBStatus.FAILED, DBStatus.PARTIAL), \
                f"Failed generation should reach FAILED/PARTIAL, got {result.status}"
            assert result.status != DBStatus.PROCESSING, \
                "Session MUST NOT stay stuck in PROCESSING"
        finally:
            check_db.close()

    def test_partial_failure_reaches_terminal(self, db, mock_pil_image):
        """When some images succeed and some fail, session = PARTIAL."""
        image_types = [DBImageType.MAIN, DBImageType.LIFESTYLE]
        session = _create_test_session(db, image_types=image_types)
        session_id = session.id
        db.close()

        call_count = 0

        async def _succeed_then_fail(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_pil_image  # First image succeeds
            raise RuntimeError("Simulated failure")  # Second image fails

        mock_gemini = MagicMock()
        mock_gemini.model = "gemini-test"
        mock_gemini.generate_image = AsyncMock(side_effect=_succeed_then_fail)

        mock_storage = MagicMock()
        mock_storage.save_generated_image = MagicMock(
            return_value="supabase://generated/test/img.png"
        )
        mock_storage.save_generated_image_versioned = MagicMock(
            return_value="supabase://generated/test/img.png"
        )

        with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
             patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
            from app.api.endpoints.generation import _batch_generate_worker
            asyncio.run(_batch_generate_worker(
                session_id=session_id,
                image_types=image_types,
                image_model="gemini-test",
                user_id="user-test-batch",
                user_email=None,
            ))

        check_db = SessionLocal()
        try:
            result = check_db.query(GenerationSession).get(session_id)
            assert result.status == DBStatus.PARTIAL, \
                f"Mix of success+failure should be PARTIAL, got {result.status}"
        finally:
            check_db.close()


# ---------------------------------------------------------------------------
# Test 3: Batch endpoint sets PROCESSING (not PENDING) for immediate spinners
# ---------------------------------------------------------------------------

class TestBatchEndpointStatus:
    """The batch endpoint must set images to PROCESSING before returning."""

    def test_batch_endpoint_sets_processing_not_pending(self, db):
        """
        Images should be PROCESSING after the batch endpoint returns,
        so the first poll shows spinners (not idle pending state).
        """
        from app.api.endpoints.generation import generate_batch
        from app.schemas.generation import BatchGenerateRequest
        from app.models.database import GenerationStatusEnum as DBStatus

        # Create session with PENDING images (default state)
        session = _create_test_session(db, status=DBStatus.PENDING)
        for img in session.images:
            img.status = DBStatus.PENDING
        db.commit()

        # Verify precondition: images start as PENDING
        for img in session.images:
            assert img.status == DBStatus.PENDING

        # Read the batch endpoint source to verify the status transition
        # (This is a code-level assertion, not a runtime test, because the
        # endpoint also spawns a background task we can't easily intercept)
        from app.api.endpoints.generation import generate_batch
        import inspect
        source = inspect.getsource(generate_batch)
        assert "DBStatus.PROCESSING" in source, \
            "Batch endpoint must set images to PROCESSING, not PENDING"
        assert "DBStatus.PENDING" not in source or "not PENDING" in source, \
            "Batch endpoint should not set images to PENDING"


# ---------------------------------------------------------------------------
# Test 4: Sequential execution — generation order is preserved
# ---------------------------------------------------------------------------

class TestBatchSequentialExecution:
    """
    Images must generate sequentially (not concurrent asyncio.gather)
    to avoid blocking the event loop with synchronous Supabase downloads.
    """

    def test_images_generate_sequentially(self, db, mock_pil_image):
        """
        Verify images are generated one at a time by tracking call order.
        With concurrent execution, start times would overlap.
        """
        image_types = [DBImageType.MAIN, DBImageType.INFOGRAPHIC_1, DBImageType.INFOGRAPHIC_2]
        session = _create_test_session(db, image_types=image_types)
        session_id = session.id
        db.close()

        generation_order = []

        async def _track_order(*args, **kwargs):
            # Record which image type is being generated
            # args[0] is session, args[1] is image_type
            img_type = args[1] if len(args) > 1 else kwargs.get("image_type")
            generation_order.append(("start", img_type))
            await asyncio.sleep(0.01)  # Simulate async work
            generation_order.append(("end", img_type))
            return mock_pil_image

        mock_gemini = MagicMock()
        mock_gemini.model = "gemini-test"
        mock_gemini.generate_image = AsyncMock(side_effect=_track_order)

        mock_storage = MagicMock()
        mock_storage.save_generated_image = MagicMock(
            return_value="supabase://generated/test/img.png"
        )
        mock_storage.save_generated_image_versioned = MagicMock(
            return_value="supabase://generated/test/img.png"
        )

        with patch("app.api.endpoints.generation.GeminiService", return_value=mock_gemini), \
             patch("app.api.endpoints.generation.get_storage_service", return_value=mock_storage):
            from app.api.endpoints.generation import _batch_generate_worker
            asyncio.run(_batch_generate_worker(
                session_id=session_id,
                image_types=image_types,
                image_model="gemini-test",
                user_id="user-test-batch",
                user_email=None,
            ))

        # With sequential execution: start1, end1, start2, end2, start3, end3
        # With concurrent execution: start1, start2, start3, end1, end2, end3
        # Verify sequential: each "end" comes before the next "start"
        for i in range(0, len(generation_order) - 2, 2):
            assert generation_order[i][0] == "start", \
                f"Expected 'start' at index {i}, got {generation_order[i]}"
            assert generation_order[i + 1][0] == "end", \
                f"Expected 'end' at index {i+1}, got {generation_order[i+1]}"

    def test_worker_source_has_no_asyncio_gather(self):
        """
        Code-level guard: the batch worker must NOT use asyncio.gather,
        which would run tasks concurrently and block the event loop.
        """
        from app.api.endpoints.generation import _batch_generate_worker
        import inspect
        source = inspect.getsource(_batch_generate_worker)
        assert "asyncio.gather" not in source, \
            "Batch worker must NOT use asyncio.gather — sequential execution only"


# ---------------------------------------------------------------------------
# Test 5: Worker function signature takes primitives, not DI objects
# ---------------------------------------------------------------------------

class TestBatchWorkerSignature:
    """The worker must accept primitive args, not request-scoped DI objects."""

    def test_worker_takes_session_id_not_session_object(self):
        """Worker should accept session_id (str), not a GenerationSession object."""
        from app.api.endpoints.generation import _batch_generate_worker
        import inspect
        sig = inspect.signature(_batch_generate_worker)
        params = list(sig.parameters.keys())

        assert "session_id" in params, \
            "Worker should accept 'session_id' (str), not a session object"
        assert "service" not in params, \
            "Worker should NOT accept 'service' — it creates its own"
        assert "credits" not in params, \
            "Worker should NOT accept 'credits' — it creates its own"

    def test_worker_creates_sessionlocal(self):
        """Worker source must create its own SessionLocal() for DB access."""
        from app.api.endpoints.generation import _batch_generate_worker
        import inspect
        source = inspect.getsource(_batch_generate_worker)
        assert "SessionLocal()" in source, \
            "Worker must create its own DB session via SessionLocal()"
        assert "db.close()" in source, \
            "Worker must close its DB session in finally block"
