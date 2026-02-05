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

# ============================================================================
# EMOTIONAL STORYTELLING - The Arc That Sells
# ============================================================================
# Amazon shoppers make emotional decisions, then justify with logic.
# Each image in the listing should hit a specific emotional beat.

EMOTIONAL_ARC = {
    # Image 1: INTRIGUE - "What is this beautiful thing?"
    "intrigue": {
        "goal": "Stop the scroll. Create visual magnetism.",
        "emotion": "curiosity, wonder, aesthetic arrest",
        "questions": "What am I looking at? Why does it feel special?",
        "vocabulary": ["mysterious elegance", "visual magnetism", "quiet confidence"],
    },
    # Image 2: TRUST - "This is real, well-made"
    "trust": {
        "goal": "Show the craft. Prove quality through details.",
        "emotion": "confidence, reassurance, appreciation",
        "questions": "Is this well-made? Can I trust this brand?",
        "vocabulary": ["meticulous craftsmanship", "honest materials", "precision"],
    },
    # Image 3: BELONGING - "People like me choose this"
    "belonging": {
        "goal": "Show the tribe. Create identity connection.",
        "emotion": "recognition, aspiration, social proof",
        "questions": "Is this for someone like me? Will others approve?",
        "vocabulary": ["curated lifestyle", "discerning taste", "thoughtful choice"],
    },
    # Image 4: DESIRE - "I can see myself with this"
    "desire": {
        "goal": "Paint the future. Show the life they want.",
        "emotion": "longing, imagination, anticipation",
        "questions": "What would my life look like with this? How would it feel?",
        "vocabulary": ["everyday luxury", "gentle transformation", "quiet joy"],
    },
    # Image 5: PERMISSION - "I deserve this"
    "permission": {
        "goal": "Remove the final barrier. Justify the purchase.",
        "emotion": "confidence, validation, relief",
        "questions": "Is it worth it? Am I making the right choice?",
        "vocabulary": ["smart investment", "lasting value", "confident decision"],
    },
}

# ============================================================================
# STORYTELLING PRINCIPLES - How to trigger emotion, not describe features
# ============================================================================

STORYTELLING_PRINCIPLES = """
THE ART OF EMOTIONAL SELLING:

1. SHOW, DON'T TELL
   - Wrong: "High-quality ceramic material"
   - Right: Close-up of light catching the glaze, revealing depth and craftsmanship

2. IMPLY, DON'T STATE
   - Wrong: "Perfect for modern homes"
   - Right: Sunlit corner with brass accents, linen textures, the product belonging there

3. CREATE LONGING, NOT INFORMATION
   - Wrong: "Dimensions: 8" x 4" x 3""
   - Right: A hand reaching toward it, about to pick it up with care

4. TRIGGER MEMORY, NOT LOGIC
   - Wrong: "Water-tight interior for fresh flowers"
   - Right: Morning light through petals, dew still visible, that first-coffee moment

5. BUILD IDENTITY, NOT FEATURES
   - Wrong: "Modern minimalist design"
   - Right: The kind of object that says something about who you are
"""


# ============================================================================
# HEATMAP & ATTENTION PRINCIPLES - Where Eyes Go
# ============================================================================

HEATMAP_PRINCIPLES = """
═══════════════════════════════════════════════════════════════════════════════
                    WHERE EYES GO (Research, Not Rules)
═══════════════════════════════════════════════════════════════════════════════

Eye-tracking studies reveal patterns. Use them as intelligence, not law.

WHAT RESEARCH SHOWS:

1. PRODUCT ANCHORING
   Eyes find the product first, then orbit around it looking for context.
   → The product is your anchor. Build the composition around it.

2. F-PATTERN & Z-PATTERN
   Western readers scan left-to-right, top-to-bottom.
   Important info placed along these paths gets seen.
   → But a striking visual can BREAK the pattern and draw eyes anywhere.

3. THUMBNAIL REALITY
   At 150x150px, only bold shapes and high-contrast text register.
   → If it disappears at thumbnail size, it doesn't exist.

4. FACES ARE MAGNETIC
   Human faces (especially eyes) pull attention involuntarily.
   → In lifestyle images, faces can direct attention toward product.

5. NUMBERS POP
   "3X Stronger" registers faster than "Much Stronger"
   Specific numbers feel credible: "847 Reviews" beats "Hundreds of Reviews"
   → Quantify when you can. Specificity = believability.

6. CONTRAST WINS
   High contrast elements get seen. Low contrast gets skipped.
   → Text needs breathing room and contrast to earn attention.

7. VISUAL HIERARCHY
   Size, color, position, and isolation all signal importance.
   → The most important thing should LOOK most important.

HOW TO USE THIS:

Don't mechanically apply rules. Instead, ask:
- "If someone glanced at this for 2 seconds, what would they SEE?"
- "Does the most important message have the most visual weight?"
- "At thumbnail size, does this still communicate?"

The goal isn't to follow a heatmap template.
The goal is to be INTENTIONAL about where attention lands.
"""


