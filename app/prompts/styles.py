"""
Style Presets for Cohesive Image Generation
Enhanced with professional design framework principles.
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from .design_framework import (
    DesignFramework,
    LayoutGrid,
    ColorHarmony,
    ColorTemperature,
    SaturationLevel,
    TypographyStyle,
    ShadowStyle,
    BackgroundStyle,
    ShapeLanguage,
    IconStyle,
    BadgeStyle,
    LightingMood,
    generate_random_framework,
)


@dataclass
class StylePreset:
    """Defines a cohesive visual style for all images"""
    id: str
    name: str
    description: str
    color_palette: List[str]
    typography: str
    mood: str
    lighting: str
    composition_style: str
    accent_elements: str
    prompt_modifier: str  # Added to all prompts
    design_framework: Optional[DesignFramework] = None  # Full design specs


STYLE_PRESETS: Dict[str, StylePreset] = {
    "clean_minimal": StylePreset(
        id="clean_minimal",
        name="Clean & Minimal",
        description="Modern, spacious design with lots of white space. Perfect for tech, skincare, and premium products.",
        color_palette=["#FFFFFF", "#F5F5F7", "#1A1A2E", "#0071E3"],
        typography="Sans-serif, thin weights, generous spacing",
        mood="Sophisticated, calm, trustworthy",
        lighting="Soft, diffused, even lighting with subtle shadows",
        composition_style="Centered, symmetrical, breathing room around elements",
        accent_elements="Thin lines, subtle gradients, geometric shapes",
        design_framework=DesignFramework(
            layout_grid=LayoutGrid.CENTERED,
            balance="symmetric",
            whitespace="generous",
            color_harmony=ColorHarmony.MONOCHROMATIC,
            color_temperature=ColorTemperature.COOL,
            saturation=SaturationLevel.MUTED,
            primary_color="#1A1A2E",
            secondary_color="#F5F5F7",
            accent_color="#0071E3",
            typography_style=TypographyStyle.MODERN_SANS,
            letter_spacing="tight",
            shadow_style=ShadowStyle.SOFT,
            background_style=BackgroundStyle.PURE_WHITE,
            shape_language=ShapeLanguage.MINIMAL,
            icon_style=IconStyle.LINE,
            badge_style=BadgeStyle.NONE,
            lighting_mood=LightingMood.HIGH_KEY,
            mood="sophisticated",
            energy="calm",
            formality="professional",
        ),
        prompt_modifier="""
[DESIGN STYLE: CLEAN & MINIMAL]

CORE PHILOSOPHY: Less is more. Every element must earn its place.

LAYOUT:
- Centered, symmetrical composition
- Generous whitespace (at least 40% of image should be breathing room)
- Product is the hero - nothing competes with it

