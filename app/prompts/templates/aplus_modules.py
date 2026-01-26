"""
A+ Content Module Prompt Templates

These templates are used for generating Premium A+ Content images
with support for sequential/chained generation where each module
continues the visual flow from the previous one.
"""

# Base template for A+ Full Image module (1464x600)
APLUS_FULL_IMAGE_BASE = """
Create a premium Amazon A+ Content banner image for: {product_title}

PRODUCT CONTEXT:
- Brand: {brand_name}
- Key Features: {features}
- Target Audience: {target_audience}

DESIGN FRAMEWORK: {framework_name}
- Style: {framework_style}
- Primary Color: {primary_color}
- Color Palette: {color_palette}
- Mood: {framework_mood}

IMAGE REQUIREMENTS:
- Wide banner format (approximately 2.4:1 aspect ratio)
- Premium, high-end aesthetic suitable for Amazon A+ Content
- Clean, professional product photography style
- Product should be prominently featured
- Include subtle branded elements using the color palette
- Space for the design to "flow" at top and bottom edges

COMPOSITION GUIDELINES:
- Use the product photos provided as reference for the actual product appearance
- Create an elegant background that complements the product
- Incorporate brand colors naturally into the design
- Leave visual "hooks" at edges for continuity with adjacent modules
"""

# Addition for chained generation (module 2+)
APLUS_CONTINUITY_ADDITION = """

CRITICAL - VISUAL CONTINUITY:
This banner will be placed DIRECTLY BELOW another banner image.
The reference image shows the banner that appears ABOVE this one.

YOU MUST:
1. Continue the EXACT background design from the reference image
2. Match the gradient direction, colors, and visual flow
3. The top edge of YOUR image should seamlessly connect with the bottom edge of the reference
4. Maintain the same lighting direction and intensity
5. Keep consistent shadow angles and highlight positions
6. Use the same decorative elements/patterns, continuing their flow

Think of both images as ONE continuous design split into two parts.
When stacked vertically, there should be NO visible seam or break.
"""

# Template for first module in chain (no reference)
APLUS_FULL_IMAGE_FIRST = APLUS_FULL_IMAGE_BASE + """

EDGE DESIGN:
Since this is the TOP module in the A+ section, design the background so it can
naturally continue downward. Create visual elements that "flow" toward the bottom
edge, ready to be continued in the next module below.
"""

# Template for middle/subsequent modules in chain
APLUS_FULL_IMAGE_CHAINED = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION

# Template for last module in chain
APLUS_FULL_IMAGE_LAST = APLUS_FULL_IMAGE_BASE + APLUS_CONTINUITY_ADDITION + """

FINAL MODULE:
This is the LAST module in the A+ section. The design should:
- Seamlessly continue from the reference image above
- Gracefully conclude the visual flow at the bottom edge
- Create a sense of visual completion/closure
"""


def get_aplus_prompt(
    module_type: str,
    position: str,  # "first", "middle", "last", or "only"
    product_title: str,
    brand_name: str,
    features: list[str],
    target_audience: str,
    framework_name: str,
    framework_style: str,
    primary_color: str,
    color_palette: list[str],
    framework_mood: str,
    custom_instructions: str = ""
) -> str:
    """
    Generate the appropriate A+ module prompt based on position in chain.

    Args:
        module_type: Type of A+ module (e.g., "full_image")
        position: Position in the chain ("first", "middle", "last", "only")
        ... other product/framework details

    Returns:
        Formatted prompt string
    """
    if module_type == "full_image":
        if position == "first":
            template = APLUS_FULL_IMAGE_FIRST
        elif position in ("middle", "last"):
            template = APLUS_FULL_IMAGE_CHAINED if position == "middle" else APLUS_FULL_IMAGE_LAST
        else:  # "only" - single module, no chaining
            template = APLUS_FULL_IMAGE_BASE
    else:
        # Default to base template for other module types
        template = APLUS_FULL_IMAGE_BASE

    prompt = template.format(
        product_title=product_title,
        brand_name=brand_name or "Premium Brand",
        features=", ".join(features) if features else "Quality craftsmanship",
        target_audience=target_audience or "Discerning customers",
        framework_name=framework_name,
        framework_style=framework_style,
        primary_color=primary_color,
        color_palette=", ".join(color_palette) if color_palette else primary_color,
        framework_mood=framework_mood,
    )

    if custom_instructions:
        prompt += f"\n\nADDITIONAL INSTRUCTIONS:\n{custom_instructions}"

    return prompt
