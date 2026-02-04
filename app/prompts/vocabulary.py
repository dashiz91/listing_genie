"""
Vocabulary Triggers for AI Image Generation

These terms activate quality distributions in Gemini's training.
When the model sees "Hasselblad H6D-100c", it recalls the high-quality
images tagged with that camera. Same for publication names, quality
descriptors, and lighting terms.

Shared across listing images and A+ content for consistent quality.
"""

# ============================================================================
# CAMERA VOCABULARY - Triggers technical excellence
# ============================================================================

CAMERA_ANCHORS = {
    "medium_format": "Hasselblad H6D-100c",
    "ultimate": "Phase One IQ4 150MP",
    "film": "medium format film",
    "large": "shot on large format",
}

# ============================================================================
# PUBLICATION VOCABULARY - Triggers editorial standards
# ============================================================================

PUBLICATION_ANCHORS = {
    "editorial": "Architectural Digest",
    "lifestyle": "Kinfolk magazine",
    "luxury": "Sotheby's catalog",
    "minimal": "Cereal Magazine",
    "fashion": "Vogue Living",
}

# ============================================================================
# QUALITY DESCRIPTORS - Triggers craftsmanship
# ============================================================================

QUALITY_VOCABULARY = [
    "museum-quality",
    "gallery-worthy",
    "campaign imagery",
    "editorial",
    "tack-sharp",
]

# ============================================================================
# LIGHTING VOCABULARY - Triggers expertise
# ============================================================================

LIGHTING_VOCABULARY = {
    "soft": "diffused key light",
    "dramatic": "rim lighting with separation",
    "natural": "golden hour warmth",
    "studio": "studio strobes with modifiers",
    "window": "natural window light",
}

# ============================================================================
# FEELING VOCABULARY - Triggers intention
# ============================================================================

FEELING_VOCABULARY = {
    "aspirational": "aspirational but attainable",
    "intimate": "intimate and personal",
    "elevated": "elevated everyday",
    "curated": "deliberately curated",
    "breathing": "breathing room and calm",
}


def get_quality_anchor(style: str = "editorial") -> str:
    """
    Generate a quality anchor string based on desired style.

    Examples:
        get_quality_anchor("editorial") -> "Hasselblad H6D-100c. Architectural Digest. Museum-quality."
        get_quality_anchor("lifestyle") -> "Hasselblad H6D-100c. Kinfolk magazine. Museum-quality."
    """
    camera = CAMERA_ANCHORS["medium_format"]
    publication = PUBLICATION_ANCHORS.get(style, "Architectural Digest")
    return f"{camera}. {publication}. Museum-quality."


def get_listing_quality_standard() -> str:
    """Quality standard block for listing image prompts."""
    return """
═══════════════════════════════════════════════════════════════════════════════
                              QUALITY STANDARD
═══════════════════════════════════════════════════════════════════════════════

Don't aim for "good Amazon listing." Aim for "belongs in Architectural Digest."

The difference between acceptable and exceptional:
- Hasselblad, not iPhone
- Editorial, not stock
- Curated, not cluttered
- Intentional, not incidental

Your vocabulary shapes the output. Use terms that trigger excellence:
- Camera: "Hasselblad H6D-100c", "Phase One", "medium format"
- Publication: "Architectural Digest", "Kinfolk", "Cereal Magazine"
- Quality: "museum-quality", "gallery-worthy", "tack-sharp"
- Light: "diffused key light", "natural window light", "soft rim"
"""


def get_aplus_quality_standard() -> str:
    """Quality standard block for A+ content prompts."""
    return """
═══════════════════════════════════════════════════════════════════════════════
                              QUALITY STANDARD
═══════════════════════════════════════════════════════════════════════════════

This isn't a product photo. This is a brand moment.
Sotheby's catalog quality. Campaign imagery standards.

Vocabulary that triggers excellence:
- "campaign imagery" - big budget, high stakes
- "editorial" - story-driven, not stock
- "cinematic" - frame from a luxury brand film
- "tack-sharp" - technical precision
- "museum-quality" - worthy of preservation

The banner should feel like a frame from a premium brand film, not a template.
"""


# Export all
__all__ = [
    'CAMERA_ANCHORS',
    'PUBLICATION_ANCHORS',
    'QUALITY_VOCABULARY',
    'LIGHTING_VOCABULARY',
    'FEELING_VOCABULARY',
    'get_quality_anchor',
    'get_listing_quality_standard',
    'get_aplus_quality_standard',
]
