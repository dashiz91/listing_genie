"""
Product Protection Directives

The product's fidelity is the immutable constraint across all generated images.
These directives ensure the AI never modifies, tints, or "improves" the actual
product - only the environment around it.

Shared across listing images and A+ content.
"""

# ============================================================================
# CORE PRODUCT PROTECTION DIRECTIVE
# ============================================================================

PRODUCT_PROTECTION_DIRECTIVE = """
═══════════════════════════════════════════════════════════════════════════════
                              THE PRODUCT IS SACRED
═══════════════════════════════════════════════════════════════════════════════

Image 1 is THE product. Not inspiration. Not reference. THE product.

Reproduce it with absolute fidelity:
- Its FORM is truth. Never "improve" or "interpret" the shape.
- Its COLORS are sacred. A white product stays white. A blue product stays blue.
- Its DETAILS matter. Every texture, every curve, every feature.

When writing prompts, always anchor to: "the exact product shown in Image 1"
Never describe by name alone - the AI must LOOK at the reference, not imagine.

Brand colors create CONTEXT around the product:
- Backgrounds and gradients ✓
- UI elements and icons ✓
- Text and headlines ✓
- Atmospheric lighting ✓

Brand colors NEVER touch the product itself:
- No color filters on product ✗
- No tinting the product ✗
- No "brand-colored version" ✗

Think of it like a gallery: the walls can be any color,
but the artwork remains exactly as the artist created it.
"""


# ============================================================================
# PRODUCT REFERENCE INSTRUCTIONS (How to reference in prompts)
# ============================================================================

PRODUCT_REFERENCE_INSTRUCTION = """
PRODUCT REFERENCE RULES:
- ALWAYS reference as "the exact product shown in Image 1" or "the product from the reference photo"
- NEVER describe by product name alone (e.g., "The sun planter is...")
- The AI must LOOK at the attached image, not imagine a generic product

WRONG: "The sun planter is positioned on a white background..."
RIGHT: "The product (shown in Image 1) is positioned on a white background..."

WRONG: "A decorative ceramic pot centered in the frame..."
RIGHT: "The exact product from the provided photo centered in the frame..."
"""


# ============================================================================
# AMAZON MAIN IMAGE REQUIREMENTS (Non-negotiable)
# ============================================================================

AMAZON_MAIN_IMAGE_REQUIREMENTS = """
AMAZON MAIN IMAGE (Image 1) - NON-NEGOTIABLE:
- Background: Pure white (#FFFFFF). No exceptions.
- Content: Product only. No text. No graphics. No props.
- Fill: Product occupies 85%+ of frame.
- Quality: Hasselblad-level product photography.

Failure to meet these = image rejected by Amazon.
"""


def get_product_protection_block() -> str:
    """Get the full product protection block for generation prompts."""
    return PRODUCT_PROTECTION_DIRECTIVE


def get_product_reference_block() -> str:
    """Get product reference instructions for prompts."""
    return PRODUCT_REFERENCE_INSTRUCTION


def get_main_image_requirements() -> str:
    """Get Amazon main image requirements."""
    return AMAZON_MAIN_IMAGE_REQUIREMENTS


# Export all
__all__ = [
    'PRODUCT_PROTECTION_DIRECTIVE',
    'PRODUCT_REFERENCE_INSTRUCTION',
    'AMAZON_MAIN_IMAGE_REQUIREMENTS',
    'get_product_protection_block',
    'get_product_reference_block',
    'get_main_image_requirements',
]