COLOR PALETTE:
- Dominant: Pure white (#FFFFFF) or off-white (#F5F5F7)
- Text/Elements: Deep charcoal (#1A1A2E)
- Accent: Single brand color used sparingly
- Ratio: 70% white, 20% dark, 10% accent

TYPOGRAPHY:
- Modern sans-serif (think SF Pro, Helvetica Neue, Inter)
- Thin to regular weights only
- Generous letter-spacing
- Clean, readable hierarchy

ELEMENTS:
- Thin 1px lines if any dividers
- Soft, subtle shadows (blur: 20px, opacity: 10%)
- No decorative elements unless essential
- Icons: thin line style only

PHOTOGRAPHY:
- High-key lighting (bright, even)
- Minimal shadows
- Clean, pure product shots
- No busy backgrounds
"""
    ),

    "bold_vibrant": StylePreset(
        id="bold_vibrant",
        name="Bold & Vibrant",
        description="Eye-catching, energetic design with saturated colors. Great for fitness, kids, and fun products.",
        color_palette=["#FF4500", "#1A1A1A", "#FFD700", "#00CED1"],
        typography="Bold, chunky, impactful headlines",
        mood="Energetic, exciting, confident",
        lighting="Bright, high-key, dynamic with color gels",
        composition_style="Dynamic angles, asymmetrical, fills the frame",
        accent_elements="Bold shapes, color blocks, dynamic lines",
        design_framework=DesignFramework(
            layout_grid=LayoutGrid.ASYMMETRIC,
            balance="asymmetric",
            whitespace="minimal",
            color_harmony=ColorHarmony.COMPLEMENTARY,
            color_temperature=ColorTemperature.WARM,
            saturation=SaturationLevel.VIBRANT,
            primary_color="#FF4500",
            secondary_color="#1A1A1A",
            accent_color="#FFD700",
            typography_style=TypographyStyle.BOLD_DISPLAY,
            letter_spacing="tight",
            shadow_style=ShadowStyle.DRAMATIC,
            background_style=BackgroundStyle.COLOR_BLOCK,
            shape_language=ShapeLanguage.ANGULAR,
            icon_style=IconStyle.FILLED,
            badge_style=BadgeStyle.STARBURST,
            lighting_mood=LightingMood.DRAMATIC,
            mood="exciting",
            energy="energetic",
            formality="casual",
        ),
        prompt_modifier="""
[DESIGN STYLE: BOLD & VIBRANT]

CORE PHILOSOPHY: Stand out and demand attention. Energy and excitement.

LAYOUT:
- Dynamic, asymmetrical composition
- Elements can break the grid, overlap, angle
- Fill the frame - minimal dead space
- Create visual tension and movement

COLOR PALETTE:
- High saturation, fully saturated colors
- Bold complementary or triadic schemes
- Strong contrast between elements
- Don't be afraid of bright, punchy colors
- Example: Orange + Black + Gold

TYPOGRAPHY:
- Extra bold, heavy weights
- Condensed or extended display fonts
- Tight letter-spacing
- Can be angled, stacked, or broken
- Impact over elegance

ELEMENTS:
- Bold geometric shapes
- Color blocks and overlays
- Dynamic diagonal lines
- Strong drop shadows
- Starburst badges, action callouts

PHOTOGRAPHY:
- Dramatic lighting with strong shadows
- Can use colored lighting/gels
- Dynamic angles
- High contrast
- Action and movement feel
"""
    ),

    "luxury_premium": StylePreset(
        id="luxury_premium",
        name="Luxury Premium",
        description="Elegant, high-end aesthetic with rich colors and refined details. Ideal for beauty, jewelry, and premium goods.",
        color_palette=["#0D0D0D", "#F8F5F0", "#C9A962", "#2C2C2C"],
        typography="Elegant serifs, refined spacing, classic proportions",
        mood="Luxurious, exclusive, aspirational",
        lighting="Dramatic, moody, with highlights on key elements",
        composition_style="Refined, curated, intentional negative space",
        accent_elements="Gold foil effects, subtle textures, reflections",
        design_framework=DesignFramework(
            layout_grid=LayoutGrid.GOLDEN_RATIO,
            balance="symmetric",
            whitespace="generous",
            color_harmony=ColorHarmony.ANALOGOUS,
            color_temperature=ColorTemperature.NEUTRAL,
            saturation=SaturationLevel.MUTED,
            primary_color="#0D0D0D",
            secondary_color="#F8F5F0",
            accent_color="#C9A962",
            typography_style=TypographyStyle.ELEGANT_SERIF,
            letter_spacing="loose",
            shadow_style=ShadowStyle.DRAMATIC,
            background_style=BackgroundStyle.GRADIENT,
            shape_language=ShapeLanguage.MINIMAL,
            icon_style=IconStyle.NONE,
            badge_style=BadgeStyle.SUBTLE,
            lighting_mood=LightingMood.LOW_KEY,
            mood="luxurious",
            energy="calm",
            formality="formal",
        ),
        prompt_modifier="""
[DESIGN STYLE: LUXURY PREMIUM]

CORE PHILOSOPHY: Refined elegance. Every detail is intentional. Exclusivity.

LAYOUT:
- Golden ratio proportions
- Symmetric, balanced compositions
- Generous, intentional negative space
- Product presented like a precious object

COLOR PALETTE:
- Rich, deep colors: black, navy, burgundy
- Cream and warm whites (not pure white)
- Metallic accents: gold (#C9A962), rose gold, platinum
- Muted, sophisticated tones
- Ratio: 40% dark, 40% light, 20% metallic accent

TYPOGRAPHY:
- Elegant serif fonts (Didot, Bodoni, Playfair)
- Light to regular weights
- Generous letter-spacing (tracking)
- Classic, timeless proportions
- Can use all-caps for short headlines

ELEMENTS:
- Subtle gold foil or metallic effects
- Thin, elegant lines
- Minimal decorative elements
- If textures: marble, silk, leather hints
- Reflective surfaces, highlights

PHOTOGRAPHY:
- Low-key, dramatic lighting
- Rich shadows with luminous highlights
- Spotlight effect on product
- Reflective surfaces
- Studio quality, editorial feel
"""
    ),

    "natural_organic": StylePreset(
        id="natural_organic",
        name="Natural & Organic",
        description="Earthy, authentic aesthetic with natural textures. Perfect for health, food, and eco-friendly products.",
        color_palette=["#2D5016", "#F5F1E8", "#8B7355", "#A8C686"],
        typography="Friendly, rounded, organic shapes",
        mood="Warm, authentic, trustworthy, healthy",
        lighting="Natural, warm, soft sunlight feel",
        composition_style="Organic arrangements, natural groupings, lifestyle context",
        accent_elements="Natural textures, botanical elements, kraft paper, wood",
        design_framework=DesignFramework(
            layout_grid=LayoutGrid.RULE_OF_THIRDS,
            balance="asymmetric",
            whitespace="balanced",
            color_harmony=ColorHarmony.ANALOGOUS,
            color_temperature=ColorTemperature.WARM,
            saturation=SaturationLevel.MUTED,
            primary_color="#2D5016",
            secondary_color="#F5F1E8",
            accent_color="#8B7355",
            typography_style=TypographyStyle.FRIENDLY_ROUNDED,
            letter_spacing="normal",
            shadow_style=ShadowStyle.SOFT,
            background_style=BackgroundStyle.TEXTURE,
            texture_intensity="subtle",
            shape_language=ShapeLanguage.ORGANIC,
            icon_style=IconStyle.ILLUSTRATED,
            badge_style=BadgeStyle.TAG,
            lighting_mood=LightingMood.NATURAL,
            mood="authentic",
            energy="calm",
            formality="casual",
        ),
        prompt_modifier="""
[DESIGN STYLE: NATURAL & ORGANIC]

CORE PHILOSOPHY: Authentic, earthy, connected to nature. Warm and inviting.

LAYOUT:
- Rule of thirds composition
- Organic, natural arrangements
- Asymmetric but balanced
- Can include lifestyle context

COLOR PALETTE:
- Earth tones: sage green, terracotta, warm browns
- Cream and natural white (not bright white)
- Muted, desaturated colors
- Colors found in nature
- Example: Forest green + Cream + Brown

TYPOGRAPHY:
- Friendly, rounded sans-serifs
- Hand-drawn or organic feel welcome
- Warm, approachable weights
- Natural, easy letter-spacing

ELEMENTS:
- Natural textures: wood grain, linen, kraft paper
- Botanical accents: leaves, plants (subtle)
- Hand-illustrated icons
- Organic blob shapes
- Stamps, tags, natural badges

PHOTOGRAPHY:
- Natural, warm sunlight
- Golden hour feel
- Soft, welcoming shadows
- Can include natural props
- Authentic, not overly polished
"""
    ),
}


def get_style_preset(style_id: str) -> Optional[StylePreset]:
    """Get a style preset by ID"""
    return STYLE_PRESETS.get(style_id)


def get_all_styles() -> List[Dict]:
    """Get all style presets as list of dicts for API response"""
    return [
        {
            "id": style.id,
            "name": style.name,
            "description": style.description,
            "color_palette": style.color_palette,
            "mood": style.mood,
        }
        for style in STYLE_PRESETS.values()
    ]


def build_brand_context(
    brand_colors: Optional[List[str]] = None,
    brand_name: Optional[str] = None,
    has_logo: bool = False,
    image_type: str = "main",
) -> str:
    """
    Build brand context string for prompts.

    Args:
        brand_colors: List of brand hex colors
        brand_name: Brand name
        has_logo: Whether a logo image is provided
        image_type: Which image type this is for (main, infographic_1, etc.)

    Returns:
        Brand context prompt string
    """
    if not brand_colors and not brand_name and not has_logo:
        return ""

    parts = ["[BRAND IDENTITY]"]

    if brand_name:
        parts.append(f"- Brand: {brand_name}")

    if brand_colors:
        colors_str = ", ".join(brand_colors)
        parts.append(f"- Brand Colors: {colors_str}")
        parts.append("- Incorporate brand colors as accent colors throughout")
        parts.append("- Maintain color consistency across all images")

    # Logo integration - NOT on main/hero image
    if has_logo and image_type != "main":
        parts.append("")
        parts.append("[LOGO INTEGRATION - SECOND REFERENCE IMAGE]")
        parts.append("Two reference images are provided:")
        parts.append("  1. FIRST IMAGE: The product photo - this is what you're selling")
        parts.append("  2. SECOND IMAGE: The brand logo - integrate this creatively")
        parts.append("")
        parts.append("LOGO PLACEMENT GUIDELINES:")
        parts.append("- Position in a corner or as part of the design composition")
        parts.append("- Keep the ESSENCE and recognizability of the logo")
        parts.append("- You MAY stylize the logo to match the overall design aesthetic")
        parts.append("- Options: embossed effect, color-matched to palette, subtle watermark")
        parts.append("- Logo should feel INTEGRATED, not just placed on top")
        parts.append("- Size: prominent enough to notice, not so large it dominates")
        parts.append("- Never distort or stretch the logo")

    return "\n".join(parts)


def build_cohesion_reminder(style_id: str, image_type: str) -> str:
    """Build the cohesion reminder for consistent image sets"""
    style = get_style_preset(style_id)
    if not style:
        return ""

    return f"""
[COHESION REQUIREMENT - CRITICAL]
This is the {image_type.upper()} image in a 5-image Amazon listing set.
ALL images must share the same visual DNA:

MAINTAIN ACROSS ALL IMAGES:
- Same color palette: {', '.join(style.color_palette[:3])}
- Same typography style: {style.typography.split(',')[0]}
- Same lighting mood: {style.lighting.split(',')[0]}
- Same design language: {style.composition_style.split(',')[0]}

The customer should instantly recognize these images belong together.
"""