# ============================================================================
# CONVERSION PRINCIPLES - Quality + Clarity Together
# ============================================================================

CONVERSION_PRINCIPLES = """
═══════════════════════════════════════════════════════════════════════════════
                    THE CONVERSION MINDSET
═══════════════════════════════════════════════════════════════════════════════

The shopper has 5 tabs open. They're scanning, not studying.
Each image has 2-3 seconds to answer a question and earn more time.

QUALITY + CLARITY (Both, Not Either)

QUALITY ANCHORS make it LOOK premium:
- Camera references: Hasselblad H6D-100c, Phase One IQ4
- Publication standards: Architectural Digest, Kinfolk, Apple product page
- Technical excellence: tack-sharp, gallery-worthy, press-ready

CLARITY ANCHORS make it COMMUNICATE:
- Text that earns its place — functional, not decorative
- Every callout answers a question or overcomes an objection
- If text doesn't WORK, it doesn't belong

The best Amazon images look like premium brand advertising
that happens to have useful information elegantly integrated.

FLEXIBLE QUALITY APPROACHES (Match to Product):

APPLE APPROACH — Premium/Minimal:
Product dominates center. One bold headline. Massive whitespace.
The product IS the message. Text is minimal but precise.
Works for: Premium, design-forward, "speaks for itself" products.

DYSON APPROACH — Technical/Engineered:
Product in action. Technical callouts with clean lines.
Engineering visible. Numbers prominent ("5X suction").
Works for: Technical products where specs matter.

GLOSSIER APPROACH — Lifestyle/Approachable:
Lifestyle-forward. Product in context. Soft, aspirational.
Text feels like a friend's recommendation, not an ad.
Works for: Beauty, wellness, emotional purchase products.

These are starting points. Let the PRODUCT guide which approach fits.
Or blend them. Or invent something new.
"""


# ============================================================================
# SHOPPER QUESTIONS - What Each Image Must Answer
# ============================================================================

SHOPPER_QUESTIONS = {
    "main": {
        "question": "What is this?",
        "job": "Stop the scroll, establish category, create intrigue",
        "text_approach": "NO TEXT - Amazon requires pure white background",
    },
    "infographic_1": {
        "question": "Is this well-made? Can I trust this?",
        "job": "Prove quality through details, earn trust",
        "text_approach": "Callouts highlighting craftsmanship, materials, precision",
    },
    "infographic_2": {
        "question": "What do I get? What are the features?",
        "job": "Answer practical questions, show what's included",
        "text_approach": "Feature grid, specs, dimensions, what's in the box",
    },
    "lifestyle": {
        "question": "Will this work for me? Will it fit my life?",
        "job": "Show product in aspirational but relatable context",
        "text_approach": "Minimal - one benefit headline or none if image speaks",
    },
    "transformation": {
        "question": "What changes if I buy this?",
        "job": "Show the before/after of their LIFE, not just the product",
        "text_approach": "Clear labels: before/after, problem/solution",
    },
    "comparison": {
        "question": "Why should I buy NOW? Why THIS one?",
        "job": "Create urgency, show social proof, differentiate",
        "text_approach": "Numbers, ratings, differentiators, limited availability",
    },
}


def get_heatmap_principles() -> str:
    """Get the heatmap/attention principles block."""
    return HEATMAP_PRINCIPLES


def get_conversion_principles() -> str:
    """Get the conversion principles block."""
    return CONVERSION_PRINCIPLES


def get_shopper_question(image_type: str) -> dict:
    """Get the shopper question context for a specific image type."""
    return SHOPPER_QUESTIONS.get(image_type, SHOPPER_QUESTIONS["infographic_1"])


def get_emotional_beat(image_number: int) -> dict:
    """Get the emotional beat for a specific image position."""
    beats = ["intrigue", "trust", "belonging", "desire", "permission"]
    beat_key = beats[min(image_number - 1, 4)]
    return EMOTIONAL_ARC[beat_key]


def get_storytelling_standard() -> str:
    """Get the storytelling principles block for prompts."""
    return STORYTELLING_PRINCIPLES


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
    'EMOTIONAL_ARC',
    'STORYTELLING_PRINCIPLES',
    'get_quality_anchor',
    'get_listing_quality_standard',
    'get_aplus_quality_standard',
    'get_emotional_beat',
    'get_storytelling_standard',
]
