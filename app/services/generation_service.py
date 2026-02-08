"""
Image Generation Service
Orchestrates prompt building, image generation, and storage with robust error handling
"""
import asyncio
import logging
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse
from sqlalchemy.orm import Session

from app.models.database import (
    GenerationSession,
    SessionKeyword,
    ImageRecord,
    GenerationStatusEnum,
    ImageTypeEnum,
    DesignContext,
    PromptHistory,
    ColorModeEnum,
)
from app.prompts import PromptEngine, ProductContext, get_prompt_engine, get_all_styles
from app.services.gemini_service import (
    GeminiService,
    append_lighting_override_once,
    strip_lighting_override,
)
from app.services.supabase_storage_service import SupabaseStorageService
from app.schemas.generation import (
    GenerationRequest,
    StylePreviewRequest,
    StylePreviewResult,
    ImageResult,
    GenerationStatusEnum as SchemaStatus,
    ImageTypeEnum as SchemaImageType,
    DesignFramework,
)
# Note: VisionService provider is resolved dynamically at runtime.

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuration for retry behavior"""
    MAX_RETRIES = 3
    BASE_DELAY = 1  # seconds
    MAX_DELAY = 8   # seconds

    # Prompt variations to try on retry
    VARIATIONS = [
        "",  # First attempt uses original prompt
        "\n\n[VARIATION: Emphasize clarity and simplicity. Use clean lines and minimal elements.]",
        "\n\n[VARIATION: Focus on product detail and precision. Showcase texture and quality.]",
        "\n\n[VARIATION: Prioritize clean composition. Ensure strong visual hierarchy.]",
    ]


class GenerationService:
    """Orchestrates the full image generation pipeline with robust error handling"""

    IMAGE_TYPES = [
        ImageTypeEnum.MAIN,
        ImageTypeEnum.INFOGRAPHIC_1,
        ImageTypeEnum.INFOGRAPHIC_2,
        ImageTypeEnum.LIFESTYLE,
        ImageTypeEnum.TRANSFORMATION,  # New: Before/After life state (image 5)
        ImageTypeEnum.COMPARISON,      # FOMO closing image (now image 6)
    ]

    def __init__(
        self,
        db: Session,
        gemini: GeminiService,
        storage: SupabaseStorageService,
        prompt_engine: PromptEngine = None,
    ):
        self.db = db
        self.gemini = gemini
        self.storage = storage
        self.prompt_engine = prompt_engine or get_prompt_engine()
        # Store framework for current session (set during create_session)
        self._current_framework: Optional[DesignFramework] = None

    @staticmethod
    def _strip_style_reference_prefix(prompt: str) -> str:
        """Remove generated style-reference header block so it is not duplicated."""
        if not prompt:
            return prompt
        trimmed = prompt.lstrip()
        if not trimmed.startswith("=== STYLE REFERENCE ==="):
            return prompt
        split_idx = trimmed.find("\n\n")
        if split_idx == -1:
            return prompt
        return trimmed[split_idx + 2:].lstrip()

    @staticmethod
    def _strip_feedback_injection_block(prompt: str) -> str:
        """Remove legacy direct-feedback injection block from a prompt."""
        if not prompt:
            return prompt
        marker = "=== USER FEEDBACK TO APPLY ==="
        idx = prompt.find(marker)
        if idx == -1:
            return prompt
        return prompt[:idx].rstrip()

    @classmethod
    def _sanitize_prompt_for_rewrite(cls, prompt: Optional[str]) -> str:
        """
        Remove system wrappers before sending prior prompt to AI Designer.

        This keeps the rewrite focused on the actual scene/copy instructions.
        """
        cleaned = (prompt or "").strip()
        cleaned = cls._strip_feedback_injection_block(cleaned)
        cleaned = strip_lighting_override(cleaned)
        cleaned = cls._strip_style_reference_prefix(cleaned)
        return cleaned.strip()

    @staticmethod
    def _normalize_image_path(path: Optional[str]) -> str:
        """Normalize image path variants for reliable matching."""
        if not path:
            return ""

        normalized = str(path).strip().strip('"').strip("'")
        if not normalized:
            return ""

        try:
            parsed = urlparse(normalized)
            query = parse_qs(parsed.query)
            encoded_path = query.get("path", [None])[0]
            if encoded_path:
                normalized = unquote(encoded_path)
            elif parsed.scheme in ("http", "https"):
                normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            normalized = normalized.split("?", 1)[0]

        return unquote(normalized).strip()

    @classmethod
    def _extract_image_filename(cls, path: Optional[str]) -> str:
        normalized = cls._normalize_image_path(path)
        if not normalized:
            return ""
        no_query = normalized.split("?", 1)[0].split("#", 1)[0]
        return no_query.rstrip("/").rsplit("/", 1)[-1]

    @classmethod
    def _paths_match(cls, left: Optional[str], right: Optional[str]) -> bool:
        """Best-effort path equality across signed URLs, encoded API paths, and raw storage paths."""
        left_norm = cls._normalize_image_path(left)
        right_norm = cls._normalize_image_path(right)
        if not left_norm or not right_norm:
            return False

        if left_norm == right_norm:
            return True

        left_no_query = left_norm.split("?", 1)[0].split("#", 1)[0]
        right_no_query = right_norm.split("?", 1)[0].split("#", 1)[0]
        if left_no_query == right_no_query:
            return True

        if left_no_query.endswith(right_no_query) or right_no_query.endswith(left_no_query):
            return True

        left_filename = cls._extract_image_filename(left_no_query)
        right_filename = cls._extract_image_filename(right_no_query)
        return bool(left_filename and right_filename and left_filename == right_filename)

    @staticmethod
    def _is_mobile_prompt_text(prompt_text: Optional[str]) -> bool:
        """Identify prompt-history entries that belong to mobile A+ operations."""
        if not prompt_text:
            return False
        normalized = prompt_text.lstrip()
        return (
            normalized.startswith("[MOBILE RECOMPOSE]")
            or normalized.startswith("[HERO MOBILE MERGE]")
            or normalized.startswith("[MOBILE EDIT]")
        )

    @staticmethod
    def _is_mobile_storage_key(storage_key: Optional[str]) -> bool:
        if not storage_key:
            return False
        key = storage_key.lower()
        return key.endswith("_mobile") or "_mobile_" in key or "hero_mobile" in key

    def create_session(self, request: GenerationRequest, user_id: Optional[str] = None) -> GenerationSession:
        """
        Create a new generation session with all image records.

        Args:
            request: Generation request with product details
            user_id: Optional Supabase user ID (from authenticated request)

        Returns:
            Created GenerationSession object
        """
        # Store the design framework if provided (MASTER level)
        if request.design_framework:
            self._current_framework = request.design_framework
            logger.info(f"Using MASTER level framework: {request.design_framework.framework_name}")

        # Create session
        session = GenerationSession(
            user_id=user_id,  # Associate with authenticated user
            upload_path=request.upload_path,
            additional_upload_paths=request.additional_upload_paths or [],
            product_title=request.product_title,
            feature_1=request.feature_1,
            feature_2=request.feature_2,
            feature_3=request.feature_3,
            target_audience=request.target_audience,
            brand_name=request.brand_name,
            brand_colors=request.brand_colors or [],
            logo_path=request.logo_path,
            style_id=request.style_id,
            # MASTER Level: Brand vibe for creative brief system
            brand_vibe=request.brand_vibe.value if request.brand_vibe else None,
            primary_color=request.primary_color,
            style_reference_path=request.style_reference_path,
            color_count=request.color_count,
            color_palette=request.color_palette or [],
            status=GenerationStatusEnum.PENDING,
            # Store framework as JSON if provided
            design_framework_json=request.design_framework.model_dump() if request.design_framework else None,
            # Global note/instructions for all images
            global_note=request.global_note,
        )
        self.db.add(session)
        self.db.flush()  # Get ID

        # Add keywords
        for kw in request.keywords:
            keyword = SessionKeyword(
                session_id=session.id,
                keyword=kw.keyword,
                intent_types=kw.intents,
            )
            self.db.add(keyword)

        # Create image records for each type
        for image_type in self.IMAGE_TYPES:
            image_record = ImageRecord(
                session_id=session.id,
                image_type=image_type,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)

        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Created generation session: {session.id}")
        return session

    def create_design_context(
        self,
        session: GenerationSession,
        color_mode: ColorModeEnum = ColorModeEnum.AI_DECIDES,
        locked_colors: Optional[List[str]] = None,
        product_analysis: Optional[Dict] = None,
        original_style_reference_path: Optional[str] = None,
    ) -> DesignContext:
        """
        Create a DesignContext for AI Designer memory.

        This enables the AI Designer to remember:
        - What prompts it generated
        - What framework was selected
        - User feedback and regeneration history
        - Product analysis from initial vision (for regeneration context)

        Args:
            session: The generation session
            color_mode: How colors should be determined
            locked_colors: Specific hex colors if mode is LOCKED_PALETTE
            product_analysis: AI's analysis of the product from framework generation
            original_style_reference_path: User's original style reference upload (if different from framework preview)

        Returns:
            Created DesignContext
        """
        # Check if context already exists
        existing = self.db.query(DesignContext).filter(
            DesignContext.session_id == session.id
        ).first()

        if existing:
            logger.info(f"DesignContext already exists for session {session.id}")
            return existing

        # Build image inventory from session
        image_inventory = []
        if session.upload_path:
            image_inventory.append({
                "type": "primary",
                "path": session.upload_path,
                "description": "Primary product photo"
            })

        if session.additional_upload_paths:
            for i, path in enumerate(session.additional_upload_paths):
                image_inventory.append({
                    "type": f"additional_{i+1}",
                    "path": path,
                    "description": f"Additional product photo {i+1}"
                })

        # Track both the original user upload AND the framework preview used for generation
        if original_style_reference_path:
            image_inventory.append({
                "type": "original_style_reference",
                "path": original_style_reference_path,
                "description": "User's original style reference image"
            })

        if session.style_reference_path:
            image_inventory.append({
                "type": "style_reference",
                "path": session.style_reference_path,
                "description": "Style reference image used for generation"
            })

        if session.logo_path:
            image_inventory.append({
                "type": "logo",
                "path": session.logo_path,
                "description": "Brand logo"
            })

        # Create context
        context = DesignContext(
            session_id=session.id,
            image_inventory=image_inventory,
            color_mode=color_mode,
            locked_colors=locked_colors or [],
            product_analysis=product_analysis,  # Store AI's analysis for regeneration context
        )

        # Store selected framework info if available
        if session.design_framework_json:
            fw = session.design_framework_json
            context.selected_framework_id = fw.get('framework_id')
            context.selected_framework_name = fw.get('framework_name')

        if product_analysis:
            logger.info(f"Storing product_analysis in DesignContext for session {session.id}")

        self.db.add(context)
        self.db.commit()
        self.db.refresh(context)

        logger.info(f"Created DesignContext for session {session.id}")
        return context

    def get_design_context(self, session_id: str) -> Optional[DesignContext]:
        """Get the DesignContext for a session"""
        return self.db.query(DesignContext).filter(
            DesignContext.session_id == session_id
        ).first()

    def store_prompt_in_history(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum,
        prompt_text: str,
        user_feedback: Optional[str] = None,
        change_summary: Optional[str] = None,
        reference_image_paths: Optional[List[Dict]] = None,
        model_name: Optional[str] = None,
    ) -> PromptHistory:
        """
        Store a prompt in the history for future reference.

        This enables AI Designer to see what it wrote before when regenerating.

        Args:
            context: The DesignContext
            image_type: Which image type this prompt is for
            prompt_text: The actual prompt sent to image generator
            user_feedback: User feedback that triggered this version (null for v1)
            change_summary: AI's interpretation of changes made
            reference_image_paths: Actual reference images passed to generation
                Format: [{"type": "primary", "path": "..."}, {"type": "previous_module", "path": "..."}]

        Returns:
            Created PromptHistory record
        """
        # Get current max version for this image type
        max_version = self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).count()

        new_version = max_version + 1

        history = PromptHistory(
            context_id=context.id,
            image_type=image_type,
            version=new_version,
            prompt_text=prompt_text,
            user_feedback=user_feedback,
            change_summary=change_summary,
            reference_image_paths=reference_image_paths,
            model_name=model_name,
        )

        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)

        logger.info(f"Stored prompt v{new_version} for {image_type.value} in history")
        return history

    def get_latest_prompt(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum,
        include_mobile: bool = True,
    ) -> Optional[PromptHistory]:
        """Get the most recent prompt for an image type"""
        query = self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).order_by(PromptHistory.version.desc())
        if include_mobile:
            return query.first()

        for item in query.all():
            if not self._is_mobile_prompt_text(item.prompt_text):
                return item
        return None

    def get_prompt_by_version(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum,
        version: int,
        include_mobile: bool = True,
    ) -> Optional[PromptHistory]:
        """Get a specific version's prompt for an image type"""
        if include_mobile:
            return self.db.query(PromptHistory).filter(
                PromptHistory.context_id == context.id,
                PromptHistory.image_type == image_type,
                PromptHistory.version == version
            ).first()

        history = self.get_prompt_history(
            context=context,
            image_type=image_type,
            include_mobile=False,
        )
        if version < 1 or version > len(history):
            return None
        return history[version - 1]

    def get_prompt_history(
        self,
        context: DesignContext,
        image_type: ImageTypeEnum,
        include_mobile: bool = True,
        mobile_only: bool = False,
    ) -> List[PromptHistory]:
        """Get all prompt versions for an image type"""
        history = self.db.query(PromptHistory).filter(
            PromptHistory.context_id == context.id,
            PromptHistory.image_type == image_type
        ).order_by(PromptHistory.version.asc()).all()
        if mobile_only:
            return [item for item in history if self._is_mobile_prompt_text(item.prompt_text)]
        if include_mobile:
            return history
        return [item for item in history if not self._is_mobile_prompt_text(item.prompt_text)]

    def _build_product_context(
        self,
        session: GenerationSession,
        style_override: Optional[str] = None
    ) -> ProductContext:
        """Build ProductContext from session data"""
        # Convert keywords to dict format for PromptEngine
        keyword_intents: Dict[str, List[str]] = {}
        keywords: List[str] = []

        for kw in session.keywords:
            keywords.append(kw.keyword)
            keyword_intents[kw.keyword] = kw.intent_types or []

        # Filter out None features
        features = [f for f in [session.feature_1, session.feature_2, session.feature_3] if f]

        return ProductContext(
            title=session.product_title,
            features=features,
            target_audience=session.target_audience or "",
            keywords=keywords,
            intents=keyword_intents,
            brand_colors=session.brand_colors or [],
            brand_name=session.brand_name,
            has_logo=bool(session.logo_path),
            style_id=style_override or session.style_id,
            # MASTER Level: Brand vibe for creative brief system
            brand_vibe=session.brand_vibe,
            primary_color=session.primary_color,
            has_style_reference=bool(session.style_reference_path),
            color_count=session.color_count,
            color_palette=session.color_palette or [],
        )

    def _build_framework_prompt(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum
    ) -> str:
        """
        Build a prompt for the given image type using the design framework.

        Delegates to prompt_builder module which handles priority logic
        (GPT-4o generated prompts first, template fallback second).
        """
        if not self._current_framework:
            raise ValueError("No design framework available")

        from app.services.prompt_builder import build_framework_prompt
        return build_framework_prompt(session, image_type, self._current_framework)

    # Template prompt builders moved to app/services/prompt_builder.py

    def _get_story_beat(self, image_num: int, story_arc) -> str:
        """Get the story beat for a specific image number"""
        beats = {
            1: f"HOOK - {story_arc.hook}",
            2: f"REVEAL - {story_arc.reveal}",
            3: f"PROOF - {story_arc.proof}",
            4: f"DREAM - {story_arc.dream}",
            5: f"CLOSE - {story_arc.close}",
        }
        return beats.get(image_num, "HOOK")

    def _get_retry_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        delay = RetryConfig.BASE_DELAY * (2 ** attempt)
        return min(delay, RetryConfig.MAX_DELAY)

    def _get_prompt_variation(self, attempt: int) -> str:
        """Get prompt variation for retry attempt"""
        if attempt < len(RetryConfig.VARIATIONS):
            return RetryConfig.VARIATIONS[attempt]
        return RetryConfig.VARIATIONS[-1]

    def _find_latest_versioned_image_name(
        self,
        session_id: str,
        base_keys: List[str],
    ) -> Optional[str]:
        """
        Find the newest versioned image filename in a session folder.

        Supports multiple historical naming patterns so older projects
        can still be edited after storage key conventions changed.
        """
        try:
            files = self.storage.client.storage.from_(self.storage.generated_bucket).list(session_id)
        except Exception as e:
            logger.warning(f"Failed to list generated files for {session_id}: {e}")
            return None

        best_name = None
        best_version = -1

        for item in files or []:
            raw_name = item.get("name", "")
            name = raw_name.split("/")[-1] if "/" in raw_name else raw_name
            for base_key in base_keys:
                match = re.match(rf"^{re.escape(base_key)}_v(\d+)\.png$", name)
                if not match:
                    continue
                version = int(match.group(1))
                if version > best_version:
                    best_version = version
                    best_name = name

        return best_name

    def _resolve_aplus_source_image_path(self, session_id: str, aplus_idx: str) -> tuple[str, str]:
        """
        Resolve the best source image path for A+ edit operations.

        Returns:
            (source_image_path, canonical_save_key)
        """
        canonical_key = f"aplus_full_image_{aplus_idx}"
        canonical_path = f"supabase://{self.storage.generated_bucket}/{session_id}/{canonical_key}.png"

        # Fast path: canonical latest key exists.
        try:
            self.storage.get_generated_url(session_id, canonical_key, expires_in=60)
            return canonical_path, canonical_key
        except Exception:
            pass

        # Legacy fallback: some sessions only have older/non-canonical names.
        candidate_names = [
            f"aplus_{aplus_idx}.png",
        ]
        try:
            files = self.storage.client.storage.from_(self.storage.generated_bucket).list(session_id)
            names = {
                (item.get("name", "").split("/")[-1] if "/" in item.get("name", "") else item.get("name", ""))
                for item in (files or [])
            }
        except Exception as e:
            logger.warning(f"Failed to list generated files for fallback lookup ({session_id}): {e}")
            names = set()

        for name in candidate_names:
            if name in names:
                fallback_path = f"supabase://{self.storage.generated_bucket}/{session_id}/{name}"
                logger.info(
                    f"Using legacy A+ source key for module {aplus_idx}: {name} "
                    f"(canonical {canonical_key}.png missing)"
                )
                return fallback_path, canonical_key

        # Versioned fallback: pick latest *_vN.png variant.
        latest_versioned = self._find_latest_versioned_image_name(
            session_id=session_id,
            base_keys=[canonical_key, f"aplus_{aplus_idx}"],
        )
        if latest_versioned:
            fallback_path = f"supabase://{self.storage.generated_bucket}/{session_id}/{latest_versioned}"
            logger.info(
                f"Using versioned A+ source for module {aplus_idx}: {latest_versioned} "
                f"(canonical {canonical_key}.png missing)"
            )
            return fallback_path, canonical_key

        raise ValueError(f"No A+ image found for module {aplus_idx}")

    async def generate_single_image(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        note: Optional[str] = None,
        use_ai_enhancement: bool = True,
        reference_image_paths: Optional[List[str]] = None,
        model_override: Optional[str] = None,
    ) -> ImageResult:
        """
        Generate a single image type for a session with retry logic.

        Args:
            session: The generation session
            image_type: Which image type to generate
            note: Optional note/instructions for this specific image generation
            use_ai_enhancement: If True and note provided, use AI Designer to enhance prompt

        Returns:
            ImageResult with status and path
        """
        # Apply model override if requested
        original_model = self.gemini.model
        if model_override:
            self.gemini.model = model_override

        try:
            return await self._generate_single_image_impl(
                session, image_type, note, use_ai_enhancement, reference_image_paths
            )
        finally:
            self.gemini.model = original_model

    async def _generate_single_image_impl(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        note: Optional[str],
        use_ai_enhancement: bool,
        reference_image_paths: Optional[List[str]],
    ) -> ImageResult:
        """Internal implementation of generate_single_image."""
        # ALWAYS reload design framework from session to pick up any replan updates
        if session.design_framework_json:
            try:
                self._current_framework = DesignFramework(**session.design_framework_json)
                logger.info(f"[REGENERATION] Loaded framework: {self._current_framework.framework_name}")
            except Exception as e:
                logger.warning(f"[REGENERATION] Failed to load framework: {e}")

        # Find the image record
        image_record = None
        for img in session.images:
            if img.image_type == image_type:
                image_record = img
                break

        if not image_record:
            raise ValueError(f"No image record found for type: {image_type}")

        template_key = image_type.value

        # Get or create design context for prompt history
        design_context = self.get_design_context(session.id)
        if not design_context:
            design_context = self.create_design_context(session)

        # Track whether this is a regeneration with AI enhancement
        user_feedback = None
        change_summary = None

        # MASTER LEVEL: Use framework-based prompt if available
        if self._current_framework:
            base_prompt = self._build_framework_prompt(session, image_type)
        else:
            context = self._build_product_context(session)
            base_prompt = self.prompt_engine.build_prompt(template_key, context)

        # NOTE: global_note is now handled by AI Designer during generate_image_prompts()
        # It interprets the user's instructions differently for each image type
        # DO NOT append it raw here - that bypasses the intelligent interpretation
        if session.global_note:
            logger.info(f"[{template_key}] Global note exists but was already processed by AI Designer")

        # Handle regeneration note via AI Designer rewrite (no raw prompt injection)
        if note:
            user_feedback = note.strip()
            if user_feedback:
                latest_prompt = self.get_latest_prompt(
                    design_context,
                    image_type,
                    include_mobile=not template_key.startswith("aplus_"),
                )
                original_prompt = latest_prompt.prompt_text if latest_prompt else base_prompt
                original_prompt = self._sanitize_prompt_for_rewrite(original_prompt)

                if not use_ai_enhancement:
                    raise RuntimeError(
                        "Regeneration feedback requires AI Designer rewrite; direct injection is disabled."
                    )

                try:
                    from app.services.vision_service import get_vision_service
                    vision_service = get_vision_service()

                    framework_dict = None
                    if self._current_framework:
                        framework_dict = self._current_framework.model_dump()

                    product_analysis_text = None
                    if design_context and design_context.product_analysis:
                        analysis = design_context.product_analysis
                        if isinstance(analysis, dict):
                            parts = []
                            if analysis.get('what_i_see'):
                                parts.append(f"What I see: {analysis['what_i_see']}")
                            if analysis.get('visual_characteristics'):
                                parts.append(f"Visual characteristics: {analysis['visual_characteristics']}")
                            if analysis.get('product_category'):
                                parts.append(f"Category: {analysis['product_category']}")
                            if analysis.get('natural_mood'):
                                parts.append(f"Mood: {analysis['natural_mood']}")
                            if analysis.get('ideal_customer'):
                                parts.append(f"Ideal customer: {analysis['ideal_customer']}")
                            product_analysis_text = "\n".join(parts) if parts else str(analysis)
                        else:
                            product_analysis_text = str(analysis)
                        logger.info("[REGENERATION] Using stored product_analysis for context")

                    logger.info(f"Using AI Designer rewrite for regeneration {template_key}")
                    from app.services.prompt_builder import get_structural_context
                    enhancement = await vision_service.enhance_prompt_with_feedback(
                        original_prompt=original_prompt,
                        user_feedback=user_feedback,
                        image_type=template_key,
                        framework=framework_dict,
                        product_analysis=product_analysis_text,
                        structural_context=get_structural_context(template_key),
                    )

                    base_prompt = self._sanitize_prompt_for_rewrite(
                        enhancement["enhanced_prompt"]
                    )
                    change_summary = enhancement.get("interpretation", "AI-enhanced based on feedback")
                    logger.info(f"AI Designer interpretation: {change_summary}")
                except Exception as e:
                    logger.error(f"AI rewrite failed for regeneration {template_key}: {e}")
                    raise RuntimeError(
                        "AI Designer could not rewrite your regeneration feedback. Please retry."
                    ) from e

        # Mark as actively processing only after preflight/prompt preparation succeeds.
        # This avoids leaving rows stuck in PROCESSING when preflight throws.
        image_record.status = GenerationStatusEnum.PROCESSING
        image_record.error_message = None
        image_record.completed_at = None
        self.db.commit()

        last_error = None

        for attempt in range(RetryConfig.MAX_RETRIES):
            try:
                # Add variation to prompt for retries
                variation = self._get_prompt_variation(attempt)
                prompt = base_prompt + variation

                logger.info(
                    f"Generating {template_key} for session {session.id} "
                    f"(attempt {attempt + 1}/{RetryConfig.MAX_RETRIES})"
                )

                # Build reference image paths and semantic roles.
                # If user provided custom reference_image_paths (focus images), use those instead.
                style_image_index = None
                logo_image_index = None
                reference_role_by_index: Dict[int, str] = {}
                additional_indices: List[int] = []

                if reference_image_paths:
                    reference_paths = list(reference_image_paths)
                    logger.info(f"[GENERATION] Using {len(reference_paths)} user-selected focus images (overriding defaults)")
                else:
                    reference_paths = [session.upload_path]
                    if session.additional_upload_paths:
                        reference_paths.extend(session.additional_upload_paths)
                    if session.style_reference_path:
                        reference_paths.append(session.style_reference_path)
                    if session.logo_path and image_type != ImageTypeEnum.MAIN:
                        reference_paths.append(session.logo_path)

                style_ref_candidates = set()
                additional_ref_candidates = set(session.additional_upload_paths or [])
                if session.style_reference_path:
                    style_ref_candidates.add(session.style_reference_path)

                if design_context and design_context.image_inventory:
                    for inv in (design_context.image_inventory or []):
                        inv_path = inv.get("path")
                        inv_type = (inv.get("type") or "").lower()
                        if not inv_path:
                            continue
                        if inv_type in ("style_reference", "original_style_reference"):
                            style_ref_candidates.add(inv_path)
                        elif inv_type.startswith("additional_") or inv_type.startswith("additional_product_"):
                            additional_ref_candidates.add(inv_path)

                for idx, path in enumerate(reference_paths, start=1):
                    role = "reference"
                    if idx == 1:
                        role = "primary_product"
                    elif any(self._paths_match(path, candidate) for candidate in style_ref_candidates):
                        role = "style_reference"
                        if style_image_index is None:
                            style_image_index = idx
                    elif session.logo_path and self._paths_match(path, session.logo_path):
                        role = "logo"
                        if logo_image_index is None:
                            logo_image_index = idx
                    elif any(self._paths_match(path, candidate) for candidate in additional_ref_candidates):
                        role = "additional_product"
                        additional_indices.append(idx)
                    reference_role_by_index[idx] = role

                # For custom focus selections, treat all remaining support refs as additional product context.
                if reference_image_paths:
                    for idx in range(2, len(reference_paths) + 1):
                        if idx in (style_image_index, logo_image_index):
                            continue
                        if reference_role_by_index.get(idx) == "reference":
                            reference_role_by_index[idx] = "additional_product"
                            additional_indices.append(idx)

                additional_indices = sorted(set(additional_indices))
                additional_count = len(additional_indices)
                additional_order = {
                    image_idx: order
                    for order, image_idx in enumerate(additional_indices, start=1)
                }

                # === COMPREHENSIVE REFERENCE IMAGE LOGGING ===
                logger.info("=" * 80)
                logger.info(f"[GENERATION] === IMAGE GENERATION REQUEST for {template_key.upper()} ===")
                logger.info(f"[GENERATION] Session ID: {session.id}")
                logger.info(f"[GENERATION] Product: {session.product_title}")
                logger.info(f"[GENERATION] Image Type: {template_key}")
                logger.info(f"[GENERATION] Attempt: {attempt + 1}/{RetryConfig.MAX_RETRIES}")
                logger.info("-" * 40)
                logger.info(f"[GENERATION] REFERENCE IMAGES ({len(reference_paths)} total):")
                for idx, path in enumerate(reference_paths, start=1):
                    role = reference_role_by_index.get(idx, "reference")
                    label = ""
                    if role == "primary_product":
                        label = " (PRIMARY PRODUCT)"
                    elif role == "style_reference":
                        label = " (STYLE REFERENCE)"
                    elif role == "logo":
                        label = " (LOGO)"
                    elif role == "additional_product":
                        label = f" (ADDITIONAL PRODUCT {additional_order.get(idx, idx)})"
                    logger.info(f"[GENERATION]   [Image {idx}] {path}{label}")
                logger.info("-" * 40)
                logger.info(f"[GENERATION] FRAMEWORK: {self._current_framework.framework_name if self._current_framework else 'None'}")
                logger.info(f"[GENERATION] Has Style Reference: {style_image_index is not None}")
                logger.info(f"[GENERATION] Has Logo: {logo_image_index is not None}")
                logger.info(f"[GENERATION] Additional Images: {additional_count}")
                logger.info("=" * 80)

                # Prepend style reference instructions to prompt if style image provided.
                if style_image_index:
                    from app.prompts.ai_designer import STYLE_REFERENCE_PROMPT_PREFIX

                    prompt = self._strip_style_reference_prefix(prompt)

                    additional_desc = ""
                    for additional_number, image_idx in enumerate(additional_indices, start=1):
                        additional_desc += f"- Image {image_idx}: Additional product photo {additional_number}\n"

                    logo_desc = ""
                    if logo_image_index:
                        logo_desc = f"- Image {logo_image_index}: Brand logo\n"

                    style_prefix = STYLE_REFERENCE_PROMPT_PREFIX.format(
                        style_image_index=style_image_index,
                        additional_images_desc=additional_desc,
                        logo_image_desc=logo_desc,
                    )
                    prompt = style_prefix + prompt
                    logger.info(f"[{template_key.upper()}] Added style reference prefix (style is Image #{style_image_index})")
                # Append lighting override once (prevents duplicate override blocks on regenerations)
                prompt = append_lighting_override_once(prompt)

                # Generate image with reference(s)
                generated_image = await self.gemini.generate_image(
                    prompt=prompt,
                    reference_image_paths=reference_paths,
                    aspect_ratio="1:1",
                    max_retries=1,  # Let our retry logic handle retries
                )

                if generated_image is None:
                    raise ValueError("No image returned from Gemini API")

                # Store prompt in history first to get version number
                img_version = 1
                if design_context:
                    try:
                        # Build reference image metadata for prompt history
                        ref_meta = []
                        additional_counter = 0
                        for idx, rp in enumerate(reference_paths, start=1):
                            role = reference_role_by_index.get(idx, "reference")
                            if role == "primary_product":
                                ref_type = "primary_product"
                                label = "PRODUCT_PHOTO"
                            elif role == "style_reference":
                                ref_type = "style_reference"
                                label = "STYLE_REFERENCE"
                            elif role == "logo":
                                ref_type = "logo"
                                label = "BRAND_LOGO"
                            elif role == "additional_product":
                                additional_counter += 1
                                ref_type = f"additional_product_{additional_counter}"
                                label = f"ADDITIONAL_PRODUCT_{additional_counter}"
                            else:
                                ref_type = "reference"
                                label = f"REFERENCE_IMAGE_{idx}"
                            ref_meta.append({"type": ref_type, "path": rp, "label": label})

                        ph = self.store_prompt_in_history(
                            context=design_context,
                            image_type=image_type,
                            prompt_text=prompt,  # The final prompt that was sent
                            user_feedback=user_feedback,
                            change_summary=change_summary,
                            reference_image_paths=ref_meta if ref_meta else None,
                            model_name=self.gemini.model,
                        )
                        img_version = ph.version
                    except Exception as e:
                        logger.warning(f"Failed to store prompt in history: {e}")

                # Save to storage with versioned copy
                storage_path = self.storage.save_generated_image_versioned(
                    session_id=session.id,
                    image_type=template_key,
                    image=generated_image,
                    version=img_version,
                )

                # Update record - success!
                image_record.storage_path = storage_path
                image_record.status = GenerationStatusEnum.COMPLETE
                image_record.completed_at = datetime.now(timezone.utc)
                image_record.retry_count = attempt
                image_record.error_message = None
                self.db.commit()

                logger.info(
                    f"Successfully generated {template_key} for session {session.id} "
                    f"on attempt {attempt + 1}"
                )

                return ImageResult(
                    image_type=SchemaImageType(template_key),
                    status=SchemaStatus.COMPLETE,
                    storage_path=storage_path,
                )

            except Exception as e:
                last_error = e
                image_record.retry_count = attempt + 1

                logger.warning(
                    f"Generation attempt {attempt + 1} failed for {template_key} "
                    f"(session: {session.id}): {e}"
                )

                # Wait before retry (except on last attempt)
                if attempt < RetryConfig.MAX_RETRIES - 1:
                    delay = self._get_retry_delay(attempt)
                    logger.info(f"Waiting {delay}s before retry...")
                    await asyncio.sleep(delay)

        # All retries exhausted
        logger.error(
            f"All {RetryConfig.MAX_RETRIES} attempts failed for {template_key} "
            f"(session: {session.id}). Last error: {last_error}"
        )

        # Update record with final failure
        image_record.status = GenerationStatusEnum.FAILED
        image_record.error_message = str(last_error)
        self.db.commit()

        return ImageResult(
            image_type=SchemaImageType(template_key),
            status=SchemaStatus.FAILED,
            error_message=str(last_error),
        )

    async def edit_single_image(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        edit_instructions: str,
        reference_image_paths: Optional[List[str]] = None,
        model_override: Optional[str] = None,
    ) -> ImageResult:
        """
        Edit an existing generated image with specific instructions.

        Unlike regenerate (which creates NEW images from product photos),
        this MODIFIES the existing generated image based on user instructions.

        Use for:
        - "Change the headline to 'New Text'"
        - "Make the background lighter"
        - "Remove the icon in the corner"
        - "Fill the empty area with the gradient"

        Args:
            session: The generation session
            image_type: Which image to edit
            edit_instructions: What to change

        Returns:
            ImageResult with status and path
        """
        # Apply model override if requested
        original_model = self.gemini.model
        if model_override:
            self.gemini.model = model_override

        try:
            return await self._edit_single_image_impl(
                session, image_type, edit_instructions, reference_image_paths
            )
        finally:
            self.gemini.model = original_model

    async def _edit_single_image_impl(
        self,
        session: GenerationSession,
        image_type: ImageTypeEnum,
        edit_instructions: str,
        reference_image_paths: Optional[List[str]],
    ) -> ImageResult:
        """Internal implementation of edit_single_image."""
        template_key = image_type.value
        is_aplus = template_key.startswith("aplus_")
        if session.design_framework_json:
            try:
                self._current_framework = DesignFramework(**session.design_framework_json)
            except Exception as e:
                logger.warning(f"[EDIT] Failed to load framework for context: {e}")

        # For A+ images: no ImageRecord, look up storage path directly
        # For listing images: use ImageRecord
        image_record = None
        existing_image_path = None

        if is_aplus:
            aplus_idx = template_key.replace("aplus_", "")
            existing_image_path, storage_key = self._resolve_aplus_source_image_path(
                session_id=session.id,
                aplus_idx=aplus_idx,
            )
        else:
            # Find the listing image record
            for img in session.images:
                if img.image_type == image_type:
                    image_record = img
                    break

            if not image_record:
                raise ValueError(f"No image record found for type: {image_type}")

            if image_record.status != GenerationStatusEnum.COMPLETE:
                raise ValueError(f"Cannot edit image - status is {image_record.status.value}, must be 'complete'")

            if not image_record.storage_path:
                raise ValueError("No existing image to edit - storage path is empty")

            existing_image_path = image_record.storage_path

        logger.info(f"Editing {template_key} for session {session.id}")
        logger.info(f"Edit instructions: {edit_instructions[:100]}...")

        # Mark listing image as processing (A+ has no record to update)
        original_path = existing_image_path
        if image_record:
            image_record.status = GenerationStatusEnum.PROCESSING
            image_record.error_message = None
            self.db.commit()

        try:
            # A+ modules use wider aspect ratio (1464x600 ≈ 21:9)
            aspect_ratio = "21:9" if is_aplus else "1:1"

            # Use AI Designer to rewrite the previous prompt with edit feedback.
            design_context = self.get_design_context(session.id)
            if not design_context:
                design_context = self.create_design_context(session)

            change_summary = "Image edit"

            latest_prompt = self.get_latest_prompt(
                design_context,
                image_type,
                include_mobile=not is_aplus,
            )
            original_prompt = latest_prompt.prompt_text if latest_prompt else None
            if not original_prompt:
                if is_aplus:
                    original_prompt = (
                        "Revise the existing A+ module image while preserving product identity, "
                        "brand style, and readability."
                    )
                elif self._current_framework:
                    original_prompt = self._build_framework_prompt(session, image_type)
                else:
                    context = self._build_product_context(session)
                    original_prompt = self.prompt_engine.build_prompt(template_key, context)
            original_prompt = self._sanitize_prompt_for_rewrite(original_prompt)

            try:
                from app.services.vision_service import get_vision_service
                vision_service = get_vision_service()

                framework_dict = None
                if self._current_framework:
                    framework_dict = self._current_framework.model_dump()
                elif session.design_framework_json:
                    framework_dict = session.design_framework_json

                product_analysis_text = None
                if design_context.product_analysis:
                    analysis = design_context.product_analysis
                    if isinstance(analysis, dict):
                        parts = []
                        if analysis.get('what_i_see'):
                            parts.append(f"What I see: {analysis['what_i_see']}")
                        if analysis.get('visual_characteristics'):
                            parts.append(f"Visual characteristics: {analysis['visual_characteristics']}")
                        if analysis.get('product_category'):
                            parts.append(f"Category: {analysis['product_category']}")
                        product_analysis_text = "\n".join(parts) if parts else str(analysis)
                    else:
                        product_analysis_text = str(analysis)

                logger.info(f"[EDIT] Using AI Designer to plan edit instructions for {template_key}")
                from app.services.prompt_builder import get_structural_context
                edit_plan = await vision_service.plan_edit_instructions(
                    source_image_path=existing_image_path,
                    user_feedback=edit_instructions,
                    image_type=template_key,
                    original_prompt=original_prompt,
                    framework=framework_dict,
                    product_analysis=product_analysis_text,
                    reference_image_paths=reference_image_paths,
                    structural_context=get_structural_context(template_key),
                )
                enhanced_instructions = (edit_plan.get("edit_instructions") or "").strip()
                if not enhanced_instructions:
                    raise ValueError("AI Designer returned empty edit_instructions")
                change_summary = edit_plan.get("interpretation", "AI-guided edit")
                logger.info(f"[EDIT] AI Designer interpretation: {change_summary}")
            except Exception as e:
                logger.error(f"[EDIT] AI edit planning failed for {template_key}: {e}")
                raise RuntimeError(
                    "AI Designer could not plan edit instructions. Please retry."
                ) from e

            # Call Gemini to edit the image with enhanced instructions
            edited_image = await self.gemini.edit_image(
                source_image_path=existing_image_path,
                edit_instructions=enhanced_instructions,
                reference_images=reference_image_paths,
                aspect_ratio=aspect_ratio,
                max_retries=3,
            )

            if edited_image is None:
                raise ValueError("No image returned from Gemini edit API")

            # Store prompt in history to get version number
            edit_version = 1
            if design_context:
                try:
                    # Build reference image metadata for edit prompt history
                    edit_ref_meta = [{
                        "type": "source_image",
                        "path": existing_image_path,
                        "label": "SOURCE_IMAGE",
                    }]
                    if reference_image_paths:
                        for idx, rp in enumerate(reference_image_paths):
                            if session.upload_path and rp == session.upload_path:
                                edit_ref_meta.append({
                                    "type": "primary",
                                    "path": rp,
                                    "label": "PRODUCT_PHOTO",
                                })
                            elif session.style_reference_path and rp == session.style_reference_path:
                                edit_ref_meta.append({
                                    "type": "style_reference",
                                    "path": rp,
                                    "label": "STYLE_REFERENCE",
                                })
                            elif session.logo_path and rp == session.logo_path:
                                edit_ref_meta.append({
                                    "type": "logo",
                                    "path": rp,
                                    "label": "BRAND_LOGO",
                                })
                            else:
                                edit_ref_meta.append({
                                    "type": "focus_reference",
                                    "path": rp,
                                    "label": f"FOCUS_REFERENCE_{idx + 1}",
                                })

                    ph = self.store_prompt_in_history(
                        context=design_context,
                        image_type=image_type,
                        prompt_text=f"[EDIT] {enhanced_instructions}",
                        user_feedback=edit_instructions,
                        change_summary=change_summary,
                        reference_image_paths=edit_ref_meta,
                        model_name=self.gemini.model,
                    )
                    edit_version = ph.version
                except Exception as e:
                    logger.warning(f"Failed to store edit prompt in history: {e}")

            # Save edited image with versioned copy
            save_key = storage_key if is_aplus else template_key
            storage_path = self.storage.save_generated_image_versioned(
                session_id=session.id,
                image_type=save_key,
                image=edited_image,
                version=edit_version,
            )

            # Update listing image record (A+ has no record)
            if image_record:
                image_record.storage_path = storage_path
                image_record.status = GenerationStatusEnum.COMPLETE
                image_record.completed_at = datetime.now(timezone.utc)
                image_record.error_message = None
                self.db.commit()

            logger.info(f"Successfully edited {template_key} for session {session.id}")

            return ImageResult(
                image_type=SchemaImageType(template_key),
                status=SchemaStatus.COMPLETE,
                storage_path=storage_path,
            )

        except Exception as e:
            logger.error(f"Edit failed for {template_key} (session: {session.id}): {e}")

            # Revert listing image to complete with original path
            if image_record:
                image_record.status = GenerationStatusEnum.COMPLETE
                image_record.storage_path = original_path
                image_record.error_message = f"Edit failed: {str(e)}"
                self.db.commit()

            return ImageResult(
                image_type=SchemaImageType(template_key),
                status=SchemaStatus.FAILED,
                storage_path=original_path,
                error_message=str(e),
            )

    async def generate_all_images(
        self,
        session: GenerationSession,
        model_override: Optional[str] = None,
    ) -> List[ImageResult]:
        """
        Generate all 5 image types for a session.

        Args:
            session: The generation session

        Returns:
            List of ImageResult for each type
        """
        # Load design framework from session if available
        if session.design_framework_json and not self._current_framework:
            try:
                self._current_framework = DesignFramework(**session.design_framework_json)
                logger.info(f"Loaded MASTER level framework from session: {self._current_framework.framework_name}")
            except Exception as e:
                logger.warning(f"Failed to load design framework from session: {e}")

        # Update session status
        session.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        logger.info(f"Starting SEQUENTIAL generation of all 5 images for session {session.id}")

        # Generate all 5 images SEQUENTIALLY (one at a time)
        # This allows the frontend to show progress as each image completes
        results = []
        for i, image_type in enumerate(self.IMAGE_TYPES):
            logger.info(f"Generating image {i+1}/5: {image_type.value}")
            result = await self.generate_single_image(session, image_type, model_override=model_override)
            results.append(result)
            # Commit after each image so frontend can poll and see progress
            self.db.commit()
            logger.info(f"Completed image {i+1}/5: {image_type.value} - status: {result.status}")

        logger.info(f"All 5 images generated sequentially for session {session.id}")

        # Update session status based on results
        complete_count = sum(1 for r in results if r.status == SchemaStatus.COMPLETE)
        total_count = len(results)

        if complete_count == total_count:
            session.status = GenerationStatusEnum.COMPLETE
        elif complete_count > 0:
            session.status = GenerationStatusEnum.PARTIAL
        else:
            session.status = GenerationStatusEnum.FAILED

        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        logger.info(
            f"Session {session.id} completed with status: {session.status.value} "
            f"({complete_count}/{total_count} images successful)"
        )

        return results

    async def retry_failed_images(
        self,
        session: GenerationSession,
    ) -> List[ImageResult]:
        """
        Retry generation of failed images only - IN PARALLEL.

        Args:
            session: The generation session

        Returns:
            List of ImageResult for retried images
        """
        # Collect failed images to retry
        failed_image_types = []
        for img in session.images:
            if img.status == GenerationStatusEnum.FAILED:
                # Reset status for retry
                img.status = GenerationStatusEnum.PENDING
                img.error_message = None
                failed_image_types.append(img.image_type)

        self.db.commit()

        if not failed_image_types:
            return []

        logger.info(f"Retrying {len(failed_image_types)} failed images in PARALLEL")

        # Retry all failed images in parallel
        results = await asyncio.gather(
            *[self.generate_single_image(session, image_type) for image_type in failed_image_types]
        )

        # Update session status
        self._update_session_status(session)

        return results

    def _update_session_status(self, session: GenerationSession) -> None:
        """Update session status based on image statuses"""
        statuses = [img.status for img in session.images]

        if all(s == GenerationStatusEnum.COMPLETE for s in statuses):
            session.status = GenerationStatusEnum.COMPLETE
        elif any(s == GenerationStatusEnum.COMPLETE for s in statuses):
            session.status = GenerationStatusEnum.PARTIAL
        elif any(s == GenerationStatusEnum.PROCESSING for s in statuses):
            session.status = GenerationStatusEnum.PROCESSING
        elif any(s == GenerationStatusEnum.PENDING for s in statuses):
            session.status = GenerationStatusEnum.PENDING
        else:
            session.status = GenerationStatusEnum.FAILED

        self.db.commit()

    def get_session_status(self, session_id: str) -> Optional[GenerationSession]:
        """Get a session by ID"""
        return self.db.query(GenerationSession).filter(
            GenerationSession.id == session_id
        ).first()

    def get_session_results(self, session: GenerationSession) -> List[ImageResult]:
        """Get image results for a session"""
        results = []
        for img in session.images:
            results.append(ImageResult(
                image_type=SchemaImageType(img.image_type.value),
                status=SchemaStatus(img.status.value),
                storage_path=img.storage_path,
                error_message=img.error_message,
            ))
        return results

    def get_generation_stats(self, session: GenerationSession) -> Dict:
        """Get statistics about a generation session"""
        statuses = {}
        for status in GenerationStatusEnum:
            statuses[status.value] = sum(
                1 for img in session.images if img.status == status
            )

        return {
            "session_id": session.id,
            "total_images": len(session.images),
            "by_status": statuses,
            "retry_counts": {
                img.image_type.value: img.retry_count
                for img in session.images
            }
        }

    def create_preview_session(self, request: StylePreviewRequest, user_id: Optional[str] = None) -> GenerationSession:
        """
        Create a session for style preview generation.

        Args:
            request: Style preview request with product details
            user_id: Optional Supabase user ID (from authenticated request)

        Returns:
            Created GenerationSession object
        """
        session = GenerationSession(
            user_id=user_id,  # Associate with authenticated user
            upload_path=request.upload_path,
            product_title=request.product_title,
            feature_1=request.feature_1,
            brand_colors=request.brand_colors or [],
            logo_path=request.logo_path,
            style_reference_path=request.style_reference_path,
            color_count=request.color_count,
            color_palette=request.color_palette or [],
            status=GenerationStatusEnum.PENDING,
        )
        self.db.add(session)
        self.db.flush()

        # Create image records for each style preview
        for style_id in request.style_ids:
            image_record = ImageRecord(
                session_id=session.id,
                image_type=ImageTypeEnum.STYLE_PREVIEW,
                style_id=style_id,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)

        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Created style preview session: {session.id}")
        return session

    async def generate_style_preview(
        self,
        session: GenerationSession,
        style_id: str,
    ) -> StylePreviewResult:
        """
        Generate a single style preview image.

        Args:
            session: The generation session
            style_id: Which style to preview

        Returns:
            StylePreviewResult with status and image URL
        """
        from app.prompts import get_style_preset

        style = get_style_preset(style_id)
        if not style:
            return StylePreviewResult(
                style_id=style_id,
                style_name="Unknown",
                status=SchemaStatus.FAILED,
                error_message=f"Unknown style: {style_id}"
            )

        # Find the image record for this style
        image_record = None
        for img in session.images:
            if img.image_type == ImageTypeEnum.STYLE_PREVIEW and img.style_id == style_id:
                image_record = img
                break

        if not image_record:
            # Create one if it doesn't exist
            image_record = ImageRecord(
                session_id=session.id,
                image_type=ImageTypeEnum.STYLE_PREVIEW,
                style_id=style_id,
                status=GenerationStatusEnum.PENDING,
            )
            self.db.add(image_record)
            self.db.commit()

        # Update status to processing
        image_record.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        # Build context with style override
        context = self._build_product_context(session, style_override=style_id)
        prompt = self.prompt_engine.build_style_preview_prompt(context, style_id)

        try:
            logger.info(f"Generating style preview for {style_id} (session: {session.id})")

            # Build reference paths for style preview
            # Include product image and style reference (if provided)
            # No logo for style previews - that's for final generation
            reference_paths = [session.upload_path]
            if session.style_reference_path:
                reference_paths.append(session.style_reference_path)

            generated_image = await self.gemini.generate_image(
                prompt=prompt,
                reference_image_paths=reference_paths,
                aspect_ratio="1:1",
                max_retries=2,
            )

            if generated_image is None:
                raise ValueError("No image returned from Gemini API")

            # Save to storage
            storage_path = self.storage.save_generated_image(
                session_id=session.id,
                image_type=f"style_preview_{style_id}",
                image=generated_image,
            )

            # Update record
            image_record.storage_path = storage_path
            image_record.status = GenerationStatusEnum.COMPLETE
            image_record.completed_at = datetime.now(timezone.utc)
            self.db.commit()

            logger.info(f"Successfully generated style preview for {style_id}")

            return StylePreviewResult(
                style_id=style_id,
                style_name=style.name,
                status=SchemaStatus.COMPLETE,
                image_url=f"/api/images/{session.id}/style_preview_{style_id}",
            )

        except Exception as e:
            logger.error(f"Style preview generation failed for {style_id}: {e}")

            image_record.status = GenerationStatusEnum.FAILED
            image_record.error_message = str(e)
            self.db.commit()

            return StylePreviewResult(
                style_id=style_id,
                style_name=style.name,
                status=SchemaStatus.FAILED,
                error_message=str(e),
            )

    async def generate_all_style_previews(
        self,
        session: GenerationSession,
        style_ids: List[str],
    ) -> List[StylePreviewResult]:
        """
        Generate preview images for multiple styles.

        Args:
            session: The generation session
            style_ids: List of style IDs to preview

        Returns:
            List of StylePreviewResult for each style
        """
        session.status = GenerationStatusEnum.PROCESSING
        self.db.commit()

        logger.info(f"Generating {len(style_ids)} style previews in PARALLEL")

        # Generate all style previews in parallel
        results = await asyncio.gather(
            *[self.generate_style_preview(session, style_id) for style_id in style_ids]
        )

        logger.info(f"All {len(style_ids)} style previews generated")

        # Update session status
        complete_count = sum(1 for r in results if r.status == SchemaStatus.COMPLETE)
        if complete_count == len(results):
            session.status = GenerationStatusEnum.COMPLETE
        elif complete_count > 0:
            session.status = GenerationStatusEnum.PARTIAL
        else:
            session.status = GenerationStatusEnum.FAILED

        session.completed_at = datetime.now(timezone.utc)
        self.db.commit()

        return results

    def select_style(self, session_id: str, style_id: str) -> Optional[GenerationSession]:
        """
        Set the selected style for a session.

        Args:
            session_id: The session ID
            style_id: The selected style ID

        Returns:
            Updated session or None if not found
        """
        session = self.get_session_status(session_id)
        if not session:
            return None

        session.style_id = style_id
        self.db.commit()
        self.db.refresh(session)

        logger.info(f"Selected style {style_id} for session {session_id}")
        return session

    # ========================================================================
    # Unified execute() pipeline — replaces direct Gemini calls in endpoints
    # ========================================================================

    async def execute(self, ctx: "GenerationContext") -> "GenerationResult":
        """
        Unified generation pipeline for ALL image operations.

        Handles: generate, edit, mobile_transform, canvas_extension.
        Post-processes: hero split, canvas split, A+ resize, as-is.
        Saves with versioning and stores prompt history.

        Args:
            ctx: GenerationContext with all operation details

        Returns:
            GenerationResult with paths, URLs, and version info
        """
        from app.services.generation_utils import (
            GenerationContext, get_next_version, ensure_design_context,
        )
        from app.services.image_utils import resize_for_aplus_module
        from app.services.canvas_compositor import CanvasCompositor

        raw_image = None
        refined_previous = None

        # Apply model override if requested, restore after generation
        original_model = self.gemini.model
        if ctx.model_override:
            self.gemini.model = ctx.model_override
        ctx.model_name = self.gemini.model

        # Final safety net for A+ prompt boilerplate removal (all operations).
        if ctx.image_type == "aplus_hero" or ctx.image_type.startswith("aplus_"):
            from app.prompts.templates.aplus_modules import strip_aplus_banner_boilerplate
            ctx.prompt = strip_aplus_banner_boilerplate(ctx.prompt)

        # Step 1: Call Gemini based on operation type
        if ctx.operation == "edit" or ctx.operation == "mobile_transform":
            raw_image = await self.gemini.edit_image(
                source_image_path=ctx.source_image_path,
                edit_instructions=ctx.prompt,
                reference_images=ctx.reference_images.unnamed_paths if ctx.reference_images.unnamed_paths else None,
                aspect_ratio=ctx.aspect_ratio,
                max_retries=3,
            )
        elif ctx.operation == "canvas_extension":
            raw_image = await self.gemini.generate_image(
                prompt=ctx.prompt,
                named_images=ctx.reference_images.named_images if ctx.reference_images.named_images else None,
                aspect_ratio=ctx.aspect_ratio,
                image_size=ctx.image_size,
            )
        else:  # "generate"
            if ctx.reference_images.named_images:
                raw_image = await self.gemini.generate_image(
                    prompt=ctx.prompt,
                    named_images=ctx.reference_images.named_images,
                    aspect_ratio=ctx.aspect_ratio,
                    image_size=ctx.image_size,
                )
            else:
                raw_image = await self.gemini.generate_image(
                    prompt=ctx.prompt,
                    reference_image_paths=ctx.reference_images.unnamed_paths if ctx.reference_images.unnamed_paths else None,
                    aspect_ratio=ctx.aspect_ratio,
                    image_size=ctx.image_size,
                )

        # Restore original model after generation
        self.gemini.model = original_model

        if raw_image is None:
            raise ValueError(f"Generation failed: no image returned for {ctx.image_type}")

        # Step 2: Post-process based on image type
        result_images = {}  # key -> PIL.Image

        if ctx.image_type == "aplus_hero":
            # Hero pair: split at midpoint into modules 0 and 1
            compositor = CanvasCompositor()
            top, bottom = compositor.split_hero_image(raw_image)
            result_images["aplus_full_image_0"] = top
            result_images["aplus_full_image_1"] = bottom

        elif ctx.operation == "canvas_extension":
            # Canvas: split into refined previous + new module
            compositor = CanvasCompositor()
            top, bottom = compositor.split_canvas_output(raw_image)
            prev_idx = ctx.module_index - 1
            result_images[f"aplus_full_image_{prev_idx}"] = top
            result_images[ctx.storage_key or f"aplus_full_image_{ctx.module_index}"] = bottom
            # Track refined previous for response
            refined_previous = (prev_idx, top)

        elif ctx.target_dimensions:
            # A+ module or mobile: resize to target
            is_mobile = ctx.operation == "mobile_transform" or (ctx.target_dimensions == (600, 450))
            resized = resize_for_aplus_module(
                raw_image,
                "full_image",
                mobile=is_mobile,
            )
            key = ctx.storage_key or ctx.image_type
            result_images[key] = resized

        else:
            # Listing image or other: save as-is
            key = ctx.storage_key or ctx.image_type
            result_images[key] = raw_image

        # Step 3: Save with versioning and prompt history
        saved = {}  # key -> (path, url, version)

        # Get or create design context for prompt history
        design_ctx = None
        try:
            design_ctx = ensure_design_context(
                self.db, ctx.session, gemini=self.gemini, storage=self.storage,
            )
        except Exception as e:
            logger.warning(f"Could not get design context: {e}")

        for key, image in result_images.items():
            # Determine version
            if ctx.image_type == "aplus_hero" and design_ctx:
                # Hero pair: compute shared version across modules 0 and 1
                count_0 = self.db.query(PromptHistory).filter(
                    PromptHistory.context_id == design_ctx.id,
                    PromptHistory.image_type == ImageTypeEnum("aplus_0"),
                ).count()
                count_1 = self.db.query(PromptHistory).filter(
                    PromptHistory.context_id == design_ctx.id,
                    PromptHistory.image_type == ImageTypeEnum("aplus_1"),
                ).count()
                version = max(count_0, count_1) + 1
            else:
                version = get_next_version(self.storage, ctx.session.id, key)

            # Save image
            path = self.storage.save_generated_image_versioned(
                ctx.session.id, key, image, version,
            )

            # Get URL
            try:
                url = self.storage.get_generated_url(ctx.session.id, key, expires_in=3600)
            except Exception:
                url = f"/api/images/file?path={path}"

            saved[key] = (path, url, version)

        # Step 4: Store prompt history
        if design_ctx:
            try:
                if ctx.image_type == "aplus_hero":
                    # Store for both modules 0 and 1
                    version = list(saved.values())[0][2] if saved else 1
                    for aplus_idx in [0, 1]:
                        ph = PromptHistory(
                            context_id=design_ctx.id,
                            image_type=ImageTypeEnum(f"aplus_{aplus_idx}"),
                            version=version,
                            prompt_text=ctx.prompt,
                            reference_image_paths=ctx.reference_images.history_meta or None,
                            user_feedback=ctx.user_feedback,
                            change_summary=ctx.change_summary,
                            model_name=ctx.model_name,
                        )
                        self.db.add(ph)
                    self.db.commit()
                else:
                    # Single image type
                    img_type_enum = ImageTypeEnum(ctx.image_type) if not ctx.image_type.startswith("aplus_hero") else ImageTypeEnum("aplus_0")
                    prompt_prefix = ""
                    if ctx.operation == "edit":
                        prompt_prefix = "[MOBILE EDIT] " if self._is_mobile_storage_key(ctx.storage_key) else "[EDIT] "
                    elif ctx.operation == "mobile_transform":
                        prompt_prefix = "[MOBILE RECOMPOSE] "

                    self.store_prompt_in_history(
                        context=design_ctx,
                        image_type=img_type_enum,
                        prompt_text=f"{prompt_prefix}{ctx.prompt}",
                        user_feedback=ctx.user_feedback,
                        change_summary=ctx.change_summary,
                        reference_image_paths=ctx.reference_images.history_meta or None,
                        model_name=ctx.model_name,
                    )
            except Exception as e:
                logger.warning(f"Failed to store prompt history in execute(): {e}")

        # Build result
        from app.services.generation_utils import GenerationContext as _GC  # avoid circular

        # Primary result is the main image (or first if hero)
        if ctx.image_type == "aplus_hero":
            return GenerationResult(
                saved=saved,
                refined_previous_index=None,
            )
        elif refined_previous:
            prev_idx, _ = refined_previous
            prev_key = f"aplus_full_image_{prev_idx}"
            return GenerationResult(
                saved=saved,
                refined_previous_index=prev_idx,
                refined_previous_path=saved[prev_key][0] if prev_key in saved else None,
                refined_previous_url=saved[prev_key][1] if prev_key in saved else None,
            )
        else:
            return GenerationResult(saved=saved)


@dataclass
class GenerationResult:
    """Result from GenerationService.execute()"""
    saved: Dict[str, tuple]  # key -> (path, url, version)
    refined_previous_index: Optional[int] = None
    refined_previous_path: Optional[str] = None
    refined_previous_url: Optional[str] = None

    @property
    def primary_key(self) -> str:
        """Get the primary storage key (first one)"""
        return next(iter(self.saved))

    @property
    def primary_path(self) -> str:
        return self.saved[self.primary_key][0]

    @property
    def primary_url(self) -> str:
        return self.saved[self.primary_key][1]

    @property
    def primary_version(self) -> int:
        return self.saved[self.primary_key][2]


