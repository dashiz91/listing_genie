from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
import uuid
import enum

Base = declarative_base()


# Enums
class GenerationStatusEnum(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    PARTIAL = "partial"
    FAILED = "failed"


class ImageTypeEnum(enum.Enum):
    MAIN = "main"
    INFOGRAPHIC_1 = "infographic_1"
    INFOGRAPHIC_2 = "infographic_2"
    LIFESTYLE = "lifestyle"
    COMPARISON = "comparison"
    # Style previews
    STYLE_PREVIEW = "style_preview"
    # A+ Content modules (0-indexed)
    APLUS_0 = "aplus_0"
    APLUS_1 = "aplus_1"
    APLUS_2 = "aplus_2"
    APLUS_3 = "aplus_3"
    APLUS_4 = "aplus_4"
    APLUS_5 = "aplus_5"


class IntentTypeEnum(enum.Enum):
    DURABILITY = "durability"
    USE_CASE = "use_case"
    STYLE = "style"
    PROBLEM_SOLUTION = "problem_solution"
    COMPARISON = "comparison"


# Models
class GenerationSession(Base):
    """Represents a single image generation request/session"""
    __tablename__ = "generation_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True, index=True)  # Supabase user UUID
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING)

    # Upload reference
    upload_path = Column(String(500), nullable=False)
    additional_upload_paths = Column(JSON, default=list)  # Additional product images

    # Product information
    product_title = Column(String(200), nullable=False)
    feature_1 = Column(String(100), nullable=True)  # Now optional
    feature_2 = Column(String(100), nullable=True)  # Now optional
    feature_3 = Column(String(100), nullable=True)  # Now optional
    target_audience = Column(String(150), nullable=True)  # Now optional

    # Brand & Style
    brand_name = Column(String(100), nullable=True)
    brand_colors = Column(JSON, default=list)  # List of hex colors
    logo_path = Column(String(500), nullable=True)  # Path to brand logo image
    style_id = Column(String(50), nullable=True)  # Selected style preset (legacy)

    # MASTER Level: Brand Vibe - drives the entire creative brief
    brand_vibe = Column(String(50), nullable=True)  # e.g., "clean_modern", "premium_luxury"
    primary_color = Column(String(7), nullable=True)  # Primary brand color (hex: #RRGGBB)

    # Style Reference Image - AI matches this visual style across all images
    style_reference_path = Column(String(500), nullable=True)

    # Color Palette Options - User-specified or AI-generated
    color_count = Column(Integer, nullable=True)  # Number of colors (2-6)
    color_palette = Column(JSON, default=list)  # Specific hex colors for palette

    # MASTER LEVEL: Complete design framework from Principal Designer AI
    # Stores the full framework as JSON (colors, typography, copy, layout, etc.)
    design_framework_json = Column(JSON, nullable=True)

    # Global note/instructions applied to all image generations
    global_note = Column(Text, nullable=True)

    # A+ Content: Art Director visual script (JSON plan for all modules)
    aplus_visual_script = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=7))

    # Relationships
    keywords = relationship("SessionKeyword", back_populates="session", cascade="all, delete-orphan")
    images = relationship("ImageRecord", back_populates="session", cascade="all, delete-orphan")


class SessionKeyword(Base):
    """Keywords associated with a generation session, with intent classification"""
    __tablename__ = "session_keywords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("generation_sessions.id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    intent_types = Column(JSON, default=list)  # List of IntentTypeEnum values
    created_at = Column(DateTime, default=func.now())

    # Relationships
    session = relationship("GenerationSession", back_populates="keywords")


class ImageRecord(Base):
    """Record of a generated image with status tracking"""
    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("generation_sessions.id"), nullable=False)
    image_type = Column(Enum(ImageTypeEnum), nullable=False)
    storage_path = Column(String(500), nullable=True)
    status = Column(Enum(GenerationStatusEnum), default=GenerationStatusEnum.PENDING)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)

    # For style previews
    style_id = Column(String(50), nullable=True)

    # Relationships
    session = relationship("GenerationSession", back_populates="images")


# ============================================================================
# AI DESIGNER CONTEXT SYSTEM
# ============================================================================

class ColorModeEnum(enum.Enum):
    """How colors should be determined"""
    AI_DECIDES = "ai_decides"          # AI picks all colors based on product
    SUGGEST_PRIMARY = "suggest_primary" # User suggests primary, AI builds palette
    LOCKED_PALETTE = "locked_palette"   # User locks exact colors, AI must use them


class DesignContext(Base):
    """
    Persistent context for AI Designer across a session.
    Stores what the AI knows about this design project.
    """
    __tablename__ = "design_contexts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("generation_sessions.id"), unique=True, nullable=False)

    # What AI Designer analyzed about the product
    product_analysis = Column(JSON, nullable=True)  # Structured analysis from Vision AI

    # Image inventory - what reference images are available
    # Format: [{"type": "primary", "path": "...", "description": "Hero shot"}, ...]
    image_inventory = Column(JSON, default=list)

    # Color mode and locked colors (if any)
    color_mode = Column(Enum(ColorModeEnum), default=ColorModeEnum.AI_DECIDES)
    locked_colors = Column(JSON, default=list)  # List of hex colors if mode is LOCKED_PALETTE

    # The selected framework (stored separately for quick access)
    selected_framework_id = Column(String(50), nullable=True)
    selected_framework_name = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship("GenerationSession", backref="design_context", uselist=False)
    prompt_history = relationship("PromptHistory", back_populates="design_context", cascade="all, delete-orphan")


class PromptHistory(Base):
    """
    History of prompts generated/modified for each image type.
    Enables AI Designer to see what it wrote before and user feedback.
    """
    __tablename__ = "prompt_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    context_id = Column(Integer, ForeignKey("design_contexts.id"), nullable=False)
    image_type = Column(Enum(ImageTypeEnum), nullable=False)

    # Version tracking (1 = original, 2+ = regenerations)
    version = Column(Integer, default=1)

    # The prompt that was sent to image generator
    prompt_text = Column(Text, nullable=False)

    # Actual reference images passed to the generation call
    # Format: [{"type": "primary", "path": "supabase://..."}, {"type": "previous_module", "path": "..."}]
    reference_image_paths = Column(JSON, nullable=True)

    # User feedback that triggered this version (null for v1)
    user_feedback = Column(Text, nullable=True)

    # What changed from previous version (AI's interpretation)
    change_summary = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=func.now())

    # Relationships
    design_context = relationship("DesignContext", back_populates="prompt_history")
